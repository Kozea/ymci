from subprocess import STDOUT
from tornado.process import Subprocess
from time import sleep


class ExecutionException(Exception):
    def __init__(self, command, errno):
        self.command = command
        self.errno = errno
        super(ExecutionException, self).__init__(
            '%s exited with return code %d' % (command, errno))


def execute(cmd, cwd, out):
    from .. import builder

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
        if builder.current_task.stop:
            subproc.proc.kill()
    if subproc.proc.returncode != 0:
        raise ExecutionException(''.join(cmd), subproc.proc.returncode)
