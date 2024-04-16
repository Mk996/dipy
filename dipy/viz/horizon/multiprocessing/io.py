import multiprocessing


class IOProcess(multiprocessing.Process):

    def __init__(
        self,
        group=None,
        target=None,
        daemon=False,
        name=None,
        queue=None,
        *args,
        **kwargs
    ):

        super().__init__(group, target, name, args, kwargs, daemon=daemon)

        def run(self):
            self._target()
