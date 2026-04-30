from .base import BasePatcher

class DisnakePatcher(BasePatcher):
    def patch(self):
        # Disnake already supports FileInput natively
        return