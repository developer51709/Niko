"""The amount argument economy and casino commands accept.

Players rarely know their exact balance, and asking ``/balance`` first just to
copy a number into ``/pay`` or ``/slots play`` is busywork. Every command that
takes a sum of coins therefore accepts the word ``all`` and spends whatever the
wallet holds at that moment.
"""

from __future__ import annotations

#: Words that mean "everything the player has". ``max`` and ``everything`` are
#: accepted alongside ``all`` because that is what people type when a bet is
#: rejected for being over the balance.
ALL_WORDS = frozenset({"all", "max", "everything"})


def resolve_amount(value, balance: int) -> int | None:
    """Return the number of coins ``value`` names, or ``None`` if it is not one.

    ``all`` (and its synonyms) resolves to ``balance``, so a caller passes the
    wallet it just read and gets the whole thing back. Thousand separators are
    ignored, because ``1,000`` is how the wallet is displayed. Zero and negative
    values are returned unchanged: each command keeps its own wording for "that
    bet has to be positive".
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    text = str(value if value is not None else "").strip().lower()
    text = text.replace(",", "").replace("_", "").replace(" ", "")
    if not text:
        return None
    if text in ALL_WORDS:
        return int(balance or 0)
    try:
        return int(text)
    except ValueError:
        return None


__all__ = ["ALL_WORDS", "resolve_amount"]
