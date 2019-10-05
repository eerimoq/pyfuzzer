import sys
import os
import argparse
import subprocess

from .version import __version__


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


def generate(module_name):
    with open('module.c', 'w') as fout:
        fout.write(MODULE_SRC.format(module_name=module_name))

        
def build(module_name, csource):
    cflags = [
        '-fprofile-instr-generate',
        '-fcoverage-mapping',
        '-I/usr/include/python3.7m',
        '-g',
        '-fsanitize=fuzzer',
        '-fsanitize=signed-integer-overflow',
        '-fno-sanitize-recover=all'
    ]
    sources = [
        csource,
        'module.c',
        '../../pyfuzzer/pyfuzzer.c'
    ]
    command = ['clang']
    command += cflags
    command += sources
    command += [
        '-lpython3.7m',
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
    build(module_name, args.csource)
    run(module_name)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')
    parser.add_argument('-m', '--mutator', help='Mutator module.')
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
