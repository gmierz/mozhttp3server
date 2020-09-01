from mozhttp3server.throttling.throttler import Throttler
from mozhttp3server.throttling.netimpair import NetemInstance


OPTIONS = {
    "loss_ratio": 0,
    "loss_corr": 0,
    "dup_ratio": 0,
    "delay": 0,
    "jitter": 0,
    "delay_jitter_corr": 0,
    "reorder_ratio": 0,
    "reorder_corr": 0,
}


class LinuxThrottler(Throttler):
    def initialize(self):
        self.netem = NetemInstance(self.nic, self.inbound, self.include, self.exclude)
        return {}

    def teardown(self):
        self.netem.stop_netem()
        self.netem.teardown()
        self.status = {"throttling": False}
        return self.status

    def shape(self, options):
        if self.status["throttling"]:
            try:
                self.teardown()
            except Exception:
                pass
        self.netem.initialize()
        status = dict(OPTIONS)
        for key in status:
            if key in options:
                status[key] = options[key]
        self.netem.netem(**status)
        status["throttling"] = True
        self.status = status
        return self.status
