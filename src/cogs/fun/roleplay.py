"""
Roleplay cog — anime reaction GIFs from the nekos.best API.

Every action fetches a random SFW GIF from ``https://nekos.best/api/v2/<action>``
and renders it in a CV2 layout message:

    ### <emoji> <action>
    ─────────────────
    <desc>            (author did X to target)
    <gif>
    [💖 Hug back]     ← ActionRow at the bottom of the container

Right-clicking a user exposes a **single** ``Roleplay`` user context command:
Discord caps global user commands at 15 per app, so one menu per action would
blow the quota. The menu opens an *ephemeral* CV2 container with a select menu
of every action; picking one posts that action's card in the channel (the
ephemeral picker then disappears).

The "do it back" button:

  * is only usable by the **target** user,
  * **persists across restarts** — click handling is a cog listener that
    resolves per-message state from the ``roleplay_actions`` table (no view
    store to lose), so old messages keep working after a redeploy,
  * **disables itself after first use** by rebuilding the original layout
    (same title/desc/GIF) with the button set to ``disabled=True``, and
  * sends a **new** roleplay message without a button as the "back" action.

``rpblock`` / ``rpunblock`` manage a per-user block list: blocking someone
refuses every roleplay path that targets you — prefix commands, the context-
menu action picker, and "do it back" buttons (the ``roleplay_blocks`` table,
resolved by (blocker, blocked) pairs).

The API is fully SFW and has no "kill" category, so the legacy hug/kill/kiss
set was replaced by the expanded action list below (each maps 1:1 to a
nekos.best category). Every request sends the required application
User-Agent header ``Niko (https://niko.sryze.cc)``.
"""

import random

import aiohttp
import discord
from discord.ext import commands

from utils import logging as log
from utils.i18n import get_lang, make_msg


# ─────────────────────────────────────────────────────────────────────────────
#  ACTION REGISTRY (order = prefix-command/select-option order)
# ─────────────────────────────────────────────────────────────────────────────

