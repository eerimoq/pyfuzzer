import sys
import os
import argparse
import subprocess
import sysconfig
import shutil
import glob

from .version import __version__


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

MODULE_SRC = '''\
#include <Python.h>

extern PyMODINIT_FUNC PyInit_{module_name}(void);

PyMODINIT_FUNC pyfuzzer_module_init(void)
{{
    return (PyInit_{module_name}());
}}
'''


def mkdir_p(name):
    if not os.path.exists(name):
        os.makedirs(name)


def includes():
    include = sysconfig.get_path('include')

    return [f'-I{include}']


def ldflags():
    ldflags = sysconfig.get_config_var('LDFLAGS')
    ldversion = sysconfig.get_config_var('LDVERSION')
    ldflags += f' -lpython{ldversion}'

    return ldflags.split()


def run_command(command, env=None):
    print(' '.join(command))

    subprocess.check_call(command, env=env)


def generate(module_name, mutator):
    with open('module.c', 'w') as fout:
        fout.write(MODULE_SRC.format(module_name=module_name))

    if mutator is not None:
        shutil.copyfile(mutator, 'mutator.py')


def build(csources):
    command = ['clang']
    command += [
        '-fprofile-instr-generate',
        '-fcoverage-mapping',
        '-g',
        '-fsanitize=fuzzer',
        '-fsanitize=signed-integer-overflow',
        '-fno-sanitize-recover=all'
    ]
    command += includes()
    command += csources
    command += [
        'module.c',
        os.path.join(SCRIPT_DIR, 'pyfuzzer.c')
    ]
    command += ldflags()
    command += [
        '-o', 'pyfuzzer'
    ]

    run_command(command)


def build_print_corpus(csources):
    command = ['clang']
    command += includes()
    command += csources
    command += [
        'module.c',
        os.path.join(SCRIPT_DIR, 'pyfuzzer_print_corpus.c')
    ]
    command += ldflags()
    command += [
        '-o', 'pyfuzzer_print_corpus'
    ]

    run_command(command)


def run(maximum_execution_time):
    run_command(['rm', '-f', 'pyfuzzer.profraw'])
    mkdir_p('corpus')
    command = [
        './pyfuzzer',
        'corpus',
        f'-max_total_time={maximum_execution_time}',
        '-max_len=4096'
    ]
    env = os.environ.copy()
    env['LLVM_PROFILE_FILE'] = 'pyfuzzer.profraw'
    run_command(command, env=env)
    run_command([
        'llvm-profdata',
        'merge',
        '-sparse', 'pyfuzzer.profraw',
        '-o', 'pyfuzzer.profdata'
    ])
    run_command([
        'llvm-cov',
        'show',
        'pyfuzzer',
        '-instr-profile=pyfuzzer.profdata',
        '-ignore-filename-regex=/usr/|pyfuzzer.c|module.c'
    ])


def do_run(args):
    generate(args.modulename, args.mutator)
    build(args.csources)
    build_print_corpus(args.csources)
    run(args.maximum_execution_time)


def array_to_bytes(string):
    return bytes([
        int(byte[2:], 16)
        for byte in string.split(',')
        if byte
    ])


def do_print_corpus(_args):
    try:
        filenames = os.listdir('corpus')
    except:
        return

    paths = [
        os.path.join('corpus', filename)
        for filename in filenames
    ]

    for path in paths:
        subprocess.check_call(['./pyfuzzer_print_corpus', path])


def do_print_crashes(_args):
    for filename in glob.glob('crash-*'):
        subprocess.check_call(['./pyfuzzer_print_corpus', filename])


def do_clean(_args):
    shutil.rmtree('corpus', ignore_errors=True)

    for filename in glob.glob('crash-*'):
        os.remove(filename)


def main():
    parser = argparse.ArgumentParser(
        description='Use libFuzzer to fuzz test Python 3.6+ C extension modules.')

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')

    # Workaround to make the subparser required in Python 3.
    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='subcommand')
    subparsers.required = True

    # The run subparser.
    subparser = subparsers.add_parser(
        'run',
        description='Build and run the fuzz tester.')
    subparser.add_argument('-m', '--mutator', help='Mutator module.')
    subparser.add_argument(
        '-t', '--maximum-execution-time',
        type=int,
        default=1,
        help='Maximum execution time in seconds (default: %(default)s).')
    subparser.add_argument('modulename', help='C extension module name.')
    subparser.add_argument('csources', nargs='+', help='C extension source files.')
    subparser.set_defaults(func=do_run)

    # The print_corpus subparser.
    subparser = subparsers.add_parser(
        'print_corpus',
        description=('Print the corpus as Python functions with arguments and '
                     'return value or exception.'))
    subparser.set_defaults(func=do_print_corpus)

    # The print_crashes subparser.
    subparser = subparsers.add_parser('print_crashes',
                                      description='Print all crashes.')
    subparser.set_defaults(func=do_print_crashes)

    # The clean subparser.
    subparser = subparsers.add_parser(
        'clean',
        description='Remove the corpus and all crashes.')
    subparser.set_defaults(func=do_clean)

    args = parser.parse_args()

    if args.debug:
        args.func(args)
    else:
        try:
            args.func(args)
        except BaseException as e:
            sys.exit('error: ' + str(e))
