"""Shared plumbing for the casino's persistent "play again" buttons.

A Components V2 button keeps working after a restart only when its custom id
carries everything the click needs.  These helpers let both casino cogs replay a
round through the exact same flow the command uses, instead of duplicating it.
"""


class InteractionContext:
    """Minimal ``commands.Context`` stand-in for a replay started by a button.

    The casino flows only touch ``author``/``guild``/``channel`` and ``send``.
    The interaction is always deferred before a replay starts, so everything the
    replayed round sends goes through its followup.
    """

    def __init__(self, interaction):
        self.interaction = interaction
        self.bot = interaction.client
        self.author = interaction.user
        self.guild = interaction.guild
        self.channel = interaction.channel
        self.message = interaction.message

    async def send(self, *args, **kwargs):
        return await self.interaction.followup.send(*args, **kwargs)
