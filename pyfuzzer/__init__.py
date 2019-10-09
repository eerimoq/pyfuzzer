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


def format_cflags(cflags):
    return [f'-{cflag}' for cflag in cflags if cflag]


def build(csources, cflags):
    command = ['clang']
    command += [
        '-fprofile-instr-generate',
        '-fcoverage-mapping',
        '-g',
        '-fsanitize=fuzzer'
    ]

    if cflags:
        command += format_cflags(cflags)
    else:
        command += [
            '-fsanitize=undefined',
            '-fsanitize=signed-integer-overflow',
            '-fsanitize=alignment',
            '-fsanitize=bool',
            '-fsanitize=builtin',
            '-fsanitize=bounds',
            '-fsanitize=enum',
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


def build_print(csources, cflags):
    command = ['clang']
    command += format_cflags(cflags)
    command += includes()
    command += csources
    command += [
        'module.c',
        os.path.join(SCRIPT_DIR, 'pyfuzzer_print.c')
    ]
    command += ldflags()
    command += [
        '-o', 'pyfuzzer_print'
    ]

    run_command(command)


def run(libfuzzer_arguments):
    run_command(['rm', '-f', 'pyfuzzer.profraw'])
    mkdir_p('corpus')
    command = [
        './pyfuzzer',
        'corpus',
        '-print_final_stats=1'
    ]
    command += [f'-{a}' for a in libfuzzer_arguments]
    env = os.environ.copy()
    env['LLVM_PROFILE_FILE'] = 'pyfuzzer.profraw'
    run_command(command, env=env)


def print_coverage():
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
    build(args.csources, args.cflag)
    build_print(args.csources, args.cflag)
    run(args.libfuzzer_argument)


def do_print_corpus(args):
    if args.units:
        filenames = args.units
    else:
        filenames = glob.glob('corpus/*')

    paths = '\n'.join(filenames)

    subprocess.run(['./pyfuzzer_print'], input=paths.encode('utf-8'), check=True)


def do_print_crashes(args):
    if args.units:
        filenames = args.units
    else:
        filenames = glob.glob('crash-*')

    for filename in filenames:
        proc = subprocess.run(['./pyfuzzer_print'], input=filename.encode('utf-8'))
        print()

        try:
            proc.check_returncode()
        except Exception as e:
            print(e)


def do_print_coverage(_args):
    print_coverage()


def do_clean(_args):
    shutil.rmtree('corpus', ignore_errors=True)

    for filename in glob.glob('crash-*'):
        os.remove(filename)

    for filename in glob.glob('oom-*'):
        os.remove(filename)

    for filename in glob.glob('slow-unit-*'):
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
        '-l', '--libfuzzer-argument',
        action='append',
        default=[],
        help="Add a libFuzzer command line argument without its leading '-'.")
    subparser.add_argument(
        '-c', '--cflag',
        action='append',
        default=[],
        help=("Add a C extension compilation flag without its leading '-'. If "
              "given, all default sanitizers are removed."))
    subparser.add_argument('modulename', help='C extension module name.')
    subparser.add_argument('csources', nargs='+', help='C extension source files.')
    subparser.set_defaults(func=do_run)

    # The print_coverage subparser.
    subparser = subparsers.add_parser('print_coverage',
                                      description='Print code coverage.')
    subparser.set_defaults(func=do_print_coverage)

    # The print_corpus subparser.
    subparser = subparsers.add_parser(
        'print_corpus',
        description=('Print corpus units as Python functions with arguments and '
                     'return value or exception.'))
    subparser.add_argument('units',
                           nargs='*',
                           help='Units to print, or whole corpus if none given.')
    subparser.set_defaults(func=do_print_corpus)

    # The print_crashes subparser.
    subparser = subparsers.add_parser('print_crashes',
                                      description='Print all crashes.')
    subparser.add_argument('units',
                           nargs='*',
                           help='Crashes to print, or all if none given.')
    subparser.set_defaults(func=do_print_crashes)

    # The clean subparser.
    subparser = subparsers.add_parser(
        'clean',
        description='Remove the corpus and all crashes to start over.')
    subparser.set_defaults(func=do_clean)

    args = parser.parse_args()

    if args.debug:
        args.func(args)
    else:
        try:
            args.func(args)
        except BaseException as e:
            sys.exit('error: ' + str(e))
