import os
import hashlib
from os import path
from pathlib import Path

project_root = Path(__file__) / '..' / '..'
additional_requirements_path = [
    '.pre-commit-config.yaml',
]

for dir, _, files in os.walk(path.join(project_root, 'requirements')):
    for file in files:
        file_path = path.normpath(path.join(dir, file))
        if file.endswith('.txt'):
            additional_requirements_path.append(file_path)

m = hashlib.md5()
for file in sorted(additional_requirements_path):
    with open(file, 'rb') as f:
        content = f.read()
        m.update(content)
print(m.hexdigest())
