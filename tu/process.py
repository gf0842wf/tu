# -*- coding: utf-8 -*-

import tornado.process
import tornado.ioloop

import time


class TorSubProcess(tornado.process.Subprocess):
    def __init__(self, callback, timeout=None, *args, **kwargs):
        """
        :param callback: 结果回调, params: (status, stdout, stderr, is_timeout)
        :param timeout: 超时
        :param args: subprocess command
        :return:
        """
        self.result_callback = callback

        self.timeout = timeout

        self.stdout_future = tornado.process.Subprocess.STREAM
        self.stderr_future = tornado.process.Subprocess.STREAM

        self.status_msg = None
        self.stdout_msg = None
        self.stderr_msg = None
        self.is_timeout = False

        super(TorSubProcess, self).__init__(stdout=self.stdout_future, stderr=self.stderr_future, *args, **kwargs)

        def stderr_cb(_stderr_msg):
            self.stderr_msg = _stderr_msg
            self.result_callback(self.status_msg, self.stdout_msg, self.stderr_msg, self.is_timeout)

        def stdout_cb(_stdout_msg):
            self.stdout_msg = _stdout_msg
            self.stderr.read_until_close(callback=stderr_cb)

        def exit_cb(_status_msg):
            self.status_msg = _status_msg
            self.stdout.read_until_close(callback=stdout_cb)

        if self.timeout is not None:
            self.io_loop.add_timeout(time.time() + self.timeout, self.on_timeout)

        self.set_exit_callback(exit_cb)

    def on_timeout(self):
        try:
            self.is_timeout = True
            self.cancel()
        except:
            pass

    def cancel(self):
        try:
            self.proc.kill()
        except:
            pass


if __name__ == '__main__':
    def cb(status, stdout, stderr, is_timeout):
        print status
        print stdout
        print stderr
        print is_timeout

    TorSubProcess(callback=cb, timeout=3, args=['ip', 'a'])

    ioloop = tornado.ioloop.IOLoop.current()
    ioloop.start()