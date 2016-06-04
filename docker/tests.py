import os
import subprocess

import sys
from colorclass import Color

__dir__ = os.path.dirname(os.path.abspath(__file__))


def execute(cmds, output=False, exit=False):
    output = None if output else subprocess.PIPE
    p = subprocess.Popen(cmds, stdout=output, stderr=output)
    p.wait()
    if p.returncode != 0:
        print(Color('{red}ERROR!{/red}'))
        if output is not None:
            print('STDOUT: {}'.format(p.stdout.read().decode('utf-8')))
            print('STDERR: {}'.format(p.stderr.read().decode('utf-8')))
        raise (SystemExit if exit else ChildProcessError)


def test_image(name, image_output=False, container_output=False, exit=False):
    print_ = print if image_output or container_output else sys.stdout.write
    print_(Color('{yellow}TESTING:{/yellow} {magenta}{}{/magenta}... ').format(name))
    directory = os.path.join(__dir__, name)
    image_name = name.lower()
    execute(['docker', 'build', '-t', image_name, directory], image_output, exit)
    execute(['docker', 'run', '--rm', image_name], container_output, exit)
    print(Color('{green}SUCCESS{/green}'))


def test_all(image_output=False, container_output=False):
    results = []
    for dirname in os.listdir(__dir__):
        if not os.path.isdir(dirname):
            continue
        try:
            test_image(dirname, image_output=image_output, container_output=container_output)
        except ChildProcessError:
            results.append(False)
        else:
            results.append(True)
    print('-' * 60)
    print('PASSED: {} {}/{}'.format(
        ''.join([{False: Color.red('F'), True: Color.green('.')}[x] for x in results]),
        len(list(filter(lambda x: x, results))), len(results)
    ))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Test images.')
    parser.add_argument('image', nargs='?')
    parser.add_argument('--image-output', action='store_true')
    parser.add_argument('--container-output', action='store_true')
    args = parser.parse_args()
    if args.image:
        test_image(args.image, args.image_output, args.container_output, True)
    else:
        test_all(args.image_output, args.container_output)
