import logging

from os import path as ospath, environ
from subprocess import run as srun
from requests import get as rget
from dotenv import load_dotenv
import pkg_resources
from subprocess import call

if ospath.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()],
                    level=logging.INFO)

# update everything
packages = [dist.project_name for dist in pkg_resources.working_set]
call("pip install --upgrade " + ' '.join(packages), shell=True)

CONFIG_FILE_URL = environ.get('CONFIG_FILE_URL', None)
try:
    if len(CONFIG_FILE_URL) == 0:
        raise TypeError
    try:
        res = rget(CONFIG_FILE_URL)
        if res.status_code == 200:
            with open('config.env', 'wb+') as f:
                f.write(res.content)
                f.close()
        else:
            logging.error(f"Failed to download config.env {res.status_code}")
    except Exception as e:
        logging.error(f"CONFIG_FILE_URL: {e}")
except TypeError:
    pass

load_dotenv('config.env', override=True)

UPSTREAM_REPO = environ.get('UPSTREAM_REPO', None)
try:
    if len(UPSTREAM_REPO) == 0:
       raise TypeError
except TypeError:
    UPSTREAM_REPO = None

if UPSTREAM_REPO is not None:
    if ospath.exists('.git'):
        srun(["rm", "-rf", ".git"])

    srun([f"git init -q \
                      && git config --global user.email anonym@ous.com \
                      && git config --global user.name asdf \
                      && git add . \
                      && git commit -sm update -q \
                      && git remote add origin {UPSTREAM_REPO} \
                      && git fetch origin -q \
                      && git reset --hard origin/master -q"], shell=True)

