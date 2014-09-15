from subprocess import STDOUT
from tornado.process import Subprocess
from time import sleep


class ExecutionException(Exception):
    def __init__(self, command, errno):
        self.command = command
        self.errno = errno
        super(ExecutionException, self).__init__(
            '%s exited with return code %d' % (command, errno))


def execute(cmd, cwd, out, project_id, build_id):
    from .. import server

    subproc = Subprocess(
        cmd,
        stdout=Subprocess.STREAM,
        stderr=STDOUT,
        cwd=cwd)

    def send(data):
        if data:
            out(data.decode('utf-8'))

    subproc.stdout.read_until_close(send, send)

    while subproc.proc.poll() is None:
        sleep(.1)
        if (project_id, build_id) in server.builder.stop_flags:
            subproc.proc.kill()
            server.builder.stop_flags.remove((project_id, build_id))

    if subproc.proc.returncode != 0:
        raise ExecutionException(''.join(cmd), subproc.proc.returncode)
