from communication import Observable
import multiprocessing


class ComputeProcess(multiprocessing.Process, Observable):

    def __inti__(self, target=None, args=(), kwargs={}):
        super(multiprocessing.Process, self).__init__(
            target=target, args=args, kwargs=kwargs)
        super(Observable, self).__init__()

    def run(self):
        result = self._target(*self._args, **self._kwargs)
        self.notify_observers(result=result)
