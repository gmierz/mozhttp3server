import logging


class Throttler:
    def __init__(self, nic, inbound=False, include=None, exclude=None, logger=None):
        self.inbound = inbound
        self.include = include
        self.exclude = exclude
        self.nic = nic
        if logger is None:
            logger = logging.getLogger("webnetem")
        self.logger = logger
        self._status = {"throttling": False}
        self._test_started = False

    @property
    def status(self):
        self._status["test_running"] = self._test_started
        return self._status

    def initialize(self):
        pass

    def start_test(self, force=False):
        if self._test_started and not force:
            raise Exception("Already started")
        self._test_started = True
        return self.status

    def stop_test(self):
        self._test_started = False
        return self.status