# meta fields per action:
#   emoji   — used in the title and the button label
#   playful — adds the shared "all in good fun" footer
#   label   — "do it back" button text per language (personality-neutral)
#   desc    — roleplay sentence variants per language
#             (picked at random per message so cards don't repeat)
#   help    — English help text for the prefix command
ACTIONS: dict = {
    "hug": {
        "emoji": "💖",
        "playful": False,
        "help": "Give someone a hug! 💖",
        "label": {"en": "Hug back", "de": "Umarm zurück", "es": "Abrazo de vuelta"},
        "desc": {
                "en": [
                    "{author} hugged {target}! :hugging:",
                    "{author} pulled {target} into a big hug! 🤗",
                    "{author} wrapped {target} up in a warm hug! 💖",
                    "{author} gave {target} the coziest hug ever! 🫂",
                    "{author} squeezed {target} tight! 🫂",
                    "{author} glomped {target} with a flying hug! 💨",
                    "{author} wrapped their arms around {target}! 💞",
                    "{author} hugged {target} and refused to let go! 💖",
                    "{author} gave {target} a surprise hug from behind! 😮",
                    "{author} bear-hugged {target}! 🐻",
                    "{author} hugged {target} so hard they almost tipped over! 🫣",
                    "{author} snuck in and hugged {target}! 🤫",
                    "{author} offered {target} a hug and made their whole day! ☺️",
                    "{author} wrapped {target} in a blanket and hugged them! 🧣",
                    "{author} gave {target} a hug worth a thousand words! 💬",
                    "{author} spun {target} around in a hug! 🌀",
                    "{author} hugged {target} until all their worries melted away! 🫠",
                    "{author} rested their head on {target}'s shoulder mid-hug! 🥰",
                    "{author} ran across the room just to hug {target}! 🏃",
                    "{author} hugged {target} — maximum comfort achieved! 💯",
                ],
                "de": [
                    "{author} hat {target} umarmt! :hugging:",
                    "{author} hat {target} in eine dicke Umarmung gezogen! 🤗",
                    "{author} hat {target} ganz warm umarmt! 💖",
                    "{author} hat {target} die kuscheligste Umarmung aller Zeiten gegeben! 🫂",
                    "{author} hat {target} ganz fest gedrückt! 🫂",
                    "{author} ist {target} mit einer fliegenden Umarmung entgegengesprungen! 💨",
                    "{author} hat die Arme um {target} gelegt! 💞",
                    "{author} hat {target} umarmt und wollte gar nicht mehr loslassen! 💖",
                    "{author} hat {target} von hinten eine Überraschungsumarmung gegeben! 😮",
                    "{author} hat {target} eine Bärenumarmung verpasst! 🐻",
                    "{author} hat {target} so fest umarmt, dass sie fast umgekippt wären! 🫣",
                    "{author} hat sich geschlichen und {target} umarmt! 🤫",
                    "{author} hat {target} eine Umarmung angeboten und ihren Tag gerettet! ☺️",
                    "{author} hat {target} in eine Decke gewickelt und umarmt! 🧣",
                    "{author} hat {target} eine Umarmung gegeben, die mehr als tausend Worte wert ist! 💬",
                    "{author} hat {target} in einer Umarmung herumgedreht! 🌀",
                    "{author} hat {target} so lange umarmt, bis sich alle Sorgen verflüchtigt haben! 🫠",
                    "{author} hat bei der Umarmung den Kopf an {target}s Schulter gelegt! 🥰",
                    "{author} ist quer durch den Raum gerannt, nur um {target} zu umarmen! 🏃",
                    "{author} hat {target} umarmt — maximale Geborgenheit erreicht! 💯",
                ],
                "es": [
                    "¡{author} abrazó a {target}! :hugging:",
                    "¡{author} metió a {target} en un abrazo enorme! 🤗",
                    "¡{author} envolvió a {target} en un abrazo bien calentito! 💖",
                    "¡{author} le dio a {target} el abrazo más acogedor de todos! 🫂",
                    "¡{author} apretó a {target} con todas sus fuerzas! 🫂",
                    "¡{author} se lanzó hacia {target} en plan abrazo volador! 💨",
                    "¡{author} rodeó a {target} con sus brazos! 💞",
                    "¡{author} abrazó a {target} y no pensaba soltar! 💖",
                    "¡{author} le dio a {target} un abrazo sorpresa por detrás! 😮",
                    "¡{author} le metió a {target} un abrazo de oso! 🐻",
                    "¡{author} abrazó a {target} tan fuerte que casi se desequilibran! 🫣",
                    "¡{author} se acercó sigiloso y abrazó a {target}! 🤫",
                    "¡{author} le ofreció un abrazo a {target} y le arregló el día! ☺️",
                    "¡{author} envolvió a {target} en una manta y lo abrazó! 🧣",
                    "¡{author} le dio a {target} un abrazo que vale más que mil palabras! 💬",
                    "¡{author} giró a {target} en pleno abrazo! 🌀",
                    "¡{author} abrazó a {target} hasta que se le derritieron todas las preocupaciones! 🫠",
                    "¡{author} apoyó la cabeza en el hombro de {target} para abrazarle! 🥰",
                    "¡{author} cruzó la sala corriendo solo para abrazar a {target}! 🏃",
                    "¡{author} abrazó a {target} — confort máximo conseguido! 💯",
                ],
            },
        },
    },
    "kiss": {
        "emoji": "💋",
        "playful": False,
        "help": "Give someone a kiss! 💋",
        "label": {"en": "Kiss back", "de": "Küss zurück", "es": "Beso de vuelta"},
        "desc": {
                "en": [
                    "{author} kissed {target}! 💋",
                    "{author} planted a quick kiss on {target}! 😚",
                    "{author} blew a kiss at {target}! 😘",
                    "{author} kissed {target} on the cheek! 💕",
                    "{author} gave {target} a tiny peck on the forehead! 🥺",
                    "{author} snuck in a kiss while {target} wasn't looking! 🤭",
                    "{author} kissed {target} and left them speechless! 😳",
                    "{author} covered {target}'s face in kisses! 💋",
                    "{author} gave {target} a gentle goodnight kiss! 🌙",
                    "{author} kissed {target} mid-sentence! 😮",
                    "{author} left a kiss on {target}'s forehead! ✨",
                    "{author} kissed {target} and skipped away! 💃",
                    "{author} stole a kiss from {target}! 🫢",
                    "{author} kissed {target} so softly it felt like a butterfly! 🦋",
                    "{author} gave {target} a million-dollar kiss! 💰",
                    "{author} kissed {target} and the whole room went aww! 😍",
                    "{author} peppered {target} with kisses! 😚",
                    "{author} kissed {target} like in the movies! 🎬",
                    "{author} spun {target} around and kissed their cheek! 🌀",
                    "{author} kissed {target} — hearts everywhere! 💞",
                ],
                "de": [
                    "{author} hat {target} geküsst! 💋",
                    "{author} hat {target} einen schnellen Kuss gedrückt! 😚",
                    "{author} hat {target} einen Kuss zugeflogen! 😘",
                    "{author} hat {target} auf die Wange geküsst! 💕",
                    "{author} hat {target} ein winziges Küsschen auf die Stirn gegeben! 🥺",
                    "{author} hat {target} geküsst, während sie nicht hingesehen haben! 🤭",
                    "{author} hat {target} geküsst und sprachlos zurückgelassen! 😳",
                    "{author} hat {target}s Gesicht komplett mit Küssen bedeckt! 💋",
                    "{author} hat {target} einen sanften Gute-Nacht-Kuss gegeben! 🌙",
                    "{author} hat {target} mitten im Satz geküsst! 😮",
                    "{author} hat einen Kuss auf {target}s Stirn hinterlassen! ✨",
                    "{author} hat {target} geküsst und ist hüpfend weitergetänzelt! 💃",
                    "{author} hat {target} einen Kuss gestohlen! 🫢",
                    "{author} hat {target} so sanft geküsst wie ein Schmetterling! 🦋",
                    "{author} hat {target} einen Million-Dollar-Kuss gegeben! 💰",
                    "{author} hat {target} geküsst und der ganze Raum hat 'aww' gemacht! 😍",
                    "{author} hat {target} mit Küssen überschüttet! 😚",
                    "{author} hat {target} geküsst wie im Film! 🎬",
                    "{author} hat {target} herumgedreht und auf die Wange geküsst! 🌀",
                    "{author} hat {target} geküsst — Herzen überall! 💞",
                ],
                "es": [
                    "¡{author} besó a {target}! 💋",
                    "¡{author} le plantó un beso rápido a {target}! 😚",
                    "¡{author} le lanzó un beso a {target}! 😘",
                    "¡{author} besó a {target} en la mejilla! 💕",
                    "¡{author} le dio a {target} un besito en la frente! 🥺",
                    "¡{author} coló un beso a {target} cuando no miraba! 🤭",
                    "¡{author} besó a {target} y le dejó sin palabras! 😳",
                    "¡{author} cubrió de besos la cara de {target}! 💋",
                    "¡{author} le dio a {target} un dulce beso de buenas noches! 🌙",
                    "¡{author} besó a {target} en plena frase! 😮",
                    "¡{author} dejó un beso en la frente de {target}! ✨",
                    "¡{author} besó a {target} y se fue saltando! 💃",
                    "¡{author} robó un beso a {target}! 🫢",
                    "¡{author} besó a {target} tan suave como una mariposa! 🦋",
                    "¡{author} le dio a {target} un beso de un millón de dólares! 💰",
                    "¡{author} besó a {target} y todo el mundo dijo aww! 😍",
                    "¡{author} llovió besos sobre {target}! 😚",
                    "¡{author} besó a {target} como en el cine! 🎬",
                    "¡{author} giró a {target} y le besó la mejilla! 🌀",
                    "¡{author} besó a {target} — corazones por todas partes! 💞",
                ],
            },
        },
    },
    "cuddle": {
        "emoji": "🤗",
        "playful": False,
        "help": "Cuddle with someone! 🤗",
        "label": {"en": "Cuddle back", "de": "Kuschel zurück", "es": "Acurruca de vuelta"},
        "desc": {
                "en": [
                    "{author} cuddled {target}! 🤗",
                    "{author} snuggled up next to {target}! 🥰",
                    "{author} pulled {target} into a cuddle pile! 🫂",
                    "{author} wrapped {target} in a blanket and cuddled them! 🧣",
                    "{author} cuddled {target} on the couch! 🛋️",
                    "{author} nuzzled into {target}'s shoulder! 😌",
                    "{author} gave {target} the coziest cuddle session! ✨",
                    "{author} hugged {target} close and refused to move! 🤗",
                    "{author} curled up against {target} like a cat! 🐱",
                    "{author} cuddled {target} until they both dozed off! 💤",
                    "{author} wrapped around {target} like a koala! 🐨",
                    "{author} gave {target} warm cuddles and good vibes! ☺️",
                    "{author} leaned their head on {target} for a soft cuddle! 🥺",
                    "{author} stole all the blankets while cuddling {target}! 😂",
                    "{author} cuddled {target} through the whole movie! 🍿",
                    "{author} held {target} in the gentlest cuddle! 💞",
                    "{author} squished {target} in a bear cuddle! 🐻",
                    "{author} cuddled {target} like it was the last day on earth! 🌍",
                    "{author} melted into a cuddle with {target}! 🫠",
                    "{author} gave {target} cuddles until all the sadness was gone! 💖",
                ],
                "de": [
                    "{author} hat {target} gekuschelt! 🤗",
                    "{author} hat sich neben {target} geschmiegt! 🥰",
                    "{author} hat {target} in einen kuschel-haufen gezogen! 🫂",
                    "{author} hat {target} in eine decke gewickelt und gekuschelt! 🧣",
                    "{author} hat mit {target} auf dem sofa gekuschelt! 🛋️",
                    "{author} hat sich in {target}s schulter gekuschelt! 😌",
                    "{author} hat {target} die gemütlichste kuscheleinheit aller zeiten gegeben! ✨",
                    "{author} hat {target} fest an sich gedrückt und wollte sich nicht rühren! 🤗",
                    "{author} hat sich wie eine katze an {target} gekuschelt! 🐱",
                    "{author} hat mit {target} gekuschelt, bis beide eingeschlafen sind! 💤",
                    "{author} hat sich wie ein koala um {target} gewickelt! 🐨",
                    "{author} hat {target} warme kuschelstunden und gute laune geschenkt! ☺️",
                    "{author} hat den kopf an {target} gelegt für eine sanfte kuscheleinheit! 🥺",
                    "{author} hat beim kuscheln mit {target} alle decken gestohlen! 😂",
                    "{author} hat {target} durch den ganzen film hindurch gekuschelt! 🍿",
                    "{author} hat {target} in die sanfteste umarmung genommen! 💞",
                    "{author} hat {target} in eine bären-kuschelrunde gequetscht! 🐻",
                    "{author} hat {target} gekuschelt, als wäre es der letzte tag auf erden! 🌍",
                    "{author} ist beim kuscheln mit {target} regelrecht dahingegossen! 🫠",
                    "{author} hat {target} gekuschelt, bis alle traurigkeit verschwunden war! 💖",
                ],
                "es": [
                    "¡{author} acurrucó a {target}! 🤗",
                    "¡{author} se arrimó a {target} para acurrucarse! 🥰",
                    "¡{author} metió a {target} en un montón de mimos! 🫂",
                    "¡{author} envolvió a {target} en una manta y le dio mimos! 🧣",
                    "¡{author} se acurrucó con {target} en el sofá! 🛋️",
                    "¡{author} se restregó en el hombro de {target}! 😌",
                    "¡{author} le dio a {target} la sesión de mimos más acogedora! ✨",
                    "¡{author} abrazó a {target} con fuerza y no pensaba moverse! 🤗",
                    "¡{author} se acurrucó contra {target} como un gatito! 🐱",
                    "¡{author} se acurrucó con {target} hasta que los dos se quedaron dormidos! 💤",
                    "¡{author} se enroscó en {target} como un koala! 🐨",
                    "¡{author} le dio a {target} mimos calentitos y buenas vibras! ☺️",
                    "¡{author} apoyó la cabeza en {target} para un mimo suavecito! 🥺",
                    "¡{author} robó todas las mantas mientras acurrucaba a {target}! 😂",
                    "¡{author} acurrucó a {target} durante toda la película! 🍿",
                    "¡{author} sostuvo a {target} en el mimo más tierno! 💞",
                    "¡{author} apretó a {target} en un mimo de oso! 🐻",
                    "¡{author} acurrucó a {target} como si fuera el último día en la tierra! 🌍",
                    "¡{author} se derritió en un mimo con {target}! 🫠",
                    "¡{author} le dio mimos a {target} hasta que se fue toda la tristeza! 💖",
                ],
            },
        },
    },
    "pat": {
        "emoji": "🫳",
        "playful": False,
        "help": "Give someone headpats! 🫳",
        "label": {"en": "Pat back", "de": "Pat zurück", "es": "Pat de vuelta"},
        "desc": {
                "en": [
                    "{author} gave {target} headpats! ✨",
                    "{author} gently patted {target}'s head! 🫳",
                    "{author} ruffled {target}'s hair! 😄",
                    "{author} gave {target} headpats until they purred! 😽",
                    "{author} patted {target} like the good bean they are! 🫘",
                    "{author} showered {target} in headpats! 🚿",
                    "{author} gave {target} a proud double headpat! 👏",
                    "{author} smoothed {target}'s hair back with a soft pat! 😌",
                    "{author} patted {target}'s head — achievement unlocked! 🏆",
                    "{author} gave {target} headpats of approval! 👍",
                    "{author} patted {target} until they melted! 🫠",
                    "{author} gave {target} a gentle headpat and a smile! ☺️",
                    "{author} patted {target}'s head like the precious cinnamon roll they are! 🥮",
                    "{author} gave {target} bonus headpats for being awesome! ⭐",
                    "{author} patted {target} with utmost care! 💕",
                    "{author} delivered the fluffiest headpats to {target}! ☁️",
                    "{author} gave {target} a headpat combo — pat pat pat! 🥊",
                    "{author} patted {target} and whispered 'well done'! 🤫",
                    "{author} gave {target} ceremonial headpats of the highest order! 🎖️",
                    "{author} patted {target}'s head and fixed their whole mood! 💯",
                ],
                "de": [
                    "{author} hat {target} den kopf gestreichelt! ✨",
                    "{author} hat {target} sanft über den kopf gestrichelt! 🫳",
                    "{author} hat {target} durch die haare gewühlt! 😄",
                    "{author} hat {target} so lange gestreichelt, bis sie geschnurrt haben! 😽",
                    "{author} hat {target} gestreichelt wie das brave bohnchen, das sie sind! 🫘",
                    "{author} hat {target} mit kopfstreichel-attacken überhäuft! 🚿",
                    "{author} hat {target} einen stolzen doppel-kopfpatscher verpasst! 👏",
                    "{author} hat {target}s haare mit einer sanften berührung geglättet! 😌",
                    "{author} hat {target} den kopf gestreichelt — erfolg freigeschaltet! 🏆",
                    "{author} hat {target} zustimmende kopfstreichel gegeben! 👍",
                    "{author} hat {target} gestreichelt, bis sie dahingeschmolzen sind! 🫠",
                    "{author} hat {target} einen sanften kopfpatscher und ein lächeln geschenkt! ☺️",
                    "{author} hat {target} gestreichelt wie das kostbare zimtschnecken-wesen, das sie sind! 🥮",
                    "{author} hat {target} bonus-kopfstreichel verpasst, weil sie so toll sind! ⭐",
                    "{author} hat {target} mit größter sorgfalt gestreichelt! 💕",
                    "{author} hat {target} die fluffigsten kopfstreichel geliefert! ☁️",
                    "{author} hat {target} eine kopfpatscher-kombi verpasst — pat pat pat! 🥊",
                    "{author} hat {target} gestreichelt und 'gut gemacht' geflüstert! 🤫",
                    "{author} hat {target} feierliche kopfstreichel höchster ordnung verliehen! 🎖️",
                    "{author} hat {target} den kopf gestreichelt und die ganze laune repariert! 💯",
                ],
                "es": [
                    "¡{author} dio palmaditas a {target}! ✨",
                    "¡{author} acarició la cabeza de {target} con cariño! 🫳",
                    "¡{author} despeinó a {target}! 😄",
                    "¡{author} acarició a {target} hasta que ronroneó! 😽",
                    "¡{author} acarició a {target} como al buen frijolito que es! 🫘",
                    "¡{author} llovió palmaditas sobre {target}! 🚿",
                    "¡{author} le dio a {target} una doble palmadita de orgullo! 👏",
                    "¡{author} alisó el pelo de {target} con una palmadita suave! 😌",
                    "¡{author} acarició la cabeza de {target} — logro desbloqueado! 🏆",
                    "¡{author} le dio a {target} palmaditas de aprobación! 👍",
                    "¡{author} acarició a {target} hasta derretirle! 🫠",
                    "¡{author} le dio a {target} una palmadita suave y una sonrisa! ☺️",
                    "¡{author} acarició a {target} como al precioso rollito de canela que es! 🥮",
                    "¡{author} le dio a {target} palmaditas extra por ser tan genial! ⭐",
                    "¡{author} acarició a {target} con mucho cuidado! 💕",
                    "¡{author} le dio a {target} las palmaditas más esponjositas! ☁️",
                    "¡{author} le metió a {target} una combinación de palmaditas — ¡pat pat pat! 🥊",
                    "¡{author} acarició a {target} y susurró 'bien hecho'! 🤫",
                    "¡{author} le concedió a {target} palmaditas ceremoniales de alto nivel! 🎖️",
                    "¡{author} acarició la cabeza de {target} y le arregló el humor entero! 💯",
                ],
            },
        },
    },
    "poke": {
        "emoji": "🫵",
        "playful": False,
        "help": "Poke someone! 🫵",
        "label": {"en": "Poke back", "de": "Stups zurück", "es": "Poke de vuelta"},
        "desc": {
                "en": [
                    "{author} poked {target}! 🫵",
                    "{author} poked {target} and ran away! 🏃",
                    "{author} poked {target}'s cheek! 😝",
                    "{author} poked {target} repeatedly until they reacted! 😤",
                    "{author} sneakily poked {target}'s side! 🤭",
                    "{author} poked {target} — boop! 👆",
                    "{author} poked {target} right in the ticklish spot! 😆",
                    "{author} poked {target} three times for good luck! 🍀",
                    "{author} poked {target} and immediately looked innocent! 😇",
                    "{author} poked {target} with maximum mischief! 😈",
                    "{author} poked {target}'s arm and giggled! 🤭",
                    "{author} poked {target} to get their attention! 🫵",
                    "{author} poked {target} — poke war initiated! ⚔️",
                    "{author} poked {target} and demanded a response! 📣",
                    "{author} gently poked {target} just to say hi! 👋",
                    "{author} poked {target} and hid behind their screen! 🫥",
                    "{author} poked {target} in the ribs! 😂",
                    "{author} poked {target} until they finally looked up! 👀",
                    "{author} poked {target} — that's a challenge now! 🎯",
                    "{author} poked {target} and declared victory! 🏆",
                ],
                "de": [
                    "{author} hat {target} angestupst! 🫵",
                    "{author} hat {target} angestupst und bin weggerannt! 🏃",
                    "{author} hat {target} in die wange gestupst! 😝",
                    "{author} hat {target} so lange gestupst, bis sie reagiert haben! 😤",
                    "{author} hat {target} heimlich in die seite gestupst! 🤭",
                    "{author} hat {target} gestupst — boop! 👆",
                    "{author} hat {target} genau in die kitzelstelle gestupst! 😆",
                    "{author} hat {target} dreimal gestupst, für glück! 🍀",
                    "{author} hat {target} gestupst und sofort unschuldig geguckt! 😇",
                    "{author} hat {target} mit maximaler schelmerei gestupst! 😈",
                    "{author} hat {target} in den arm gestupst und gekichert! 🤭",
                    "{author} hat {target} gestupst, um ihre aufmerksamkeit zu kriegen! 🫵",
                    "{author} hat {target} gestupst — stups-krieg gestartet! ⚔️",
                    "{author} hat {target} gestupst und eine antwort gefordert! 📣",
                    "{author} hat {target} sanft gestupst, nur um hallo zu sagen! 👋",
                    "{author} hat {target} gestupst und sich hinter dem bildschirm versteckt! 🫥",
                    "{author} hat {target} in die rippen gestupst! 😂",
                    "{author} hat {target} gestupst, bis sie endlich hochgeschaut haben! 👀",
                    "{author} hat {target} gestupst — das ist jetzt eine herausforderung! 🎯",
                    "{author} hat {target} gestupst und den sieg erklärt! 🏆",
                ],
                "es": [
                    "¡{author} le picó a {target}! 🫵",
                    "¡{author} le picó a {target} y salió corriendo! 🏃",
                    "¡{author} le pellizcó la mejilla a {target}! 😝",
                    "¡{author} le picó a {target} una y otra vez hasta que reaccionó! 😤",
                    "¡{author} coló un pellizco en el costado de {target}! 🤭",
                    "¡{author} le picó a {target} — boop! 👆",
                    "¡{author} le picó a {target} justo en el punto de cosquillas! 😆",
                    "¡{author} le picó a {target} tres veces para buena suerte! 🍀",
                    "¡{author} le picó a {target} y puso cara de inocente! 😇",
                    "¡{author} le picó a {target} con travesura máxima! 😈",
                    "¡{author} le picó el brazo a {target} y se rio! 🤭",
                    "¡{author} le picó a {target} para llamar su atención! 🫵",
                    "¡{author} le picó a {target} — ¡guerra de pellizcos iniciada! ⚔️",
                    "¡{author} le picó a {target} y exigió respuesta! 📣",
                    "¡{author} le picó a {target} suavecito solo para saludar! 👋",
                    "¡{author} le picó a {target} y se escondió detrás de la pantalla! 🫥",
                    "¡{author} le metió un pellizco en las costillas a {target}! 😂",
                    "¡{author} le picó a {target} hasta que por fin levantó la vista! 👀",
                    "¡{author} le picó a {target} — ¡esto ya es un desafío! 🎯",
                    "¡{author} le picó a {target} y declaró la victoria! 🏆",
                ],
            },
        },
    },
    "tickle": {
        "emoji": "🤭",
        "playful": False,
        "help": "Tickle someone! 🤭",
        "label": {"en": "Tickle back", "de": "Kitzel zurück", "es": "Cosquillas de vuelta"},
        "desc": {
                "en": [
                    "{author} tickled {target}! 😆",
                    "{author} tickled {target} until they cried laughing! 🤣",
                    "{author} snuck up and tickled {target}'s sides! 🤭",
                    "{author} tickled {target} — mercy was not granted! 😈",
                    "{author} tickled {target} into a giggle fit! 😂",
                    "{author} wiggled their fingers at {target} threateningly! 🫰",
                    "{author} tickled {target} while they begged for mercy! 🥺",
                    "{author} tickled {target} until they snorted! 🐽",
                    "{author} ambushed {target} with surprise tickles! 💥",
                    "{author} tickled {target} and dodged the revenge attempt! 🥊",
                    "{author} tickled {target} until they fell off the couch! 🛋️",
                    "{author} gave {target} the tickle treatment! ✋",
                    "{author} tickled {target} — the giggling won't stop for hours! 😆",
                    "{author} tickled {target}'s tummy like a mischievous gremlin! 👹",
                    "{author} tickled {target} and got tickled back instantly! ⚔️",
                    "{author} tickled {target} until they rolled away! 🌀",
                    "{author} tickled {target} — cute aggression fully unleashed! 🥰",
                    "{author} tickled {target} during their dramatic speech! 🎭",
                    "{author} tickled {target} with expert precision! 🎯",
                    "{author} tickled {target} and recorded it for evidence! 📸",
                ],
                "de": [
                    "{author} hat {target} gekitzelt! 😆",
                    "{author} hat {target} zum lachtränchen gekitzelt! 🤣",
                    "{author} hat sich geschlichen und {target} in die seiten gekitzelt! 🤭",
                    "{author} hat {target} gekitzelt — gnade wurde nicht gewährt! 😈",
                    "{author} hat {target} in einen kicheranfall gekitzelt! 😂",
                    "{author} hat {target} mit wackelnden fingern bedroht! 🫰",
                    "{author} hat {target} gekitzelt, während sie um gnade gefleht haben! 🥺",
                    "{author} hat {target} zum schnauben gekitzelt! 🐽",
                    "{author} hat {target} mit überraschungskitzel-attacken überfallen! 💥",
                    "{author} hat {target} gekitzelt und dem racheversuch ausgewichen! 🥊",
                    "{author} hat {target} vom sofa gekitzelt! 🛋️",
                    "{author} hat {target} die kitzel-behandlung verpasst! ✋",
                    "{author} hat {target} gekitzelt — das gekichel hält noch stunden an! 😆",
                    "{author} hat {target} wie ein frecher gremlin auf den bauch gekitzelt! 👹",
                    "{author} hat {target} gekitzelt und wurde sofort zurückgekitzelt! ⚔️",
                    "{author} hat {target} weggerollt vor lachen beim kitzeln! 🌀",
                    "{author} hat {target} gekitzelt — knuddel-aggression voll entfesselt! 🥰",
                    "{author} hat {target} mitten in der dramatischen rede gekitzelt! 🎭",
                    "{author} hat {target} mit exakter präzision gekitzelt! 🎯",
                    "{author} hat {target} gekitzelt und als beweis aufgezeichnet! 📸",
                ],
                "es": [
                    "¡{author} le hizo cosquillas a {target}! 😆",
                    "¡{author} le hizo cosquillas a {target} hasta hacerle llorar de risa! 🤣",
                    "¡{author} se acercó sigiloso y le metió cosquillas en los costados a {target}! 🤭",
                    "¡{author} le hizo cosquillas a {target} — ¡la piedad no fue concedida! 😈",
                    "¡{author} provocó un ataque de risa a {target} con cosquillas! 😂",
                    "¡{author} amenazó a {target} moviendo los dedos! 🫰",
                    "¡{author} le hizo cosquillas a {target} mientras rogaba clemencia! 🥺",
                    "¡{author} le hizo cosquillas a {target} hasta hacerle resoplar! 🐽",
                    "¡{author} emboscó a {target} con cosquillas sorpresa! 💥",
                    "¡{author} le hizo cosquillas a {target} y esquivó la venganza! 🥊",
                    "¡{author} le hizo cosquillas a {target} hasta tirarle del sofá! 🛋️",
                    "¡{author} le aplicó a {target} el tratamiento de cosquillas! ✋",
                    "¡{author} le hizo cosquillas a {target} — la risa no parará en horas! 😆",
                    "¡{author} le hizo cosquillas en la barriga a {target} como un gremlin travieso! 👹",
                    "¡{author} le hizo cosquillas a {target} y recibió venganza al instante! ⚔️",
                    "¡{author} le hizo cosquillas a {target} hasta que rodó fuera! 🌀",
                    "¡{author} le hizo cosquillas a {target} — agresión adorable al máximo! 🥰",
                    "¡{author} le hizo cosquillas a {target} en pleno discurso dramático! 🎭",
                    "¡{author} le hizo cosquillas a {target} con precisión de experto! 🎯",
                    "¡{author} le hizo cosquillas a {target} y lo grabó como evidencia! 📸",
                ],
            },
        },
    },
    "highfive": {
        "emoji": "🙌",
        "playful": False,
        "help": "High-five someone! 🙌",
        "label": {"en": "High five back", "de": "High five zurück", "es": "Choca esos cinco"},
        "desc": {
                "en": [
                    "{author} high-fived {target}! 🙌",
                    "{author} gave {target} an earth-shattering high five! 💥",
                    "{author} high-fived {target} so hard it echoed! 📢",
                    "{author} ran up and high-fived {target}! 🏃",
                    "{author} high-fived {target} — perfect contact, zero whiff! 🎯",
                    "{author} gave {target} a slow-motion high five! 🎬",
                    "{author} high-fived {target} with both hands! 🙌",
                    "{author} high-fived {target} and struck a victory pose! 🏆",
                    "{author} attempted a high five and {target} left them hanging… then delivered! 😅",
                    "{author} high-fived {target} into next week! 📅",
                    "{author} gave {target} the legendary double-spin high five! 🌀",
                    "{author} high-fived {target} mid-jump! 🦘",
                    "{author} high-fived {target} like champions! 🥇",
                    "{author} high-fived {target} and the crowd went wild! 🎉",
                    "{author} sneakily high-fived {target} from behind! 🤭",
                    "{author} high-fived {target} after their brilliant idea! 💡",
                    "{author} high-fived {target} with the force of a thousand suns! ☀️",
                    "{author} gave {target} a gentle, wholesome high five! ☺️",
                    "{author} high-fived {target} and did a little dance! 💃",
                    "{author} high-fived {target} — friendship level increased! 💯",
                ],
                "de": [
                    "{author} hat {target} ein High Five gegeben! 🙌",
                    "{author} hat {target} ein erdbeschleunigendes High Five gegeben! 💥",
                    "{author} hat {target} so fest ein High Five gegeben, dass es widerhallte! 📢",
                    "{author} ist herangerannt und hat {target} ein High Five gegeben! 🏃",
                    "{author} hat {target} ein High Five gegeben — perfekter kontakt, kein fehlschlag! 🎯",
                    "{author} hat {target} ein high-five in zeitlupe gegeben! 🎬",
                    "{author} hat {target} mit beiden händen ein High Five gegeben! 🙌",
                    "{author} hat {target} ein High Five gegeben und eine siegespose eingenommen! 🏆",
                    "{author} wollte ein High Five und {target} ließ sie hängen… dann kam es doch! 😅",
                    "{author} hat {target} bis in die nächste woche ein High Five gegeben! 📅",
                    "{author} hat {target} das legendäre doppel-dreh-high-five gegeben! 🌀",
                    "{author} hat {target} mitten im sprung ein High Five gegeben! 🦘",
                    "{author} hat {target} wie echte championen ein High Five gegeben! 🥇",
                    "{author} hat {target} ein High Five gegeben und die menge tobte! 🎉",
                    "{author} hat {target} von hinten heimlich ein High Five gegeben! 🤭",
                    "{author} hat {target} nach ihrer genialen idee ein High Five gegeben! 💡",
                    "{author} hat {target} mit der kraft von tausend sonnen ein High Five gegeben! ☀️",
                    "{author} hat {target} ein sanftes, herzliches High Five gegeben! ☺️",
                    "{author} hat {target} ein High Five gegeben und einen kleinen tanz gemacht! 💃",
                    "{author} hat {target} ein High Five gegeben — freundschaftsstufe gestiegen! 💯",
                ],
                "es": [
                    "¡{author} chocó esos cinco con {target}! 🙌",
                    "¡{author} le dio a {target} un choque de cinco que partió la tierra! 💥",
                    "¡{author} chocó esos cinco con {target} tan fuerte que sonó el eco! 📢",
                    "¡{author} corrió y chocó esos cinco con {target}! 🏃",
                    "¡{author} chocó esos cinco con {target} — contacto perfecto, cero fallo! 🎯",
                    "¡{author} le dio a {target} un choque de cinco en cámara lenta! 🎬",
                    "¡{author} chocó esos cinco con {target} con las dos manos! 🙌",
                    "¡{author} chocó esos cinco con {target} y posó como campeón! 🏆",
                    "{author} quiso chocar los cinco y {target} los dejó colgados… ¡pero al final llegaron! 😅",
                    "¡{author} chocó esos cinco con {target} hasta la semana que viene! 📅",
                    "¡{author} le dio a {target} el legendario choque de cinco con doble giro! 🌀",
                    "¡{author} chocó esos cinco con {target} en pleno salto! 🦘",
                    "¡{author} chocó esos cinco con {target} como puros campeones! 🥇",
                    "¡{author} chocó esos cinco con {target} y el público enloqueció! 🎉",
                    "¡{author} coló un choque de cinco a {target} desde atrás! 🤭",
                    "¡{author} chocó esos cinco con {target} por su idea brillante! 💡",
                    "¡{author} chocó esos cinco con {target} con la fuerza de mil soles! ☀️",
                    "¡{author} le dio a {target} un choque de cinco suave y sano! ☺️",
                    "¡{author} chocó esos cinco con {target} y bailó un poquito! 💃",
                    "¡{author} chocó esos cinco con {target} — ¡nivel de amistad aumentado! 💯",
                ],
            },
        },
    },
    "slap": {
        "emoji": "✋",
        "playful": True,
        "help": "Playfully slap someone! ✋",
        "label": {"en": "Slap back", "de": "Schlag zurück", "es": "Cachetada de vuelta"},
        "desc": {
                "en": [
                    "{author} slapped {target}! ✋",
                    "{author} playfully slapped {target}! 😜",
                    "{author} slapped {target} with a wet noodle! 🍜",
                    "{author} slapped {target} — slap heard round the world! 🌍",
                    "{author} slapped {target} and ran! 🏃",
                    "{author} slapped {target} with a feather-light touch! 🪶",
                    "{author} slapped {target} for their terrible pun! 😂",
                    "{author} slapped {target} — it echoed for days! 📢",
                    "{author} slapped {target} with a fish! 🐟",
                    "{author} slapped {target} and looked very proud! 😌",
                    "{author} slapped {target} in slow motion! 🎬",
                    "{author} slapped {target} with a pillow! 🛏️",
                    "{author} slapped {target} and immediately apologized with cookies! 🍪",
                    "{author} slapped {target} — the audacity was real! 😤",
                    "{author} slapped {target} with a pool noodle! 🏊",
                    "{author} slapped {target} twice for good measure! ✌️",
                    "{author} slapped {target} and called it friendship! 🤝",
                    "{author} slapped {target} with dramatic flair! 🎭",
                    "{author} slapped {target} — lightly, out of love! 💖",
                    "{author} slapped {target} and the whole chat gasped! 😱",
                ],
                "de": [
                    "{author} hat {target} eine geknallt! ✋",
                    "{author} hat {target} spielerisch eine geklebt! 😜",
                    "{author} hat {target} mit einer nassen nudel geschlagen! 🍜",
                    "{author} hat {target} eine geknallt — der schlag war rund um die welt zu hören! 🌍",
                    "{author} hat {target} eine geknallt und bin gerannt! 🏃",
                    "{author} hat {target} federleicht geknallt! 🪶",
                    "{author} hat {target} für den schlimmen witz eine geknallt! 😂",
                    "{author} hat {target} eine geknallt — das echo hielt tage an! 📢",
                    "{author} hat {target} mit einem fisch geschlagen! 🐟",
                    "{author} hat {target} eine geknallt und sah sehr stolz aus! 😌",
                    "{author} hat {target} in zeitlupe eine geknallt! 🎬",
                    "{author} hat {target} mit einem kissen geschlagen! 🛏️",
                    "{author} hat {target} eine geknallt und sich sofort mit kekzen entschuldigt! 🍪",
                    "{author} hat {target} eine geknallt — die frechheit war real! 😤",
                    "{author} hat {target} mit einem pool-noodle geschlagen! 🏊",
                    "{author} hat {target} zur sicherheit zweimal geknallt! ✌️",
                    "{author} hat {target} eine geknallt und es freundschaft genannt! 🤝",
                    "{author} hat {target} mit dramatischem flair eine geknallt! 🎭",
                    "{author} hat {target} eine geknallt — ganz leicht, aus liebe! 💖",
                    "{author} hat {target} eine geknallt und der ganze chat hat laut geklatscht! 😱",
                ],
                "es": [
                    "¡{author} abofeteó a {target}! ✋",
                    "¡{author} le dio a {target} una bofetada en plan broma! 😜",
                    "¡{author} bofeteó a {target} con un fideo mojado! 🍜",
                    "¡{author} abofeteó a {target} — se oyó en todo el planeta! 🌍",
                    "¡{author} abofeteó a {target} y salió corriendo! 🏃",
                    "¡{author} bofeteó a {target} con un tacto ligerito como pluma! 🪶",
                    "¡{author} abofeteó a {target} por su chiste horrible! 😂",
                    "¡{author} abofeteó a {target} — el eco duró días! 📢",
                    "¡{author} bofeteó a {target} con un pescado! 🐟",
                    "¡{author} abofeteó a {target} y quedó muy satisfecho! 😌",
                    "¡{author} abofeteó a {target} en cámara lenta! 🎬",
                    "¡{author} bofeteó a {target} con una almohada! 🛏️",
                    "¡{author} abofeteó a {target} y pidió perdón con galletas al instante! 🍪",
                    "¡{author} abofeteó a {target} — la frescura era real! 😤",
                    "¡{author} bofeteó a {target} con un flotador de piscina! 🏊",
                    "¡{author} abofeteó a {target} dos veces para asegurarse! ✌️",
                    "¡{author} abofeteó a {target} y lo llamó amistad! 🤝",
                    "¡{author} abofeteó a {target} con mucho dramatismo! 🎭",
                    "¡{author} abofeteó a {target} — suavecito, con cariño! 💖",
                    "¡{author} abofeteó a {target} y todo el chat se quedó boquiabierto! 😱",
                ],
            },
        },
    },
    "bonk": {
        "emoji": "🔨",
        "playful": True,
        "help": "Bonk someone! 🔨",
        "label": {"en": "Bonk back", "de": "Bonk zurück", "es": "Bonk de vuelta"},
        "desc": {
                "en": [
                    "{author} bonked {target}! 🔨",
                    "{author} bonked {target} back to the shadow realm! 👻",
                    "{author} bonked {target} for being too horny! 🙅",
                    "{author} bonked {target} with the bonk hammer of justice! ⚖️",
                    "{author} bonked {target} — no thoughts, head empty! 🫥",
                    "{author} bonked {target} into next Tuesday! 📅",
                    "{author} bonked {target} gently, for their own good! 😌",
                    "{author} bonked {target} for their crimes against puns! 😂",
                    "{author} bonked {target} and sent them to the bonk dimension! 🌀",
                    "{author} bonked {target} with maximum horniness-jail energy! 🔒",
                    "{author} bonked {target} and yelled 'BONK'! 📢",
                    "{author} bonked {target} so they'd think better thoughts! 💭",
                    "{author} bonked {target} — the bonk was deserved! 👍",
                    "{author} bonked {target} with a squeaky toy hammer! 🐽",
                    "{author} bonked {target} and instantly bonked themselves too! 🔄",
                    "{author} bonked {target} for waking up the whole server! 😴",
                    "{author} bonked {target} right on the head, cartoon-style! 🎨",
                    "{author} bonked {target} and their brain buffered! 💻",
                    "{author} bonked {target} — straight to horny jail, do not pass go! 🚔",
                    "{author} bonked {target} with love and bonk energy! 💖",
                ],
                "de": [
                    "{author} hat {target} gebonkt! 🔨",
                    "{author} hat {target} zurück in das schattenreich gebonkt! 👻",
                    "{author} hat {target} gebonkt, weil sie zu versaut waren! 🙅",
                    "{author} hat {target} mit dem bonk-hammer der gerechtigkeit gebonkt! ⚖️",
                    "{author} hat {target} gebonkt — keine gedanken, kopf leer! 🫥",
                    "{author} hat {target} bis in den nächsten dienstag gebonkt! 📅",
                    "{author} hat {target} sanft gebonkt, zu ihrem eigenen bestem! 😌",
                    "{author} hat {target} für ihre verbrechen gegen die witze gebonkt! 😂",
                    "{author} hat {target} in die bonk-dimension gebonkt! 🌀",
                    "{author} hat {target} mit maximaler kuschelhaft-energie gebonkt! 🔒",
                    "{author} hat {target} gebonkt und 'BONK' geschrien! 📢",
                    "{author} hat {target} gebonkt, damit sie bessere gedanken denken! 💭",
                    "{author} hat {target} gebonkt — der bonk war verdient! 👍",
                    "{author} hat {target} mit einem quietsch-hammer gebonkt! 🐽",
                    "{author} hat {target} gebonkt und sich selbst sofort auch gebonkt! 🔄",
                    "{author} hat {target} gebonkt, weil sie den ganzen server geweckt haben! 😴",
                    "{author} hat {target} wie im cartoon direkt auf den kopf gebonkt! 🎨",
                    "{author} hat {target} gebonkt und ihr gehirn hat gepuffert! 💻",
                    "{author} hat {target} gebonkt — direkt in die kuschelhaft, ohne vorbeigehen! 🚔",
                    "{author} hat {target} mit liebe und bonk-energie gebonkt! 💖",
                ],
                "es": [
                    "¡{author} le dio un bonk a {target}! 🔨",
                    "¡{author} mandó a {target} de bonkazo al reino de las sombras! 👻",
                    "¡{author} le dio un bonk a {target} por ser demasiado travieso! 🙅",
                    "¡{author} bonkeó a {target} con el martillo del bonk de la justicia! ⚖️",
                    "¡{author} le dio un bonk a {target} — cero pensamientos, cabeza vacía! 🫥",
                    "¡{author} bonkeó a {target} hasta el próximo martes! 📅",
                    "¡{author} le dio un bonk suavecito a {target}, para su propio bien! 😌",
                    "¡{author} bonkeó a {target} por sus crímenes contra los juegos de palabras! 😂",
                    "¡{author} mandó a {target} a la dimensión del bonk de un bonkazo! 🌀",
                    "¡{author} bonkeó a {target} con energía de cárcel del bonk al máximo! 🔒",
                    "¡{author} le dio un bonk a {target} y gritó '¡BONK'! 📢",
                    "¡{author} bonkeó a {target} para que pensara mejores pensamientos! 💭",
                    "¡{author} le dio un bonk a {target} — el bonk estaba merecido! 👍",
                    "¡{author} bonkeó a {target} con un martillo de juguete que hace squeak! 🐽",
                    "¡{author} bonkeó a {target} y se bonkeó a sí mismo al instante! 🔄",
                    "¡{author} bonkeó a {target} por despertar a todo el server! 😴",
                    "¡{author} bonkeó a {target} en plena cabeza, estilo cartoon! 🎨",
                    "¡{author} bonkeó a {target} y su cerebro se quedó cargando! 💻",
                    "¡{author} bonkeó a {target} — directo a la cárcel del bonk, sin pasar por la casilla de salida! 🚔",
                    "¡{author} bonkeó a {target} con amor y energía de bonk! 💖",
                ],
            },
        },
    },
    "yeet": {
        "emoji": "🚀",
        "playful": True,
        "help": "Yeet someone! 🚀",
        "label": {"en": "Yeet back", "de": "Yeet zurück", "es": "Yeet de vuelta"},
        "desc": {
                "en": [
                    "{author} yeeted {target}! 🚀",
                    "{author} yeeted {target} into orbit! 🛰️",
                    "{author} yeeted {target} across the room! 💨",
                    "{author} yeeted {target} to the moon and back! 🌙",
                    "{author} yeeted {target} with the power of friendship! 💪",
                    "{author} yeeted {target} into the shadow realm! 👻",
                    "{author} yeeted {target} like a frisbee! 🥏",
                    "{author} yeeted {target} into next week! 📅",
                    "{author} yeeted {target} gently — a polite yeet! ☺️",
                    "{author} yeeted {target} over the horizon! 🌅",
                    "{author} yeeted {target} into a pile of pillows! 🛏️",
                    "{author} yeeted {target} — straight to the moon jail! 🌕",
                    "{author} yeeted {target} and yelled 'YEET'! 📢",
                    "{author} yeeted {target} with perfect form! 🏅",
                    "{author} yeeted {target} and won an imaginary gold medal! 🥇",
                    "{author} yeeted {target} at a speed of 300 yeets per second! ⚡",
                    "{author} yeeted {target} and caught them again! 🤝",
                    "{author} yeeted {target} into the nearest lake! 🌊",
                    "{author} yeeted {target} — the birds scattered! 🐦",
                    "{author} yeeted {target} with a graceful spin! 🌀",
                ],
                "de": [
                    "{author} hat {target} weggeyeeted! 🚀",
                    "{author} hat {target} ins orbit geeyeetet! 🛰️",
                    "{author} hat {target} quer durch den raum geeyeetet! 💨",
                    "{author} hat {target} zum mond und wieder zurück geeyeetet! 🌙",
                    "{author} hat {target} mit der kraft der freundschaft geeyeetet! 💪",
                    "{author} hat {target} ins schattenreich geeyeetet! 👻",
                    "{author} hat {target} wie eine frisbee geeyeetet! 🥏",
                    "{author} hat {target} bis in die nächste woche geeyeetet! 📅",
                    "{author} hat {target} sanft geeyeetet — ein höflicher yeet! ☺️",
                    "{author} hat {target} über den horizont geeyeetet! 🌅",
                    "{author} hat {target} auf einen haufen kissen geeyeetet! 🛏️",
                    "{author} hat {target} geeyeetet — direkt in den mond-knast! 🌕",
                    "{author} hat {target} geeyeetet und 'YEET' geschrien! 📢",
                    "{author} hat {target} mit perfekter haltung geeyeetet! 🏅",
                    "{author} hat {target} geeyeetet und eine imaginäre goldmedaille gewonnen! 🥇",
                    "{author} hat {target} mit 300 yeets pro sekunde geeyeetet! ⚡",
                    "{author} hat {target} geeyeetet und wieder aufgefangen! 🤝",
                    "{author} hat {target} in den nächsten see geeyeetet! 🌊",
                    "{author} hat {target} geeyeetet — die vögel sind auseinandergeflogen! 🐦",
                    "{author} hat {target} mit eleganter drehung geeyeetet! 🌀",
                ],
                "es": [
                    "¡{author} lanzó a {target} por los aires! 🚀",
                    "¡{author} mandó a {target} a la órbita de un yotazo! 🛰️",
                    "¡{author} lanzó a {target} de un lado a otro de la sala! 💨",
                    "¡{author} yoteó a {target} a la luna y de vuelta! 🌙",
                    "¡{author} yoteó a {target} con el poder de la amistad! 💪",
                    "¡{author} mandó a {target} al reino de las sombras de un yotazo! 👻",
                    "¡{author} lanzó a {target} como si fuera un frisbee! 🥏",
                    "¡{author} yoteó a {target} hasta la semana que viene! 📅",
                    "¡{author} yoteó a {target} con suavidad — un yeet educado! ☺️",
                    "¡{author} yoteó a {target} por encima del horizonte! 🌅",
                    "¡{author} lanzó a {target} a un montón de cojines! 🛏️",
                    "¡{author} yoteó a {target} — directo a la cárcel de la luna! 🌕",
                    "¡{author} yoteó a {target} y gritó '¡YEET'! 📢",
                    "¡{author} yoteó a {target} con técnica perfecta! 🏅",
                    "¡{author} yoteó a {target} y ganó una medalla de oro imaginaria! 🥇",
                    "¡{author} yoteó a {target} a 300 yeets por segundo! ⚡",
                    "¡{author} yoteó a {target} y lo atrapó de vuelta! 🤝",
                    "¡{author} lanzó a {target} al lago más cercano! 🌊",
                    "¡{author} yoteó a {target} — los pajaritos salieron volando! 🐦",
                    "¡{author} yoteó a {target} con un giro elegante! 🌀",
                ],
            },
        },
    },
}

