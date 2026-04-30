class BasePatcher:
    def __init__(self, bot, fingerprint, handlers):
        self.bot = bot
        self.fingerprint = fingerprint
        self.handlers = handlers

    def patch(self):
        raise NotImplementedError("Patchers must implement patch()")