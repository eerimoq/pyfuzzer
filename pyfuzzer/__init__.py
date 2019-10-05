import sys
import os
import argparse
import subprocess
import sysconfig

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


def run_pkg_config(option):
    command = ['pkg-config', option, 'python3']

    try:
        return run_command_stdout(command)
    except Exception:
        return ''


def default_cflags():
    include = sysconfig.get_path('include')

    return [f'-I{include}']


def default_ldflags():
    ldflags = sysconfig.get_config_var('LDFLAGS')
    ldversion = sysconfig.get_config_var('LDVERSION')
    ldflags += f' -lpython{ldversion}'

    return ldflags.split()


def run_command(command, env=None):
    print(' '.join(command))

    subprocess.check_call(command, env=env)


def run_command_stdout(command):
    print(' '.join(command))

    return subprocess.check_output(command).decode('ascii').strip()


def generate(module_name):
    with open('module.c', 'w') as fout:
        fout.write(MODULE_SRC.format(module_name=module_name))


def build(module_name, csource):
    command = ['clang']
    command += [
        '-fprofile-instr-generate',
        '-fcoverage-mapping',
        '-g',
        '-fsanitize=fuzzer',
        '-fsanitize=signed-integer-overflow',
        '-fno-sanitize-recover=all'
    ]
    command += default_cflags()
    command += [
        csource,
        'module.c',
        os.path.join(SCRIPT_DIR, 'pyfuzzer.c')
    ]
    command += default_ldflags()
    command += [
        '-o', module_name
    ]

    run_command(command)


def run(name, maximum_execution_time):
    run_command(['rm', '-f', f'{name}.profraw'])
    command = [
        f'./{name}',
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
        '-ignore-filename-regex=/usr/include|pyfuzzer.c|module.c'
    ])


def do(args):
    module_name = os.path.splitext(os.path.basename(args.csource))[0]
    generate(module_name)
    build(module_name, args.csource)
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