# Shared strings (need-mention prompt, playful footer, GIF-fetch failure
# notice). Button labels + sentences live in ACTIONS above.
_BASE_STRINGS: dict = {
    "need_mention": {
        "normal": {
            "en": "You need to mention someone to use this command on them!",
            "de": "Du musst jemanden erwähnen, um diesen Befehl zu nutzen!",
            "es": "¡Tienes que mencionar a alguien para usar este comando!",
        },
    },
    "rp_footer": {
        "normal": {
            "en": "*all in good fun — no one actually got hurt!*",
            "de": "*alles nur Spaß — niemand wurde wirklich verletzt!*",
            "es": "*¡todo en broma — nadie salió herido de verdad!*",
        },
    },
    "fetch_fail": {
        "normal": {
            "en": "The GIF fairy is on a break — try again in a moment! 🥺",
            "de": "Die GIF-Fee macht gerade Pause — versuch es gleich nochmal! 🥺",
            "es": "¡El hada de los GIFs está de descanso — inténtalo en un momento! 🥺",
        },
    },
    "only_target": {
        "normal": {
            "en": "Only the person who was on the receiving end can do this one!",
            "de": "Nur die Person, an die sich die Aktion gerichtet hat, kann das tun!",
            "es": "¡Solo quien recibió la acción puede hacer esto!",
        },
    },
    "expired": {
        "normal": {
            "en": "That roleplay moment has already ended. 💤",
            "de": "Dieser Roleplay-Moment ist schon vorbei. 💤",
            "es": "Ese momento de roleplay ya terminó. 💤",
        },
    },
    "cannot_self": {
        "normal": {
            "en": "You can't do that to yourself — right-click someone else!",
            "de": "Das kannst du nicht mit dir selbst machen — klicke jemand anderen an!",
            "es": "¡No puedes hacerte eso a ti mismo — haz clic en otra persona!",
        },
    },
    "pick_hint": {
        "normal": {
            "en": "What should happen to {target}? Pick an action — the card is posted in this channel.",
            "de": "Was soll mit {target} passieren? Wähle eine Aktion — die Karte erscheint in diesem Kanal.",
            "es": "¿Qué le hacemos a {target}? Elige una acción — la tarjeta se publica en este canal.",
        },
    },
    "blocked": {
        "normal": {
            "en": "{target} has blocked you from using roleplay commands on them!",
            "de": "{target} hat dich von Roleplay-Befehlen gesperrt!",
            "es": "¡{target} te ha bloqueado para usar comandos de roleplay con ellos!",
        },
    },
    "block_success": {
        "normal": {
            "en": "🚫 {target} can no longer use roleplay commands on you.",
            "de": "🚫 {target} kann keine Roleplay-Befehle mehr auf dich anwenden.",
            "es": "🚫 {target} ya no puede usar comandos de roleplay contigo.",
        },
    },
    "already_blocked": {
        "normal": {
            "en": "{target} is already blocked from roleplaying with you.",
            "de": "{target} ist bereits vom Roleplay mit dir gesperrt.",
            "es": "{target} ya está bloqueado para el roleplay contigo.",
        },
    },
    "unblock_success": {
        "normal": {
            "en": "✅ {target} can use roleplay commands on you again.",
            "de": "✅ {target} kann wieder Roleplay-Befehle auf dich anwenden.",
            "es": "✅ {target} ya puede usar comandos de roleplay contigo de nuevo.",
        },
    },
    "not_blocked": {
        "normal": {
            "en": "You haven't blocked {target}.",
            "de": "Du hast {target} nicht gesperrt.",
            "es": "No has bloqueado a {target}.",
        },
    },
    "cannot_block_self": {
        "normal": {
            "en": "You can't block yourself — pick someone else!",
            "de": "Du kannst dich nicht selbst sperren — wähle jemand anderen!",
            "es": "¡No puedes bloquearte a ti mismo — elige a otra persona!",
        },
    },
    "db_fail": {
        "normal": {
            "en": "Something went wrong saving that — try again in a moment!",
            "de": "Beim Speichern ist etwas schiefgelaufen — versuch es gleich nochmal!",
            "es": "¡Algo salió mal al guardar eso — inténtalo en un momento!",
        },
    },
}


