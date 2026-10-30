"""The premium launch has to be reflected in every copy of the legal pages.

Niko publishes its Privacy Policy and Terms of Service in four places: the
website (`web/src/pages/LegalPage.tsx`), the repository docs, and the
`/legal` command in three languages (the strings live in
`src/cogs/legal/locales/`). They are maintained by hand, so these checks pin
the payment, refund, and volunteer-run language that the premium update depends
on.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

#: The three `/legal` catalogues, one per language.
LEGAL_LOCALES = [f"src/cogs/legal/locales/{lang}.json" for lang in ("en", "de", "es")]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _legal_copy() -> str:
    """Every `/legal` string in every language, as one searchable blob."""
    return "\n".join(_read(path) for path in LEGAL_LOCALES)


@pytest.mark.parametrize(
    "path",
    [
        "web/src/pages/LegalPage.tsx",
        "docs/privacy-policy.md",
        "docs/terms-of-service.md",
        *LEGAL_LOCALES,
    ],
)
def test_every_legal_copy_names_the_payment_processor(path):
    assert "OxaPay" in _read(path)


def test_the_terms_cover_refunds_and_the_volunteer_project():
    terms = _read("docs/terms-of-service.md")

    assert "Refunds" in terms
    assert "non-refundable" in terms
    assert "volunteer-run" in terms
    assert "not a company" in terms
    assert "Limitation of liability" in terms
    assert "Indemnity" in terms
    # Chargebacks for a delivered service are the most likely payment dispute.
    assert "chargeback" in terms
    assert "old enough to enter a contract" in terms


def test_the_privacy_policy_covers_payment_records_and_premium_images():
    privacy = _read("docs/privacy-policy.md")

    assert "Payment records are kept" in privacy
    assert "Premium image moderation" in privacy
    assert "fal.ai" in privacy
    assert "wallet private keys" in privacy


#: The phrase that publishes the bot-wide analytics disclosure, per copy.
#: The website and docs are English; `/legal` carries all three languages.
ANALYTICS_DISCLOSURE = {
    "web/src/pages/LegalPage.tsx": (
        "Global analytics",
        "anonymous aggregate counters only",
        "never seen, published, shared, or sold",
    ),
    "docs/privacy-policy.md": (
        "Global analytics (anonymous)",
        "never seen, published, shared, or sold",
        "last 90 days",
    ),
    "src/cogs/legal/locales/en.json": (
        "Global analytics (anonymous)",
        "never seen, published, shared, or sold",
    ),
    "src/cogs/legal/locales/de.json": (
        "Globale Analyse (anonym)",
        "an Unternehmen oder Einzelpersonen verkauft",
    ),
    "src/cogs/legal/locales/es.json": (
        "An\u00e1lisis global (an\u00f3nimo)",
        "a ninguna empresa ni persona ajena",
    ),
}


@pytest.mark.parametrize("path,tokens", ANALYTICS_DISCLOSURE.items())
def test_every_privacy_copy_discloses_the_anonymous_global_analytics(path, tokens):
    text = _read(path)

    for token in tokens:
        assert token in text, f"{path} is missing the analytics disclosure: {token!r}"


def test_the_legal_command_carries_the_same_payment_sections_in_all_languages():
    cog = _legal_copy()

    assert "**8. Payments & crypto**" in cog
    assert "**8. Zahlungen & Krypto**" in cog
    assert "**8. Pagos y cripto**" in cog
    assert "**9. Refunds**" in cog
    assert "**9. Rückerstattungen**" in cog
    assert "**9. Devoluciones**" in cog


def test_the_data_removal_page_is_linked_from_the_legal_pages():
    legal = _read("web/src/pages/LegalPage.tsx")
    footer = _read("web/src/components/Footer.tsx")

    assert "/data-removal" in legal
    assert "/data-removal" in footer
    assert "sorenthedev.indevs.in" in legal
    assert "court record" in legal
    assert "confidential" in legal


@pytest.mark.parametrize(
    "path",
    [
        "web/src/pages/LegalPage.tsx",
        "docs/privacy-policy.md",
        "docs/terms-of-service.md",
    ],
)
def test_every_legal_copy_says_moderation_records_are_preserved(path):
    text = _read(path).lower()

    assert "moderation" in text
    assert "blacklist" in text
    assert "giveaway ban" in text
    assert "court record" in text
    # The website copies use the literal URL; the bot's catalogue uses a token
    # that resolves to the shared link from config/links.py.
    assert "sorenthedev.indevs.in" in text or "owner_contact" in text


def test_the_legal_command_says_moderation_records_are_preserved():
    """German and Spanish translate the wording, so the bot's copies are read
    together: at least the English one carries the English phrases."""
    text = _legal_copy().lower()

    assert "moderation" in text
    assert "blacklist" in text
    assert "giveaway ban" in text
    assert "court record" in text
    assert "owner_contact" in text


def test_the_effective_date_moved_with_the_analytics_disclosure():
    assert "30 October 2026" in _read("web/src/pages/LegalPage.tsx")
    assert "2026-10-30" in _read("docs/privacy-policy.md")
    assert "2026-10-30" in _read("docs/terms-of-service.md")
    # 30 October 2026 00:00 UTC, rendered as a Discord timestamp.
    assert "1793318400" in _read("src/cogs/legal/cog.py")
