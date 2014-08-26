from tornado.concurrent import Future
from subprocess import STDOUT
from tornado.process import Subprocess


def execute(cmd, cwd, out):
    future = Future()

    subproc = Subprocess(
        cmd,
        stdout=Subprocess.STREAM,
        stderr=STDOUT,
        cwd=cwd)

    def send(data):
        if data:
            out(data.decode('utf-8'))

    def callback(rv):
        future.set_result(rv)

    subproc.stdout.read_until_close(send, send)
    subproc.set_exit_callback(callback)
    return future