def _build_messages() -> dict:
    """Build the personality→lang→key message dict from ACTIONS + _BASE_STRINGS."""
    messages: dict = {
        "normal": {"en": {}, "de": {}, "es": {}},
    }
    for personality in ("normal",):
        for lang in ("en", "de", "es"):
            entry = messages[personality][lang]
            for base_key in (
                "need_mention",
                "rp_footer",
                "fetch_fail",
                "only_target",
                "expired",
                "cannot_self",
                "pick_hint",
                "blocked",
                "block_success",
                "already_blocked",
                "unblock_success",
                "not_blocked",
                "cannot_block_self",
                "db_fail",
            ):
                entry[base_key] = _BASE_STRINGS[base_key][personality][lang]

    for action, meta in ACTIONS.items():
        for lang in ("en", "de", "es"):
            messages["normal"][lang][f"{action}_back"] = meta["label"][lang]
    return messages


msg = make_msg(_build_messages())


# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────────────────────

NEKOS_API = "https://nekos.best/api/v2"
NEKOS_UA = "Niko (https://niko.sryze.cc)"  # required application User-Agent
NEKOS_TIMEOUT = 10
FETCH_RETRIES = 2

BACK_PREFIX = "roleplay_back:"  # custom_id prefix for the "do it back" buttons
PICK_PREFIX = "roleplay_pick:"  # custom_id prefix for the action-picker selects


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

