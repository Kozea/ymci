from ymci import config
from subprocess import Popen
import os


def get_log_file(id, idx):
    path = config['ymci']['projects_path']
    project_dir = os.path.join(path, id)
    return os.path.join(project_dir, 'build_%d.log' % idx)


def build(id, idx):
    project = config['projects'][id]
    path = config['ymci']['projects_path']
    project_dir = os.path.join(path, id)
    if not os.path.exists(project_dir):
        os.mkdir(project_dir)
    build_dir = os.path.join(project_dir, 'build_%d' % idx)
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    log = open(get_log_file(id, idx), 'w')
    log.write('Starting build %d...\n' % idx)

    Popen(
        ['/bin/bash', '-x', '-c', project['build_script']],
        executable='/bin/bash',
        stdout=log,
        stderr=log,
        cwd=build_dir)
