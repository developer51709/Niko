"""The premium launch has to be reflected in every copy of the legal pages.

Niko publishes its Privacy Policy and Terms of Service in four places: the
website (`web/src/pages/LegalPage.tsx`), the repository docs, and the
`/legal` command in four languages (the strings live in
`src/cogs/legal/locales/`). They are maintained by hand, so these checks pin
the payment, refund, and volunteer-run language that the premium update depends
on, plus the AI-provider, storage, and self-hosted disclosures.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

#: The shipped `/legal` catalogues, one per language.
LEGAL_LOCALES = [f"src/cogs/legal/locales/{lang}.json" for lang in ("en", "de", "es", "fr")]

#: Every published copy of the policy, in each place it is maintained.
ALL_COPIES = [
    "web/src/pages/LegalPage.tsx",
    "docs/privacy-policy.md",
    "docs/terms-of-service.md",
    *LEGAL_LOCALES,
]


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
    # The owner team mailbox is the point of contact, not the owner's website.
    assert "owner@niko.sryze.cc" in legal
    assert "sorenthedev.indevs.in" not in legal
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
    # The website copies carry the mailbox; the bot's catalogue uses a token
    # that resolves to the shared address from config/links.py.
    assert "owner@niko.sryze.cc" in text or "owner_contact" in text


def test_the_legal_command_says_moderation_records_are_preserved():
    """German and Spanish translate the wording, so the bot's copies are read
    together: at least the English one carries the English phrases."""
    text = _legal_copy().lower()

    assert "moderation" in text
    assert "blacklist" in text
    assert "giveaway ban" in text
    assert "court record" in text
    assert "owner_contact" in text


#: The owner account credited on every legal page. The mention is suppressed at
#: send time, so opening /legal can never ping it.
OWNER_USER_ID = "1052690741874401360"


def test_the_legal_pages_use_a_dynamic_timestamp_and_credit_the_owner():
    legal = _read("web/src/pages/LegalPage.tsx")
    cog = _read("src/cogs/legal/cog.py")

    assert "<t:1793491200:F>" in legal
    assert OWNER_USER_ID in legal
    assert OWNER_USER_ID in cog
    # Every legal send is mention-free: overview, privacy, terms, community.
    assert cog.count("AllowedMentions.none()") >= 4
    # The bot renders the same credit line through the catalogues.
    for path in LEGAL_LOCALES:
        text = _read(path)
        assert "updated_by" in text, path
        assert "{owner_mention}" in text, path


def test_the_repository_copies_use_the_same_timestamp_and_credit():
    for path in ("docs/privacy-policy.md", "docs/terms-of-service.md"):
        text = _read(path)

        assert "<t:1793491200:F>" in text
        assert f"<@{OWNER_USER_ID}>" in text


def test_the_effective_date_moved_with_the_analytics_disclosure():
    # The website renders the date through the Discord markdown timestamp.
    assert "<t:1793491200:F>" in _read("web/src/pages/LegalPage.tsx")
    assert "2026-11-01" in _read("docs/privacy-policy.md")
    assert "2026-11-01" in _read("docs/terms-of-service.md")
    # 1 November 2026 00:00 UTC, rendered as a Discord timestamp.
    assert "1793491200" in _read("src/cogs/legal/cog.py")


#: The AI provider has to be named in every copy, together with its policy URL.
GROQ_DISCLOSURE = {
    copy: ("Groq", "groq.com/privacy-policy") for copy in ALL_COPIES
}


@pytest.mark.parametrize("path,tokens", GROQ_DISCLOSURE.items())
def test_every_legal_copy_names_groq_as_the_ai_provider(path, tokens):
    text = _read(path)

    for token in tokens:
        assert token in text, f"{path} is missing the AI-provider disclosure: {token!r}"


#: Each copy states where official data lives, what deprecated deployments may
#: use, and that self-hosted instances are out of our hands.
INSTANCE_DISCLOSURE = {
    "web/src/pages/LegalPage.tsx": (
        "private MongoDB database",
        "deprecated SQLite",
        "self-hosted",
        "cannot handle data-removal requests",
    ),
    "docs/privacy-policy.md": (
        "private MongoDB database",
        "deprecated SQLite storage",
        "cannot handle data-removal requests",
    ),
    "docs/terms-of-service.md": (
        "private MongoDB database",
        "deprecated SQLite storage",
        "cannot provide support, moderation, safety, access, or data-removal help",
    ),
    "src/cogs/legal/locales/en.json": (
        "private MongoDB database",
        "deprecated SQLite storage",
        "cannot handle data-removal, access, or support requests",
    ),
    "src/cogs/legal/locales/de.json": (
        "privaten MongoDB-Datenbank",
        "veraltete SQLite-Speicherung",
        "bearbeiten keine Lösch-, Auskunfts- oder Supportanfragen",
    ),
    "src/cogs/legal/locales/es.json": (
        "base de datos MongoDB privada",
        "almacenamiento SQLite obsoleto",
        "no atendemos solicitudes de eliminación",
    ),
    "src/cogs/legal/locales/fr.json": (
        "base de données MongoDB privée",
        "stockage SQLite obsolète",
        "nous ne traitons aucune demande de suppression",
    ),
}


@pytest.mark.parametrize("path,tokens", INSTANCE_DISCLOSURE.items())
def test_every_legal_copy_scopes_official_storage_and_self_hosted_instances(path, tokens):
    text = _read(path)

    for token in tokens:
        assert token in text, f"{path} is missing the instance disclosure: {token!r}"


#: The retention policy is the detailed one, so each privacy copy names it and
#: spells out the records that survive a deletion request.
RETENTION_DISCLOSURE = {
    "web/src/pages/LegalPage.tsx": ("Data retention policy", "30 days", "no automatic expiry"),
    "docs/privacy-policy.md": ("Data retention policy", "30 days", "No automatic expiry"),
    "src/cogs/legal/locales/en.json": ("**4. Data retention**", "30 days"),
    "src/cogs/legal/locales/de.json": ("**4. Aufbewahrung**", "30 Tagen"),
    "src/cogs/legal/locales/es.json": ("**4. Retención de datos**", "30 días"),
    "src/cogs/legal/locales/fr.json": ("**4. Durée de conservation**", "30 jours"),
}


@pytest.mark.parametrize("path,tokens", RETENTION_DISCLOSURE.items())
def test_every_privacy_copy_publishes_the_retention_schedule(path, tokens):
    text = _read(path)

    for token in tokens:
        assert token in text, f"{path} is missing the retention schedule: {token!r}"