async def fetch_nekos_gif(action: str) -> str | None:
    """Fetch one random GIF url from the nekos.best API (or None on failure)."""
    meta = ACTIONS.get(action)
    category = meta.get("category", action) if meta else action
    url = f"{NEKOS_API}/{category}"
    headers = {"User-Agent": NEKOS_UA}
    timeout = aiohttp.ClientTimeout(total=NEKOS_TIMEOUT)

    for attempt in range(FETCH_RETRIES):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=timeout) as resp:
                    if resp.status != 200:
                        log.warning("RolePlay", f"nekos.best {category} → HTTP {resp.status} (attempt {attempt + 1})")
                        continue
                    data = await resp.json()
            results = (data or {}).get("results") or []
            if results and results[0].get("url"):
                return results[0]["url"]
        except Exception as exc:
            log.warning("RolePlay", f"nekos.best {category} fetch failed (attempt {attempt + 1}): {exc}")
    return None


class _RoleplayLayoutView(discord.ui.LayoutView):
    """LayoutView that bypasses discord.py's in-memory per-message view store.

    discord.py registers every dispatchable view against the message it was
    sent on and would then try to invoke a *button callback* when it is
    clicked. These buttons deliberately have no callback — every click is
    resolved from the ``roleplay_actions`` table by the cog's
    ``on_interaction`` listener, which is what lets them keep working after a
    restart (there is no view store to lose). Reporting "not dispatchable"
    keeps the layout out of the per-message store so each click reaches the
    listener exactly once, instead of also tripping a callback-less dispatch
    on messages sent earlier in the same process.
    """

    def is_dispatchable(self) -> bool:
        return False


