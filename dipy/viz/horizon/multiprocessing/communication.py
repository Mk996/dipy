from abc import abstractmethod


class Observer:

    def __init__(self, observable=None):
        self._observable = observable

    def subscribe(self, observable=None):
        if observable:
            self._observable = observable
        self._observable.subscribe(self)

    @abstractmethod
    def notify(
            self,
            observable,
            *args,
            **kwargs
    ):
        pass


class Observable:

    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        for obs in self._observers:
            obs.notify(self, *args, **kwargs)

    def unsubscribe(self, observer):
        self._observers.remove(observer)
