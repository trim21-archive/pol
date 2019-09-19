import os
import sys

import toml


def _poetry_lock_to_requirements_txt(start_dir):
    with open(f'{start_dir}/poetry.lock') as f:
        lock = toml.load(f)

    requirements = {
        package['name']: package['version'] + ' # ' +
        package.get('marker', '') if 'marker' in package else package['version']
        for package in lock['package']
        if package.get('category') == 'main' and not package.get('optional')
    }
    requirements = sorted(requirements.items(), key=lambda x: x[0])

    with open(f'{start_dir}/requirements.txt', 'w') as f:
        f.writelines(f'{name}=={version} \n' for name, version in sorted(requirements))


if __name__ == '__main__':
    workdir = os.getcwd()
    if len(sys.argv) > 1:
        workdir = sys.argv[1]
    _poetry_lock_to_requirements_txt(workdir)
