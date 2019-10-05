import sys
import os
import argparse
import subprocess

from .version import __version__


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

MODULE_SRC = '''\
#include <Python.h>

extern PyMODINIT_FUNC PyInit_hello_world(void);

PyMODINIT_FUNC pyfuzzer_module_init(void)
{{
    return (PyInit_{module_name}());
}}
'''


def run_command(command, env=None):
    print(' '.join(command))

    subprocess.check_call(command, env=env)


def run_command_stdout(command):
    print(' '.join(command))

    return subprocess.check_output(command).decode('ascii')


def generate(module_name):
    with open('module.c', 'w') as fout:
        fout.write(MODULE_SRC.format(module_name=module_name))


def build(module_name, python, csource):
    cflags = [
        '-fprofile-instr-generate',
        '-fcoverage-mapping',
        '-g',
        '-fsanitize=fuzzer',
        '-fsanitize=signed-integer-overflow',
        '-fno-sanitize-recover=all'
    ]
    cflags += run_command_stdout([f'{python}-config', '--includes']).split()
    sources = [
        csource,
        'module.c',
        os.path.join(SCRIPT_DIR, 'pyfuzzer.c')
    ]
    command = ['clang']
    command += cflags
    command += sources
    command += run_command_stdout([f'{python}-config', '--ldflags']).split()
    command += run_command_stdout([f'{python}-config', '--libs']).split()
    command += [
        '-o', module_name
    ]

    run_command(command)


def run(name):
    run_command(['rm', '-f', f'{name}.profraw'])
    run_command([f'./{name}', '-max_total_time=5', '-max_len=4096'],
                   env={
                       'LLVM_PROFILE_FILE': f'{name}.profraw'
                   })
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
        f'-instr-profile={name}.profdata'
    ])


def do(args):
    module_name = os.path.splitext(os.path.basename(args.csource))[0]
    generate(module_name)
    build(module_name, args.python, args.csource)
    run(module_name)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')
    parser.add_argument('-m', '--mutator', help='Mutator module.')
    parser.add_argument('-p', '--python',
                        default='python3',
                        help='Python executable (default: %(default)s).')
    parser.add_argument(
        'csource',
        help=('C extension source file. The name of the module must be the '
              'same as the file name without suffix.'))

    args = parser.parse_args()

    if args.debug:
        do(args)
    else:
        try:
            do(args)
        except BaseException as e:
            sys.exit('error: ' + str(e))
