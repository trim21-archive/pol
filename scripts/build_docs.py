import sys
import json
import subprocess

from app.core import config
from app.fast import app

with open(
    config.PROJ_ROOT / 'docs' / 'source' / 'openapi.json',
    'w+',
    encoding='utf-8',
) as f:
    json.dump(app.openapi(), f)

retcode = subprocess.call(
    ['make', 'html'],
    stdout=sys.stdout,
    stderr=sys.stderr,
    cwd=str(config.PROJ_ROOT / 'docs'),
)

exit(retcode)
