import os
from subprocess import STDOUT
from tornado.process import Subprocess
from time import sleep
from signal import SIGKILL
from logging import getLogger
log = getLogger('ymci')


class ExecutionException(Exception):
    def __init__(self, command, errno):
        self.command = command
        self.errno = errno
        super(ExecutionException, self).__init__(
            '%s exited with return code %d' % (command, errno))


def execute(cmd, cwd, out, project_id, build_id):
    from .. import server

    log.debug('Forking subprocess [%s]' % cmd)
    subproc = Subprocess(
        cmd,
        stdout=Subprocess.STREAM,
        stderr=STDOUT,
        start_new_session=True,
        cwd=cwd)

    def end(data):
        if data == b'':
            log.debug('Got end')
            end.happened = True
        else:
            log.warn('Got WTF on ending: %s' % data)

    def send(data):
        out(data.decode('utf-8'))

    end.happened = False
    log.debug('Read until close [%s]' % cmd)
    subproc.stdout.read_until_close(end, send)

    log.debug('Polling [%s]' % cmd)
    while subproc.proc.poll() is None:
        sleep(.01)
        if (project_id, build_id) in server.builder.stop_flags:
            log.debug('Stopping [%s]' % cmd)
            os.killpg(subproc.proc.pid, SIGKILL)
            server.builder.stop_flags.remove((project_id, build_id))

    log.debug('Waiting for stream end [%s]' % cmd)
    while not end.happened:
        sleep(.01)

    log.debug('Ended with rv %d [%s]' % (subproc.proc.returncode, cmd))
    if subproc.proc.returncode != 0:
        raise ExecutionException(''.join(cmd), subproc.proc.returncode)
