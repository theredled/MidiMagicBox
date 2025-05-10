from datetime import datetime
import sched
import threading
import asyncio

class ClickSequence:
    def __init__(self, nb_clicks_required = 2):
        self.count = 0
        self.start_time = None
        self.last_click_time = None
        self.callback = None
        self.nb_clicks_required = nb_clicks_required

    def set_callback(self, callback):
        self.callback = callback

    def reset(self):
        self.count = 0
        self.start_time = None
        self.last_click_time = None

    def start(self):
        self.count = 1
        self.start_time = datetime.now()
        self.last_click_time = self.start_time

    def notify_click(self):
        if self.start_time is None:
            self.start()
            return
        this_click_time = datetime.now()
        delta_time = (this_click_time - self.last_click_time)

        self.count += 1
        if delta_time.total_seconds() > 0.5:
            self.reset()
            self.start()
        elif self.nb_clicks_required <= self.count:
            self.callback()
            self.reset()
        else:
            self.last_click_time = this_click_time




