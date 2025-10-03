class Controller:
    def __init__(self):
        self.paused = False
        self.cancelled = False

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def cancel(self):
        self.cancelled = True

    def should_continue(self):
        return not self.cancelled
