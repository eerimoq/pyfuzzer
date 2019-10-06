import sys
import os
import argparse
import subprocess
import sysconfig
import shutil

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


def build(module_name, csources):
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
        '-o', module_name
    ]

    run_command(command)


def run(name, maximum_execution_time):
    run_command(['rm', '-f', f'{name}.profraw'])
    mkdir_p('corpus')
    command = [
        f'./{name}',
        'corpus',
        f'-max_total_time={maximum_execution_time}',
        '-max_len=4096'
    ]
    env = os.environ.copy()
    env['LLVM_PROFILE_FILE'] = f'{name}.profraw'
    run_command(command, env=env)
    run_command([
        'llvm-profdata',
        'merge',
        '-sparse', f'{name}.profraw',
        '-o', f'{name}.profdata'
    ])
    run_command([
        'llvm-cov',
        'show',
        name,
        f'-instr-profile={name}.profdata',
        '-ignore-filename-regex=/usr/|pyfuzzer.c|module.c'
    ])


def do(args):
    module_name = args.modulename
    generate(module_name, args.mutator)
    build(module_name, args.csources)
    run(module_name, args.maximum_execution_time)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')
    parser.add_argument('-m', '--mutator', help='Mutator module.')
    parser.add_argument(
        '-t', '--maximum-execution-time',
        type=int,
        default=1,
        help='Maximum execution time in seconds (default: %(default)s).')
    parser.add_argument('modulename', help='C extension module name.')
    parser.add_argument('csources', nargs='+', help='C extension source files.')

    args = parser.parse_args()

    if args.debug:
        do(args)
    else:
        try:
            do(args)
        except BaseException as e:
            sys.exit('error: ' + str(e))