def build_roleplay_view(
    *,
    title: str,
    desc: str,
    gif: str,
    footer: str | None = None,
    back_action: str | None = None,
    back_label: str | None = None,
    disabled: bool = False,
    emoji: str | None = None,
) -> discord.ui.LayoutView:
    """Build the CV2 roleplay layout.

    The ActionRow with the "do it back" button sits at the *bottom of the
    container*, after the text/media/footer content. ``disabled`` rebuilds the
    exact same layout (so the GIF is preserved) with the button greyed out.
    """
    items: list = [
        discord.ui.TextDisplay(content=f"### {title}"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=desc),
        discord.ui.MediaGallery(discord.MediaGalleryItem(media=gif)),
    ]
    if footer:
        items.append(discord.ui.TextDisplay(content=f"-# {footer}"))

    if back_action:
        label = back_label or back_action
        if emoji and not label.startswith(emoji):
            label = f"{emoji} {label}"
        button = discord.ui.Button(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id=f"{BACK_PREFIX}{back_action}",
            disabled=disabled,
        )
        items.append(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
        items.append(discord.ui.ActionRow(button))

    view = _RoleplayLayoutView()
    view.add_item(discord.ui.Container(*items))
    return view


def _mention(user_id: int) -> str:
    return f"<@{int(user_id)}>"


def _action_title(action: str) -> str:
    meta = ACTIONS[action]
    return f"{meta['emoji']} {action}"


def _pick_desc(ctx, action: str, *, author: str, target: str) -> str:
    """Pick a random sentence variant for ``action`` (personality + lang aware).

    Mirrors ``resolve_msg``'s fallback chain: personality+lang →
    personality+en → normal+lang → normal+en. The variant is chosen AFTER the
    fallback is resolved so every language keeps its full variety.
    """
    personality = "normal"
    try:
        from utils.ai.config import get_personality

        personality = get_personality(ctx)
    except Exception:
        pass
    lang = get_lang(ctx) if ctx else "en"
    descs = (ACTIONS.get(action) or {}).get("desc") or {}
    variants = (
        descs.get(personality, {}).get(lang)
        or descs.get(personality, {}).get("en")
        or descs.get("normal", {}).get(lang)
        or descs.get("normal", {}).get("en")
        or [f"{author} {action}ed {target}!"]
    )
    return random.choice(variants).format(author=author, target=target)


def _build_action_message(ctx_or_interaction, action: str, gif: str, actor, target) -> tuple:
    """Compose one action card: (title, desc, footer, ready-to-send LayoutView).

    Shared by the prefix commands and the context-menu action picker so both
    entry points produce byte-identical cards (GIF fetch happens first, then
    this pure compose step).
    """
    meta = ACTIONS[action]
    title = _action_title(action)
    desc = _pick_desc(ctx_or_interaction, action, author=actor.mention, target=target.mention)
    footer = msg(ctx_or_interaction, "rp_footer") if meta.get("playful") else None
    view = build_roleplay_view(
        title=title,
        desc=desc,
        gif=gif,
        footer=footer,
        back_action=action,
        back_label=msg(ctx_or_interaction, f"{action}_back"),
        emoji=meta["emoji"],
    )
    return title, desc, footer, view


def build_picker_view(*, target_id: int, hint: str) -> discord.ui.LayoutView:
    """Build the ephemeral CV2 action picker behind the ``Roleplay`` menu.

    A single select lists every action (in ``ACTIONS`` insertion order). The
    target's user id rides in the select's custom id so the follow-up select
    interaction can be resolved with zero stored view state — the same model
    as the back buttons.
    """
    select = discord.ui.Select(
        custom_id=f"{PICK_PREFIX}{int(target_id)}",
        placeholder="🎭 Pick a roleplay action…",
        min_values=1,
        max_values=1,
    )
    for action, meta in ACTIONS.items():
        select.add_option(
            label=f"{meta['emoji']} {action.title()}",
            value=action,
            description=meta["help"],
        )

    view = _RoleplayLayoutView()
    view.add_item(
        discord.ui.Container(
            discord.ui.TextDisplay(content="### 🎭 Roleplay"),
            discord.ui.TextDisplay(content=hint),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(select),
        )
    )
    return view


# ─────────────────────────────────────────────────────────────────────────────
#  COG
# ─────────────────────────────────────────────────────────────────────────────

def _make_roleplay_command(action: str):
    """Factory for prefix commands — one per action, assigned in the class body.

    discord.py decides which signature parameters belong to the caller by
    checking ``is_inside_class(callback)``: a class method's ``__qualname__``
    makes it skip both ``self`` and ``ctx``. A function defined inside this
    factory would normally have ``<locals>`` in its qualname, so discord.py
    would treat ``ctx`` as the first user argument — the bug where every
    roleplay command demanded a "ctx" member. Overriding ``__qualname__`` to
    a class-like path fixes the signature parsing while keeping the factory.
    At invocation discord.py passes ``(cog, ctx, *args)`` itself, so the
    callback stays a plain unbound function taking ``(self, ctx, member)``.
    """
    meta = ACTIONS[action]

    async def roleplay_action(self, ctx: commands.Context, member: discord.Member = None):
        await self._do_roleplay(ctx, action, member)

    roleplay_action.__name__ = f"roleplay_{action}"
    roleplay_action.__qualname__ = f"RolePlayCog.roleplay_{action}"
    return commands.command(name=action, help=meta["help"])(roleplay_action)


class RolePlayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Single user context menu — Discord allows only 15 global user
        # commands, so every roleplay action lives behind one "Roleplay" entry
        # that opens an ephemeral action-picker select.
        self._context_menu = discord.app_commands.ContextMenu(
            name="Roleplay",
            callback=self._roleplay_picker,
        )
        bot.tree.add_command(self._context_menu)

    async def cog_unload(self) -> None:
        """Remove the user context menu from the tree on cog unload.

        Tree commands added manually in ``__init__`` are not cleaned up by
        discord.py, so without this ``!devreload fun`` would fail on
        ``CommandAlreadyRegistered`` when the cog re-registers it.
        """
        try:
            self.bot.tree.remove_command(self._context_menu.name, type=self._context_menu.type)
        except Exception:
            pass

    # ── expanded action commands (prefix) ──────────────────────────────────
    hug = _make_roleplay_command("hug")
    kiss = _make_roleplay_command("kiss")
    cuddle = _make_roleplay_command("cuddle")
    pat = _make_roleplay_command("pat")
    poke = _make_roleplay_command("poke")
    tickle = _make_roleplay_command("tickle")
    highfive = _make_roleplay_command("highfive")
    slap = _make_roleplay_command("slap")
    bonk = _make_roleplay_command("bonk")
    yeet = _make_roleplay_command("yeet")

    # ── block / unblock (prefix) ────────────────────────────────────────────
    @commands.command(
        name="rpblock",
        help="Block someone from using roleplay commands on you. 🚫",
    )
    async def rpblock(self, ctx: commands.Context, member: discord.Member = None):
        """Stop a member from using roleplay commands on you."""
        target = await self._resolve_block_target(ctx, member)
        if target is None:
            return
        if await self._is_blocked(ctx.author.id, target.id):
            return await ctx.send(content=msg(ctx, "already_blocked", target=target.mention))
        if not await self._add_block(ctx.author.id, target.id):
            return await ctx.send(content=msg(ctx, "db_fail"))
        await ctx.send(content=msg(ctx, "block_success", target=target.mention))

    @commands.command(
        name="rpunblock",
        help="Allow someone to use roleplay commands on you again. ✅",
    )
    async def rpunblock(self, ctx: commands.Context, member: discord.Member = None):
        """Remove your roleplay block on a member."""
        target = await self._resolve_block_target(ctx, member)
        if target is None:
            return
        if not await self._is_blocked(ctx.author.id, target.id):
            return await ctx.send(content=msg(ctx, "not_blocked", target=target.mention))
        if not await self._remove_block(ctx.author.id, target.id):
            return await ctx.send(content=msg(ctx, "db_fail"))
        await ctx.send(content=msg(ctx, "unblock_success", target=target.mention))

    async def _resolve_block_target(self, ctx, member: discord.Member | None):
        """Resolve the member argument for rpblock/rpunblock, or None on error."""
        if member is None:
            await self._reply_error(ctx, "need_mention")
            return None
        if member.id == ctx.author.id:
            await self._reply_error(ctx, "cannot_block_self")
            return None
        return member

    # ────────────────────────────────────────────────────────────────────────
    #  CONTEXT MENU → ACTION PICKER
    # ────────────────────────────────────────────────────────────────────────
    async def _roleplay_picker(self, interaction: discord.Interaction, member: discord.Member):
        """Callback of the single ``Roleplay`` user context command.

        Opens an ephemeral select menu listing every action for ``member``.
        """
        if member.id == interaction.user.id:
            try:
                await interaction.response.send_message(content=msg(interaction, "cannot_self"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        if await self._is_blocked(member.id, interaction.user.id):
            try:
                await interaction.response.send_message(
                    content=msg(interaction, "blocked", target=member.mention),
                    ephemeral=True,
                )
            except discord.HTTPException:
                pass
            return

        view = build_picker_view(
            target_id=member.id,
            hint=msg(interaction, "pick_hint", target=member.mention),
        )
        try:
            await interaction.response.send_message(view=view, ephemeral=True)
        except discord.HTTPException as exc:
            log.error("RolePlay", f"Could not open the roleplay picker: {exc}")

    async def _handle_pick(self, interaction: discord.Interaction, custom_id: str):
        """Resolve an action-picker select into a real roleplay card.

        The picker is ephemeral, so the select interaction carries everything
        needed: the chosen action in ``values`` and the target user id inside
        the custom id. The card is posted to the channel as a normal (public)
        follow-up and the ephemeral picker is then dismissed.
        """
        try:
            target_id = int(custom_id[len(PICK_PREFIX):])
        except ValueError:
            target_id = 0

        values = (interaction.data or {}).get("values") or []
        action = str(values[0]) if values else ""
        if action not in ACTIONS or not target_id:
            try:
                await interaction.response.send_message(content=msg(interaction, "expired"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        guild = interaction.guild
        member = guild.get_member(target_id) if guild is not None else None
        if member is None and guild is not None:
            try:
                member = await guild.fetch_member(target_id)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                member = None
        if member is None:
            try:
                await interaction.response.send_message(content=msg(interaction, "expired"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        if member.id == interaction.user.id:
            try:
                await interaction.response.send_message(content=msg(interaction, "cannot_self"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        if await self._is_blocked(member.id, interaction.user.id):
            try:
                await interaction.response.send_message(
                    content=msg(interaction, "blocked", target=member.mention),
                    ephemeral=True,
                )
            except discord.HTTPException:
                pass
            return

        # Ack first — fetching the GIF can take a moment.
        try:
            await interaction.response.defer()
        except discord.HTTPException:
            return

        gif = await fetch_nekos_gif(action)
        if not gif:
            try:
                await interaction.followup.send(content=msg(interaction, "fetch_fail"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        title, desc, footer, view = _build_action_message(interaction, action, gif, interaction.user, member)
        try:
            message = await interaction.followup.send(view=view)
        except discord.HTTPException as exc:
            log.error("RolePlay", f"Could not send {action} card: {exc}")
            try:
                await interaction.followup.send(content=msg(interaction, "fetch_fail"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        await self._store_action(
            message_id=message.id,
            channel_id=interaction.channel_id,
            guild_id=guild.id if guild is not None else None,
            action=action,
            actor_id=interaction.user.id,
            target_id=member.id,
            gif=gif,
            title=title,
            desc=desc,
            footer=footer,
        )

        # Done — dismiss the ephemeral picker.
        try:
            await interaction.delete_original_response()
        except discord.HTTPException:
            pass

    # ────────────────────────────────────────────────────────────────────────
    #  SHARED ROLEPLAY FLOW (prefix commands + context action picker)
    # ────────────────────────────────────────────────────────────────────────
    async def _do_roleplay(self, ctx_or_interaction, action: str, member: discord.Member | None):
        if isinstance(ctx_or_interaction, discord.Interaction):
            actor = ctx_or_interaction.user
        else:
            actor = ctx_or_interaction.author

        if member is None or member.id == actor.id:
            return await self._reply_error(ctx_or_interaction, "need_mention")

        # The target may have blocked the actor from roleplaying on them.
        if await self._is_blocked(member.id, actor.id):
            return await self._reply_error(ctx_or_interaction, "blocked", target=member.mention)

        # 1) Fetch the GIF
        gif = await fetch_nekos_gif(action)
        if not gif:
            return await self._reply_error(ctx_or_interaction, "fetch_fail")

        # 2) Compose the layout
        title, desc, footer, view = _build_action_message(ctx_or_interaction, action, gif, actor, member)

        # 3) Send
        try:
            if isinstance(ctx_or_interaction, discord.Interaction):
                await ctx_or_interaction.response.send_message(view=view)
                message = await ctx_or_interaction.original_response()
            else:
                message = await ctx_or_interaction.send(view=view)
        except discord.HTTPException as exc:
            log.error("RolePlay", f"Could not send {action} message: {exc}")
            return await self._reply_error(ctx_or_interaction, "fetch_fail")

        # 4) Persist the interaction state so the button works across restarts
        await self._store_action(
            message_id=message.id,
            channel_id=message.channel.id,
            guild_id=getattr(message.guild, "id", None),
            action=action,
            actor_id=actor.id,
            target_id=member.id,
            gif=gif,
            title=title,
            desc=desc,
            footer=footer,
        )

    async def _store_action(self, **fields):
        cxn = getattr(self.bot, "cxn", None)
        if cxn is None:
            log.warning("RolePlay", "No database connection — roleplay back-button state not stored")
            return
        try:
            await cxn.execute(
                "INSERT INTO roleplay_actions "
                "(message_id, guild_id, channel_id, action, actor_id, target_id, gif, title, desc, footer) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
                fields["message_id"],
                fields.get("guild_id"),
                fields["channel_id"],
                fields["action"],
                fields["actor_id"],
                fields["target_id"],
                fields["gif"],
                fields["title"],
                fields["desc"],
                fields.get("footer"),
            )
        except Exception as exc:
            log.warning("RolePlay", f"Could not store roleplay action for {fields.get('message_id')}: {exc}")

    # ────────────────────────────────────────────────────────────────────────
    #  ROLEPLAY BLOCKS ("don't let X use roleplay commands on me")
    # ────────────────────────────────────────────────────────────────────────
    async def _is_blocked(self, blocker_id: int, blocked_id: int) -> bool:
        """True if ``blocker_id`` has blocked ``blocked_id`` from roleplaying on them."""
        cxn = getattr(self.bot, "cxn", None)
        if cxn is None:
            return False
        try:
            row = await cxn.fetchrow(
                "SELECT 1 FROM roleplay_blocks "
                "WHERE blocker_id = $1 AND blocked_id = $2",
                int(blocker_id),
                int(blocked_id),
            )
            return row is not None
        except Exception as exc:
            log.warning("RolePlay", f"roleplay block lookup failed: {exc}")
            return False

    async def _add_block(self, blocker_id: int, blocked_id: int) -> bool:
        """Persist a block; returns False when the database is unavailable."""
        cxn = getattr(self.bot, "cxn", None)
        if cxn is None:
            return False
        try:
            await cxn.execute(
                "INSERT OR IGNORE INTO roleplay_blocks (blocker_id, blocked_id) "
                "VALUES ($1, $2)",
                int(blocker_id),
                int(blocked_id),
            )
            return True
        except Exception as exc:
            log.warning("RolePlay", f"Could not store roleplay block: {exc}")
            return False

    async def _remove_block(self, blocker_id: int, blocked_id: int) -> bool:
        """Delete a block; returns False when the database is unavailable."""
        cxn = getattr(self.bot, "cxn", None)
        if cxn is None:
            return False
        try:
            await cxn.execute(
                "DELETE FROM roleplay_blocks "
                "WHERE blocker_id = $1 AND blocked_id = $2",
                int(blocker_id),
                int(blocked_id),
            )
            return True
        except Exception as exc:
            log.warning("RolePlay", f"Could not remove roleplay block: {exc}")
            return False

    async def _reply_error(self, ctx_or_interaction, key: str, **kwargs):
        text = msg(ctx_or_interaction, key, **kwargs)
        if isinstance(ctx_or_interaction, discord.Interaction):
            try:
                await ctx_or_interaction.response.send_message(content=text, ephemeral=True)
            except discord.HTTPException:
                await ctx_or_interaction.followup.send(content=text, ephemeral=True)
        else:
            await ctx_or_interaction.send(content=text)

    # ────────────────────────────────────────────────────────────────────────
    #  PERSISTENT "DO IT BACK" BUTTON
    # ────────────────────────────────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle roleplay component interactions without stored view state.

        discord.py dispatches ``on_interaction`` for every component click, so
        both the action-picker selects and the per-message back-buttons work
        with no view store to lose across restarts: the picker custom id
        carries the target, the back-button message id resolves the stored
        action state from the DB.
        """
        if interaction.type is not discord.InteractionType.component:
            return
        custom_id = (interaction.data or {}).get("custom_id") or ""
        if custom_id.startswith(PICK_PREFIX):
            return await self._handle_pick(interaction, custom_id)
        if not custom_id.startswith(BACK_PREFIX):
            return
        action = custom_id[len(BACK_PREFIX):]
        if action not in ACTIONS:
            return
        await self._handle_back(interaction, action)

    async def _handle_back(self, interaction: discord.Interaction, action: str):
        meta = ACTIONS[action]
        cxn = getattr(self.bot, "cxn", None)
        message = interaction.message

        if cxn is None or message is None:
            try:
                await interaction.response.send_message(
                    content=msg(interaction, "expired"), ephemeral=True
                )
            except discord.HTTPException:
                pass
            return

        # Resolve the original action from persistent state
        try:
            row = await cxn.fetchrow(
                "SELECT message_id, guild_id, channel_id, action, actor_id, target_id, "
                "gif, title, desc, footer, used "
                "FROM roleplay_actions WHERE message_id = $1",
                message.id,
            )
        except Exception as exc:
            log.error("RolePlay", f"roleplay back lookup failed for {message.id}: {exc}")
            row = None

        if row is None or row.get("used"):
            try:
                await interaction.response.send_message(content=msg(interaction, "expired"), ephemeral=True)
            except discord.HTTPException:
                pass
            return

        # Only the target user may do the action back
        if interaction.user.id != int(row["target_id"]):
            try:
                await interaction.response.send_message(
                    content=msg(interaction, "only_target"), ephemeral=True
                )
            except discord.HTTPException:
                pass
            return

        # The original actor may have blocked the target in the meantime — the
        # "back" action is aimed at them, so it is refused too.
        if await self._is_blocked(row["actor_id"], row["target_id"]):
            try:
                await interaction.response.send_message(
                    content=msg(interaction, "blocked", target=_mention(row["actor_id"])),
                    ephemeral=True,
                )
            except discord.HTTPException:
                pass
            return

        # Acknowledge so we have time for the GIF fetch + message edits
        try:
            await interaction.response.defer()
        except discord.HTTPException:
            return

        # Claim the action first so double-clicks / restarts can't replay it
        try:
            await cxn.execute(
                "UPDATE roleplay_actions SET used = 1 WHERE message_id = $1", message.id
            )
        except Exception as exc:
            log.warning("RolePlay", f"Could not mark {message.id} as used: {exc}")

        # 1) The back action message — target does the action back to the author,
        #    fetched fresh from nekos.best. No button on this message.
        new_gif = await fetch_nekos_gif(action) or row["gif"]
        back_desc = _pick_desc(
            interaction,
            action,
            author=_mention(row["target_id"]),
            target=_mention(row["actor_id"]),
        )
        back_footer = msg(interaction, "rp_footer") if meta.get("playful") else None
        back_view = build_roleplay_view(
            title=row["title"] or _action_title(action),
            desc=back_desc,
            gif=new_gif,
            footer=back_footer,
        )
        try:
            await interaction.followup.send(view=back_view)
        except discord.HTTPException as exc:
            log.warning("RolePlay", f"Could not send {action} back message: {exc}")

        # 2) Disable the button on the original message — rebuild the exact same
        #    layout (preserving the GIF) with the button disabled.
        try:
            disabled_view = build_roleplay_view(
                title=row["title"] or _action_title(action),
                desc=row["desc"],
                gif=row["gif"],
                footer=row.get("footer"),
                back_action=action,
                back_label=msg(interaction, f"{action}_back"),
                emoji=meta["emoji"],
                disabled=True,
            )
            await message.edit(view=disabled_view)
        except discord.NotFound:
            pass
        except discord.HTTPException as exc:
            log.warning("RolePlay", f"Could not disable button on {message.id}: {exc}")


async def setup(bot):
    await bot.add_cog(RolePlayCog(bot))
