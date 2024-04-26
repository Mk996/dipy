import multiprocessing

from dipy.viz.horizon.multiprocessing.communication import Observable


class ComputeProcess(multiprocessing.Process, Observable):

    def __init__(self, target=None, name=None, args=(), kwargs={}):
        self.result = None
        Observable.__init__(self)
        multiprocessing.Process.__init__(
            self, target=target, name=name, args=args, kwargs=kwargs)

    def run(self):
        result = self._target(self._args, self._kwargs)
        self.notify_observers(result=result)
