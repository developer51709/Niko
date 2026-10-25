"""
Legal cog — /legal privacy, /legal terms, /legal community
Trilingual EN/DE/ES, cv2 LayoutView.
Content mirrors the public website's /privacy, /terms and /community pages
(web/src/pages/LegalPage.tsx) and must be kept in sync with them.
"""

import discord
from discord.ext import commands
from config.emojis import get_emoji
from config.links import SUPPORT_SERVER, PRIVACY, TOS, COMMUNITY, WEBSITE, DATA_REMOVAL, OWNER_CONTACT
from utils.i18n import make_msg

EFFECTIVE_DATE = "<t:1792454400:F>"  # 20 October 2026

MESSAGES = {
    "normal": {
        "en": {
            # ── Privacy ──────────────────────────────────────────────
            "privacy_title": f"{get_emoji('important')} Privacy Policy",
            "privacy_body": (
                "**Effective date:** " + EFFECTIVE_DATE + "\n\n"
                "**1. What we collect**\n"
                "Niko stores only what is strictly necessary to provide its features:\n"
                "- **User IDs** — to link economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings to you.\n"
                "- **Server IDs** — to keep per-server configuration (moderation, leveling, tickets, automod, etc.).\n"
                "- **Message content** — read in real time for AI replies, automod, snipe, highlights, and leveling XP; "
                "not stored permanently except for AI conversation history (last 3 exchanges, per-user), the snipe cache (last deleted/edited message per channel, cleared on restart), "
                "and the experimental MrBeast scam-image filter (see below). Daily aggregate message, join, and leave counts are stored for the dashboard without message text or member IDs.\n"
                "- **User presence & status** — read to support member-list and bot-status features; not stored.\n"
                "- **Voice state** — used only during active music or VoiceMaster sessions; not stored.\n"
                "- **Scam-image filter (experimental)** — when a member reports a message via the right-click scam report, "
                "the reported images and message context are sent to Niko staff for review. On confirmation, a perceptual hash (a compact numeric fingerprint) "
                "and a copy of the image are stored so variants can be detected and removed automatically. Nothing is stored for servers without the filter enabled.\n"
                "- **Premium image moderation** — on a server with an active premium subscription, the URL of each image attachment posted there "
                "is sent to fal.ai's NSFW model so it can be scored. Niko stores the verdict (confidence score, file name, and moderation action), not the image itself. "
                "Nothing is sent for servers without premium.\n"
                "- **Payments** — premium subscriptions and donations are processed by OxaPay. We store the order reference, OxaPay payment reference, "
                "the Discord user and server the payment belongs to, the amount and currency, the chosen crypto asset, the deposit address shown at checkout, "
                "and the payment status and timestamps. Niko never receives or stores card numbers, bank details, wallet private keys, or seed phrases. "
                "Payment records are kept for accounting, fraud prevention, refund handling, and billing support, including after a subscription ends.\n"
                "- **Social notifier** — if a server follows social accounts, only the account name, platform, last-seen post ID, and target channel are stored.\n\n"
                "**2. How we use it**\n"
                "All data is used exclusively to run Niko's features within Discord. "
                "We never sell, share, or transfer your data to third parties.\n\n"
                "**3. Storage & security**\n"
                "Data is stored in a database on the server hosting Niko (SQLite or MongoDB, depending on deployment). "
                "No external analytics service is used.\n\n"
                "**4. Data retention**\n"
                "Economy, leveling, and configuration data persist until you or a server admin removes it. "
                "AI conversation history is capped at your last 3 exchanges and is automatically overwritten. "
                "You may erase your own AI memory at any time with `/clearhistory`.\n\n"
                "**5. Your rights & data removal**\n"
                "You may request deletion of your account data or a server you own through the data removal form: "
                f"{DATA_REMOVAL}\n"
                "You must sign in with Discord so ownership can be confirmed. A server request remains available after Niko is removed "
                "if you were its owner at the time. Moderation and safety records are preserved: bot-level blacklists, warnings, mutes, "
                "moderation cases, logs and ticket transcripts, giveaway bans, abuse strikes, and scam-image reports. A request never lifts a restriction. "
                "If a law requires release of a preserved record, send a formal request with a court record or signed legal document and an official "
                f"legal contact directly to the bot owner: {OWNER_CONTACT}. These matters are confidential and handled personally.\n\n"
                "**6. Third-party services**\n"
                "When the AI feature is enabled, your message and a short anonymised context are sent to "
                "OpenAI's API to generate a reply. OpenAI's privacy policy applies to that data: https://openai.com/policies/privacy-policy\n"
                "Premium image moderation sends image URLs to fal.ai (https://fal.ai/privacy), and payments are processed by OxaPay (https://oxapay.com/privacy).\n"
                "Other features may contact their respective services (e.g. social platforms for the notifier, Google Translate for translations); "
                "only the minimum data needed for the feature is shared. Niko does not sell or rent personal data and does not use it for advertising.\n\n"
                "**7. Payments & billing support**\n"
                "Payment records are retained after a subscription ends so billing questions, duplicate charges, refunds, and financial records "
                "can be handled accurately. You can ask about, or request deletion of, the personal data attached to a payment through the support server "
                "with the server ID and order reference; records we must keep for accounting or fraud prevention may be retained as long as the law requires.\n\n"
                "**8. Changes**\n"
                "Material changes to this policy will be announced in the support server. "
                "Continued use of Niko after a change constitutes acceptance.\n\n"
                f"-# Full policy: {PRIVACY} · Questions? Join the support server: {SUPPORT_SERVER}"
            ),

            # ── Terms ────────────────────────────────────────────────
            "terms_title": f"{get_emoji('important')} Terms of Service",
            "terms_body": (
                "**Effective date:** " + EFFECTIVE_DATE + "\n\n"
                "**1. Acceptance**\n"
                "By using Niko in any Discord server you agree to these Terms and Discord's own "
                "Terms of Service (https://discord.com/terms) and Community Guidelines (https://discord.com/guidelines).\n\n"
                "**2. Permitted use**\n"
                "Niko is provided for personal, non-commercial use within Discord servers. "
                "You may not use Niko to harass, spam, or harm other users, to violate any law, "
                "or to attempt to exploit, reverse-engineer, or disrupt Niko's operation.\n\n"
                "**3. Feature availability**\n"
                "Niko is provided **as-is** with no uptime guarantee. "
                "Features may be changed, restricted, or removed at any time without prior notice.\n\n"
                "**4. Moderation & bans**\n"
                "The bot operator reserves the right to blacklist any user or server from using Niko "
                "at any time and for any reason, including but not limited to abuse, exploitation, or "
                "violation of these Terms.\n\n"
                "**5. AI-generated content**\n"
                "Niko uses an AI language model to generate replies. "
                "AI output may be inaccurate, incomplete, or unexpected — always verify important information independently. "
                "The bot operator is not liable for any harm arising from AI-generated content.\n\n"
                "**6. Economy & virtual items**\n"
                "All in-bot currency and virtual items have no real-world value and cannot be exchanged for "
                "real money or goods. Virtual balances may be reset or wiped at any time.\n\n"
                "**7. Premium subscriptions**\n"
                "Niko Premium costs **$15 USD per server per month** and is billed manually: you choose to renew, and a reminder is sent before the term ends. "
                "There is no automatic recurring charge. Premium is a licence to use server features for one server and one term; it is not a sale of software, "
                "does not create a partnership or fiduciary relationship, and does not give you ownership in Niko. "
                "You must be old enough to enter a contract where you live, or have permission from a parent or guardian, to buy premium.\n\n"
                "**8. Payments & crypto**\n"
                "Payments are collected through OxaPay, a third-party payment processor. Crypto transactions are irreversible once broadcast to the network, "
                "and the crypto amount you send is set by the network and the provider's quote. You are responsible for sending the correct asset on the correct network, "
                "and for any taxes that apply to you. OxaPay's terms also apply. Never send funds to an address copied from somewhere other than the checkout page Niko shows you. "
                "If you believe a charge is wrong, contact support first; please do not start a chargeback or payment dispute for a service that was actually delivered, except where the law gives you that right.\n\n"
                "**9. Refunds**\n"
                "Premium and donations are purchases of digital services delivered immediately and are generally non-refundable. If a payment was duplicated, "
                "charged in error, or never activated, contact us through the support server and we will review it in good faith and, where appropriate, "
                "extend the term, issue a credit, or arrange a refund through the processor. Nothing here limits a mandatory consumer right you have under applicable law.\n\n"
                "**10. Volunteer-run project**\n"
                "Niko is a free, volunteer-run community project. It is not a company, partnership, registered business, or other legal entity. "
                "It is maintained by individuals in their personal capacity, in their own time, without payment from subscription revenue beyond covering service costs. "
                "No volunteer, contributor, or maintainer is your employee, agent, partner, or fiduciary, and none of them makes any personal promise about the service.\n\n"
                "**11. Third-party services**\n"
                "Niko depends on services we do not control, including Discord, OxaPay, fal.ai, and hosting providers. Outages, policy changes, or account actions "
                "on those services can interrupt or end features. We are not responsible for third-party services, and we are not affiliated with or endorsed by "
                "Discord, OxaPay, or fal.ai.\n\n"
                "**12. Limitation of liability**\n"
                "To the maximum extent permitted by law, the operator, maintainers, and volunteers are not liable for indirect, incidental, special, consequential, "
                "exemplary, or punitive damages, or for lost profits, revenue, data, goodwill, or server growth, arising from or related to Niko, premium, or any payment. "
                "Our total aggregate liability for all claims relating to a server's subscription is limited to the greater of the amount actually paid for that subscription "
                "in the three months before the claim or $15 USD. This does not limit liability that cannot be limited by law.\n\n"
                "**13. Indemnity**\n"
                "To the maximum extent permitted by law, you agree to indemnify and hold harmless the operator, maintainers, and volunteers from claims, damages, "
                "losses, and reasonable costs arising from your server's use of Niko, content posted in it, your breach of these terms, or your violation of another person's rights.\n\n"
                "**14. Changes & discontinuation**\n"
                "We may change, suspend, or discontinue Niko or premium, including a specific feature. If premium is discontinued during a paid term, we will handle "
                "the remaining term in good faith, for example by keeping the service running to the end of the term or by offering a pro-rata credit through the processor. "
                "We do not guarantee a cash refund where the law does not require one. If any provision of these terms is unenforceable, the rest stays in effect.\n\n"
                "**15. Contact**\n"
                f"For questions or concerns: {SUPPORT_SERVER}\n"
                f"Data removal: {DATA_REMOVAL} · Formal legal requests: {OWNER_CONTACT}\n\n"
                f"-# Full terms: {TOS} · By interacting with Niko you confirm you have read and agreed to these Terms."
            ),

            # ── Community ────────────────────────────────────────────
            "community_title": f"{get_emoji('user')} Community Policy",
            "community_body": (
                "**Effective date:** " + EFFECTIVE_DATE + "\n\n"
                "These community expectations apply to every server that uses Niko. By adding the bot to a server, "
                "the server's owners and administrators agree to uphold these standards, in addition to Discord's "
                "Terms of Service and Community Guidelines.\n\n"
                "**Discrimination and harassment**\n"
                "Servers must not permit or promote discrimination, harassment, or hate speech targeting people "
                "based on race, ethnicity, national origin, religion, disability, gender, gender identity or expression, "
                "sexual orientation, age, veteran status, or any other protected identity characteristic.\n\n"
                "**Illegal and malicious content**\n"
                "Servers must not create, host, share, or distribute illegal or malicious content. This includes, but is not "
                "limited to: child sexual abuse material (CSAM), malware and other malicious software, gore or shock content, "
                "pirated media and/or software, content that facilitates violence or terrorism, scams and phishing, "
                "and any other content that is illegal under applicable law.\n\n"
                "**Other prohibited conduct**\n"
                "Servers must not use Niko to facilitate doxxing, targeted harassment campaigns, sextortion, trafficking, "
                "or the sexualization of minors in any form.\n\n"
                "**Enforcement and investigations**\n"
                "When a server is reported or flagged for potentially violating this policy, Niko will send a warning notice "
                "to the server. The notice is followed by an investigation by Niko staff. Servers that cooperate in good faith "
                "and are found not to be breaking the policies will not receive any further action.\n\n"
                "**Obstruction of investigations**\n"
                "Banning, kicking, or otherwise removing the staff member(s) sent to investigate, or hiding, deleting, or tampering "
                "with potential evidence, is treated as an admission of guilt. Doing so will result in the server — and any users "
                "who are involved — being permanently blacklisted from further use of Niko, in addition to any other action the "
                "investigation warrants.\n\n"
                "**Reporting**\n"
                "If you believe a server using Niko is violating this policy, report it through the Niko support server. "
                "Reports are reviewed by staff and handled confidentially.\n\n"
                f"-# Full policy: {COMMUNITY}"
            ),

            "footer_privacy": f"Full policy: {PRIVACY}",
            "footer_terms":   f"Support & contact: {SUPPORT_SERVER}",
            "footer_community": f"Full policy: {COMMUNITY}",
            "legal_overview": (
                "Use `/legal privacy` for the **Privacy Policy**, `/legal terms` for the **Terms of Service**, "
                f"or `/legal community` for the **Community Policy**. You can also read them online: {WEBSITE}"
            ),
        },

        "de": {
            "privacy_title": f"{get_emoji('important')} Datenschutzerklärung",
            "privacy_body": (
                "**Gültig ab:** " + EFFECTIVE_DATE + "\n\n"
                "**1. Was wir speichern**\n"
                "Niko speichert nur das Nötigste für seine Funktionen:\n"
                "- **Nutzer-IDs** — zur Verknüpfung von Wirtschaft, XP, Erinnerungen, Geburtstagen, Highlights, KI-Gedächtnis und Verwarnungen.\n"
                "- **Server-IDs** — für serverspezifische Konfigurationen (Moderation, Leveling, Tickets, AutoMod usw.).\n"
                "- **Nachrichteninhalte** — werden für KI-Antworten, AutoMod, Snipe, Highlights und Leveling-XP in Echtzeit gelesen; "
                "dauerhaft gespeichert wird der KI-Gesprächsverlauf (letzte 3 Austausche pro Nutzer), der Snipe-Cache (letzte gelöschte/bearbeitete Nachricht pro Kanal, beim Neustart gelöscht) "
                "sowie der experimentelle MrBeast-Bild-Scam-Filter (siehe unten). Tägliche aggregierte Nachrichten-, Beitritts- und Austrittszahlen werden ohne Nachrichteninhalte oder Nutzer-IDs gespeichert.\n"
                "- **Präsenz & Status** — für Mitgliederlisten- und Bot-Status-Funktionen gelesen; nicht gespeichert.\n"
                "- **Voice-Status** — nur während aktiver Musik- oder VoiceMaster-Sitzungen; nicht gespeichert.\n"
                "- **Bild-Scam-Filter (experimentell)** — meldet jemand eine Nachricht über den Rechtsklick-Scam-Report, werden die gemeldeten Bilder und der Kontext "
                "zur Überprüfung an Niko-Staff gesendet. Bei Bestätigung wird ein perzeptueller Hash (kompakter numerischer Fingerabdruck) und eine Bildkopie gespeichert, "
                "damit Varianten automatisch erkannt und entfernt werden können. Für Server ohne aktivierten Filter wird nichts gespeichert.\n"
                "- **Premium-Bildmoderation** — ist ein Server premium-aktiv, wird die URL jedes dort geposteten Bildanhangs an fal.ais NSFW-Modell gesendet, "
                "damit es bewertet werden kann. Niko speichert das Ergebnis (Konfidenzwert, Dateiname und Moderationsaktion), nicht das Bild selbst. "
                "Für Server ohne Premium wird nichts gesendet.\n"
                "- **Zahlungen** — Premium-Abos und Spenden werden über OxaPay abgewickelt. Wir speichern die Bestellreferenz, die OxaPay-Zahlungsreferenz, "
                "die zugehörige Discord-Nutzer- und Server-ID, Betrag und Währung, die gewählte Krypto-Währung, die beim Checkout angezeigte Einzahlungsadresse "
                "sowie Zahlungsstatus und Zeitstempel. Niko erhält und speichert niemals Kartennummern, Bankdaten, Wallet-Passwörter oder Seed-Phrasen. "
                "Zahlungsdaten werden für Buchhaltung, Betrugsprävention, Rückerstattungen und Abrechnungssupport aufbewahrt, auch nach Ende eines Abos.\n"
                "- **Social-Notifier** — wenn ein Server Social-Media-Konten folgt, werden nur Kontoname, Plattform, zuletzt gesehene Post-ID und Zielkanal gespeichert.\n\n"
                "**2. Verwendung**\n"
                "Alle Daten werden ausschließlich für Nikos Funktionen auf Discord genutzt. "
                "Wir verkaufen, teilen oder übertragen deine Daten nicht an Dritte.\n\n"
                "**3. Speicherung & Sicherheit**\n"
                "Daten werden in einer Datenbank auf dem Hosting-Server gespeichert (SQLite oder MongoDB, je nach Bereitstellung). "
                "Es werden keine externen Analysedienste genutzt.\n\n"
                "**4. Aufbewahrung**\n"
                "Wirtschafts-, Leveling- und Konfigurationsdaten bleiben gespeichert, bis du oder ein Server-Admin sie entfernst. "
                "Das KI-Gesprächsgedächtnis ist auf die letzten 3 Austausche begrenzt und wird automatisch überschrieben. "
                "Dein KI-Gedächtnis kannst du jederzeit mit `/clearhistory` löschen.\n\n"
                "**5. Deine Rechte & Datenlöschung**\n"
                "Du kannst die Löschung deiner Kontodaten oder eines Servers, den du besitzt, über das Formular beantragen: "
                f"{DATA_REMOVAL}\n"
                "Dafür musst du dich mit Discord anmelden, damit die Eigentümerschaft geprüft werden kann. Ein Server-Antrag bleibt auch nach "
                "der Entfernung von Niko möglich, wenn du damals Eigentümer warst. Moderations- und Sicherheitsdaten bleiben erhalten: "
                "botweite Blacklists, Verwarnungen, Mutes, Moderationsfälle, Logs und Ticket-Transkripte, Giveaway-Bans, Abuse-Strikes und Scam-Bildmeldungen. "
                "Ein Antrag hebt keine Sperre auf. Wenn ein Gesetz die Herausgabe eines aufbewahrten Datensatzes verlangt, sende einen formellen Antrag "
                "mit Gerichtsunterlage oder unterzeichneter Urkunde und einem offiziellen Rechtskontakt direkt an den Bot-Betreiber: "
                f"{OWNER_CONTACT}. Diese Angelegenheiten werden vertraulich und persönlich bearbeitet.\n\n"
                "**6. KI-Drittanbieter**\n"
                "Wenn die KI-Funktion aktiviert ist, werden deine Nachricht und ein kurzer anonymisierter Kontext "
                "an die OpenAI-API gesendet. Es gilt OpenAIs Datenschutzrichtlinie: https://openai.com/policies/privacy-policy\n"
                "Premium-Bildmoderation sendet Bild-URLs an fal.ai (https://fal.ai/privacy), Zahlungen werden von OxaPay verarbeitet (https://oxapay.com/privacy).\n"
                "Andere Funktionen kontaktieren ggf. ihre jeweiligen Dienste (z. B. Social-Plattformen für den Notifier, Google Translate für Übersetzungen); "
                "geteilt werden nur die für die Funktion nötigen Daten. Niko verkauft oder vermietet keine personenbezogenen Daten und nutzt sie nicht für Werbung.\n\n"
                "**7. Zahlungen & Abrechnungssupport**\n"
                "Zahlungsdaten bleiben nach Ende eines Abos gespeichert, damit Abrechnungsfragen, Doppelabbuchungen, Rückerstattungen und Buchführung korrekt "
                "bearbeitet werden können. Auskunft über die mit einer Zahlung verknüpften Daten oder deren Löschung kannst du über den Support-Server mit Server-ID "
                "und Bestellreferenz anfragen; Daten, die wir für Buchhaltung oder Betrugsprävention aufbewahren müssen, können so lange gespeichert bleiben, wie es das Gesetz verlangt.\n\n"
                "**8. Änderungen**\n"
                f"Wesentliche Änderungen werden im Support-Server angekündigt: {SUPPORT_SERVER}"
            ),

            "terms_title": f"{get_emoji('important')} Nutzungsbedingungen",
            "terms_body": (
                "**Gültig ab:** " + EFFECTIVE_DATE + "\n\n"
                "**1. Zustimmung**\n"
                "Durch die Nutzung von Niko stimmst du diesen Bedingungen sowie Discords "
                "Nutzungsbedingungen und Community-Richtlinien zu.\n\n"
                "**2. Erlaubte Nutzung**\n"
                "Niko darf nicht für Belästigung, Spam, Gesetzesverstöße oder Versuche genutzt werden, "
                "Niko zu manipulieren oder zu stören.\n\n"
                "**3. Verfügbarkeit**\n"
                "Niko wird ohne Uptime-Garantie bereitgestellt. Funktionen können jederzeit geändert oder entfernt werden.\n\n"
                "**4. Moderation & Sperren**\n"
                "Der Bot-Betreiber behält sich das Recht vor, Nutzer oder Server jederzeit zu sperren.\n\n"
                "**5. KI-Inhalte**\n"
                "KI-generierte Antworten können ungenau sein. Der Bot-Betreiber haftet nicht für daraus entstehende Schäden.\n\n"
                "**6. Virtuelles Guthaben**\n"
                "Bot-Währung und virtuelle Gegenstände haben keinen realen Geldwert und können jederzeit zurückgesetzt werden.\n\n"
                "**7. Premium-Abos**\n"
                "Niko Premium kostet **15 USD pro Server und Monat** und wird manuell verlängert: Du entscheidest über die Verlängerung und erhältst vor Ablauf eine Erinnerung. "
                "Es gibt keine automatische wiederkehrende Abbuchung. Premium ist eine Lizenz zur Nutzung von Serverfunktionen für einen Server und einen Zeitraum; "
                "es ist kein Softwarekauf, begründet keine Partnerschaft oder Treuhandbeziehung und gibt dir keine Eigentumsrechte an Niko. "
                "Du musst alt genug sein, um in deinem Land einen Vertrag zu schließen, oder die Erlaubnis eines Erziehungsberechtigten haben, um Premium zu kaufen.\n\n"
                "**8. Zahlungen & Krypto**\n"
                "Zahlungen werden über OxaPay, einen Drittanbieter, abgewickelt. Krypto-Transaktionen sind nach dem Senden ins Netzwerk unwiderruflich, "
                "und der Krypto-Betrag wird durch Netzwerk und Anbieter-Quote bestimmt. Du bist dafür verantwortlich, das richtige Asset im richtigen Netzwerk zu senden, "
                "sowie für deine Steuern. Es gelten zusätzlich OxaPays Bedingungen. Sende niemals Guthaben an eine Adresse, die nicht aus dem von Niko angezeigten Checkout stammt. "
                "Hältst du eine Abbuchung für falsch, wende dich zuerst an den Support; starte bitte kein Chargeback oder Zahlungsstreitverfahren für eine tatsächlich erbrachte Leistung, "
                "es sei denn, das Gesetz gibt dir dieses Recht.\n\n"
                "**9. Rückerstattungen**\n"
                "Premium und Spenden sind sofort erbrachte digitale Leistungen und grundsätzlich nicht erstattungsfähig. Wurde eine Zahlung doppelt abgebucht, "
                "fehlerhaft ausgelöst oder nie aktiviert, wende dich über den Support-Server an uns; wir prüfen den Fall nach Treu und Glauben und verlängern den Zeitraum, "
                "gewähren eine Gutschrift oder veranlassen eine Rückerstattung über den Anbieter. Zwingende Verbraucherrechte nach anwendbarem Recht bleiben unberührt.\n\n"
                "**10. Ehrenamtliches Projekt**\n"
                "Niko ist ein kostenloses, ehrenamtlich betriebenes Community-Projekt. Es ist kein Unternehmen, keine Personengesellschaft, kein eingetragener Betrieb "
                "und keine andere juristische Person. Es wird von Einzelpersonen in eigener Verantwortung und Freizeit betrieben, ohne Vergütung aus Abo-Einnahmen "
                "über die Deckung der Dienstkosten hinaus. Kein Freiwilliger, Mitwirkender oder Maintainer ist dein Arbeitnehmer, Vertreter, Partner oder Treuhänder, "
                "und niemand gibt eine persönliche Zusage für den Dienst.\n\n"
                "**11. Drittanbieter**\n"
                "Niko hängt von Diensten ab, die wir nicht kontrollieren, darunter Discord, OxaPay, fal.ai und Hosting-Anbieter. Ausfälle, Richtlinienänderungen oder "
                "Kontosperren dort können Funktionen unterbrechen oder beenden. Wir sind für Drittanbieter nicht verantwortlich und stehen in keiner Verbindung zu "
                "Discord, OxaPay oder fal.ai und werden von ihnen nicht unterstützt.\n\n"
                "**12. Haftungsbeschränkung**\n"
                "Soweit gesetzlich zulässig, haften Betreiber, Maintainer und Freiwillige nicht für mittelbare, zufällige, besondere, Folge-, Straf- oder "
                "Abschreckungsschäden oder für entgangenen Gewinn, Umsatz, Daten, Goodwill oder Serverwachstum im Zusammenhang mit Niko, Premium oder Zahlungen. "
                "Die Gesamthaftung für alle Ansprüche zu einem Server-Abo ist auf den höheren Betrag aus den tatsächlich für dieses Abo in den drei Monaten vor dem "
                "Anspruch gezahlten Summe oder 15 USD begrenzt. Zwingende gesetzliche Haftung bleibt unberührt.\n\n"
                "**13. Freistellung**\n"
                "Soweit gesetzlich zulässig, stellst du Betreiber, Maintainer und Freiwillige von Ansprüchen, Schäden, Verlusten und angemessenen Kosten frei, "
                "die aus der Nutzung von Niko durch deinen Server, dort veröffentlichten Inhalten, deinem Verstoß gegen diese Bedingungen oder der Verletzung "
                "Rechte Dritter entstehen.\n\n"
                "**14. Änderungen & Einstellung**\n"
                "Wir können Niko oder Premium (auch einzelne Funktionen) ändern, aussetzen oder einstellen. Wird Premium während eines bezahlten Zeitraums eingestellt, "
                "behandeln wir den Restzeitraum nach Treu und Glauben, etwa indem wir den Dienst bis zum Ende weiterlaufen lassen oder eine anteilige Gutschrift über "
                "den Anbieter anbieten. Eine Barerstattung garantieren wir nur, soweit gesetzlich erforderlich. Ist eine Bestimmung unwirksam, bleibt der Rest wirksam.\n\n"
                f"**15. Kontakt:** {SUPPORT_SERVER} · Datenlöschung: {DATA_REMOVAL} · Formelle Rechtsanträge: {OWNER_CONTACT}"
            ),

            "community_title": f"{get_emoji('user')} Community-Richtlinie",
            "community_body": (
                "**Gültig ab:** " + EFFECTIVE_DATE + "\n\n"
                "Diese Community-Standards gelten für jeden Server, der Niko nutzt. Mit dem Hinzufügen des Bots "
                "verpflichten sich die Server-Inhaber und -Admins zusätzlich zu Discords Nutzungsbedingungen und "
                "Community-Richtlinien zur Einhaltung dieser Standards.\n\n"
                "**Diskriminierung und Belästigung**\n"
                "Server dürfen Diskriminierung, Belästigung oder Hassrede aufgrund von Ethnizität, nationaler Herkunft, "
                "Religion, Behinderung, Geschlecht, Geschlechtsidentität oder -ausdruck, sexueller Orientierung, Alter, "
                "Veteranenstatus oder anderen geschützten Merkmalen weder erlauben noch fördern.\n\n"
                "**Illegale und bösartige Inhalte**\n"
                "Server dürfen keine illegalen oder bösartigen Inhalte erstellen, hosten, teilen oder verbreiten. Dazu zählen "
                "u. a.: Missbrauchsdarstellungen Minderjähriger (CSAM), Schadsoftware, Gore- oder Shock-Content, Raubkopien "
                "von Medien/Software, Inhalte, die Gewalt oder Terrorismus fördern, Scams und Phishing sowie alles andere, "
                "was nach anwendbarem Recht illegal ist.\n\n"
                "**Weiteres verbotenes Verhalten**\n"
                "Niko darf nicht für Doxxing, gezielte Belästigungskampagnen, Sextortion, Handel mit Menschen oder die "
                "sexualisierte Darstellung Minderjähriger genutzt werden.\n\n"
                "**Durchsetzung und Untersuchungen**\n"
                "Wird ein Server gemeldet oder wegen eines möglichen Verstoßes markiert, erhält der Server eine Warnung, "
                "der eine Untersuchung durch das Niko-Team folgt. Server, die gutgläubig mitwirken und die Richtlinien "
                "nicht brechen, erhalten keine weiteren Maßnahmen.\n\n"
                "**Behinderung von Untersuchungen**\n"
                "Das Bannen, Kicken oder sonstige Entfernen der zur Untersuchung entsandten Staff-Mitglieder oder das "
                "Verbergen, Löschen oder Manipulieren möglicher Beweise gilt als Schuldeingeständnis. Das führt zur "
                "dauerhaften Sperrung des Servers — und aller beteiligten Nutzer — von Niko, zusätzlich zu allen "
                "weiteren Maßnahmen der Untersuchung.\n\n"
                "**Meldungen**\n"
                "Wenn du glaubst, dass ein Niko-Server diese Richtlinie verletzt, melde ihn im Niko-Support-Server. "
                "Meldungen werden vertraulich vom Team geprüft.\n\n"
                f"-# Vollständige Richtlinie: {COMMUNITY}"
            ),

            "footer_privacy": f"Vollständige Richtlinie: {PRIVACY}",
            "footer_terms":   f"Support & Kontakt: {SUPPORT_SERVER}",
            "footer_community": f"Vollständige Richtlinie: {COMMUNITY}",
            "legal_overview": (
                "Nutze `/legal privacy` für die **Datenschutzerklärung**, `/legal terms` für die **Nutzungsbedingungen** "
                f"oder `/legal community` für die **Community-Richtlinie**. Online: {WEBSITE}"
            ),
        },

        "es": {
            "privacy_title": f"{get_emoji('important')} Política de Privacidad",
            "privacy_body": (
                "**Fecha de vigencia:** " + EFFECTIVE_DATE + "\n\n"
                "**1. Qué recopilamos**\n"
                "Niko almacena solo lo estrictamente necesario para sus funciones:\n"
                "- **IDs de usuario** — para vincular economía, XP, recordatorios, cumpleaños, highlights, memoria de IA y advertencias.\n"
                "- **IDs de servidor** — para configuraciones por servidor (moderación, leveling, tickets, automod, etc.).\n"
                "- **Contenido de mensajes** — leído en tiempo real para respuestas de IA, automod, snipe, highlights y XP; "
                "almacenado permanentemente: el historial de conversación de IA (últimos 3 intercambios por usuario), la caché de snipe (último mensaje borrado/editado por canal, se borra al reiniciar) "
                "y el filtro experimental de imágenes de scam de MrBeast (ver abajo). El panel guarda totales diarios agregados sin texto de mensajes ni IDs de miembros.\n"
                "- **Presencia y estado** — leído para funciones de lista de miembros; no almacenado.\n"
                "- **Estado de voz** — solo durante sesiones activas de música o VoiceMaster; no almacenado.\n"
                "- **Filtro de imágenes de scam (experimental)** — cuando alguien reporta un mensaje con el reporte de scam por clic derecho, "
                "las imágenes reportadas y el contexto se envían al staff de Niko para revisión. Al confirmarse, se guarda un hash perceptual (huella numérica compacta) "
                "y una copia de la imagen para detectar y eliminar variantes automáticamente. En servidores sin el filtro no se guarda nada.\n"
                "- **Moderación de imágenes premium** — en un servidor con suscripción premium activa, la URL de cada imagen publicada allí se envía al modelo NSFW de fal.ai "
                "para puntuarla. Niko guarda el veredicto (puntuación de confianza, nombre del archivo y acción de moderación), no la imagen. "
                "En servidores sin premium no se envía nada.\n"
                "- **Pagos** — las suscripciones premium y donaciones se procesan con OxaPay. Guardamos la referencia del pedido, la referencia de pago de OxaPay, "
                "el ID de Discord del usuario y del servidor, el importe y la moneda, la criptomoneda elegida, la dirección de depósito mostrada al pagar "
                "y el estado y la fecha del pago. Niko nunca recibe ni almacena números de tarjeta, datos bancarios, claves privadas ni frases semilla. "
                "Los registros de pago se conservan para contabilidad, prevención de fraude, devoluciones y soporte de facturación, incluso después de que termine una suscripción.\n"
                "- **Notificador social** — si un servidor sigue cuentas sociales, solo se guardan el nombre de la cuenta, la plataforma, el último ID visto y el canal de destino.\n\n"
                "**2. Uso**\n"
                "Todos los datos se usan exclusivamente para las funciones de Niko en Discord. "
                "Nunca vendemos, compartimos ni transferimos tus datos a terceros.\n\n"
                "**3. Almacenamiento y seguridad**\n"
                "Los datos se guardan en una base de datos en el servidor que aloja a Niko (SQLite o MongoDB, según el despliegue). "
                "No se usan servicios de análisis externos.\n\n"
                "**4. Retención de datos**\n"
                "Los datos de economía, leveling y configuración persisten hasta que tú o un administrador los elimine. "
                "El historial de conversación de IA está limitado a los últimos 3 intercambios. "
                "Puedes borrar tu memoria de IA en cualquier momento con `/clearhistory`.\n\n"
                "**5. Tus derechos y eliminación de datos**\n"
                "Puedes solicitar la eliminación de los datos de tu cuenta o de un servidor que poseas mediante el formulario: "
                f"{DATA_REMOVAL}\n"
                "Debes iniciar sesión con Discord para confirmar la propiedad. La solicitud de un servidor sigue disponible después de que Niko "
                "se retire si eras su propietario en ese momento. Los registros de moderación y seguridad se conservan: listas negras globales, "
                "advertencias, mutes, casos de moderación, registros y transcripciones de tickets, vetos de sorteos, strikes por abuso e informes de imágenes de estafa. "
                "Una solicitud nunca levanta una restricción. Si la ley exige la entrega de un registro conservado, envía una solicitud formal con "
                "un registro judicial o documento legal firmado y un contacto legal oficial directamente al propietario del bot: "
                f"{OWNER_CONTACT}. Estos asuntos son confidenciales y se gestionan personalmente.\n\n"
                "**6. Servicios de terceros**\n"
                "Cuando la función de IA está activada, tu mensaje y un contexto breve anonimizado se envían "
                "a la API de OpenAI. Se aplica la política de privacidad de OpenAI: https://openai.com/policies/privacy-policy\n"
                "La moderación de imágenes premium envía URLs de imágenes a fal.ai (https://fal.ai/privacy) y los pagos los procesa OxaPay (https://oxapay.com/privacy).\n"
                "Otras funciones pueden contactar a sus respectivos servicios (p. ej. plataformas sociales para el notificador, Google Translate para traducciones); "
                "solo se comparte lo mínimo necesario para la función. Niko no vende ni alquila datos personales y no los usa para publicidad.\n\n"
                "**7. Pagos y soporte de facturación**\n"
                "Los registros de pago se conservan después de que termine una suscripción para poder atender dudas, cargos duplicados, devoluciones y registros contables. "
                "Puedes preguntar por los datos personales asociados a un pago, o pedir su eliminación, a través del servidor de soporte indicando el ID del servidor y la "
                "referencia del pedido; los registros que debamos conservar por contabilidad o prevención de fraude pueden mantenerse mientras exija la ley.\n\n"
                "**8. Cambios**\n"
                f"Los cambios importantes se anunciarán en el servidor de soporte: {SUPPORT_SERVER}"
            ),

            "terms_title": f"{get_emoji('important')} Términos de Servicio",
            "terms_body": (
                "**Fecha de vigencia:** " + EFFECTIVE_DATE + "\n\n"
                "**1. Aceptación**\n"
                "Al usar Niko aceptas estos Términos y los Términos de Servicio y Normas de la Comunidad de Discord.\n\n"
                "**2. Uso permitido**\n"
                "No puedes usar Niko para acosar, spamear, violar leyes, ni intentar explotar o interrumpir su funcionamiento.\n\n"
                "**3. Disponibilidad**\n"
                "Niko se proporciona tal cual, sin garantía de disponibilidad. Las funciones pueden cambiar o eliminarse en cualquier momento.\n\n"
                "**4. Moderación y bloqueos**\n"
                "El operador puede bloquear a cualquier usuario o servidor en cualquier momento por incumplimiento.\n\n"
                "**5. Contenido generado por IA**\n"
                "Las respuestas de IA pueden ser inexactas. El operador no es responsable de los daños derivados de ellas.\n\n"
                "**6. Moneda virtual**\n"
                "La moneda del bot y los artículos virtuales no tienen valor real y pueden reiniciarse en cualquier momento.\n\n"
                "**7. Suscripciones premium**\n"
                "Niko Premium cuesta **15 USD por servidor y mes** y se renueva manualmente: tú decides renovar y recibes un recordatorio antes de que termine el plazo. "
                "No hay cobro recurrente automático. Premium es una licencia de uso de funciones del servidor para un servidor y un plazo; no es una venta de software, "
                "no crea una sociedad ni una relación fiduciaria, y no te otorga propiedad sobre Niko. "
                "Debes tener edad suficiente para celebrar un contrato en tu país, o contar con permiso de tu padre, madre o tutor, para comprar premium.\n\n"
                "**8. Pagos y cripto**\n"
                "Los pagos se cobran mediante OxaPay, un procesador externo. Las transacciones cripto son irreversibles una vez enviadas a la red, y la cantidad de cripto "
                "la determina la red y la cotización del proveedor. Eres responsable de enviar el activo correcto en la red correcta y de tus impuestos. También se aplican "
                "los términos de OxaPay. Nunca envíes fondos a una dirección copiada de otro sitio que no sea la página de pago que muestra Niko. "
                "Si crees que un cobro es incorrecto, contacta primero con soporte; no inicies una disputa o contracargo por un servicio que sí se prestó, salvo que la ley te otorgue ese derecho.\n\n"
                "**9. Devoluciones**\n"
                "Premium y las donaciones son servicios digitales entregados de inmediato y, por lo general, no son reembolsables. Si un pago se duplicó, se cobró por error "
                "o nunca se activó, contáctanos en el servidor de soporte: lo revisaremos de buena fe y, cuando corresponda, ampliaremos el plazo, emitiremos un abono o "
                "gestionaremos una devolución con el procesador. Nada de esto limita los derechos obligatorios que te reconozca la ley aplicable.\n\n"
                "**10. Proyecto de voluntarios**\n"
                "Niko es un proyecto comunitario gratuito gestionado por voluntarios. No es una empresa, sociedad, negocio registrado ni otra entidad legal. "
                "Lo mantienen personas a título personal, en su tiempo libre, sin retribución de los ingresos por suscripciones más allá de cubrir los costes del servicio. "
                "Ningún voluntario, colaborador o mantenedor es tu empleado, agente, socio ni fiduciario, y ninguno hace promesas personales sobre el servicio.\n\n"
                "**11. Servicios de terceros**\n"
                "Niko depende de servicios que no controlamos, incluidos Discord, OxaPay, fal.ai y los proveedores de alojamiento. Caídas, cambios de política o "
                "acciones sobre esas cuentas pueden interrumpir o terminar funciones. No somos responsables de servicios de terceros y no estamos afiliados ni respaldados "
                "por Discord, OxaPay ni fal.ai.\n\n"
                "**12. Limitación de responsabilidad**\n"
                "En la máxima medida permitida por la ley, el operador, los mantenedores y los voluntarios no son responsables de daños indirectos, incidentales, especiales, "
                "consecuentes, ejemplares o punitivos, ni de pérdida de beneficios, ingresos, datos, reputación o crecimiento del servidor, derivados de Niko, premium o "
                "cualquier pago. La responsabilidad total por todas las reclamaciones relacionadas con la suscripción de un servidor se limita al mayor de la cantidad "
                "realmente pagada por esa suscripción en los tres meses anteriores a la reclamación o 15 USD. Esto no limita la responsabilidad que la ley no permite limitar.\n\n"
                "**13. Indemnización**\n"
                "En la máxima medida permitida por la ley, aceptas indemnizar y mantener indemnes al operador, mantenedores y voluntarios frente a reclamaciones, daños, "
                "pérdidas y costes razonables derivados del uso de Niko por tu servidor, del contenido publicado en él, de tu incumplimiento de estos términos o de la "
                "vulneración de derechos de terceros.\n\n"
                "**14. Cambios y suspensión**\n"
                "Podemos cambiar, suspender o retirar Niko o premium, incluida una función concreta. Si premium se retira durante un plazo pagado, gestionaremos el tiempo "
                "restante de buena fe, por ejemplo manteniendo el servicio hasta el final del plazo u ofreciendo un abono proporcional a través del procesador. "
                "No garantizamos un reembolso en efectivo cuando la ley no lo exija. Si alguna disposición no es aplicable, el resto sigue vigente.\n\n"
                f"**15. Contacto:** {SUPPORT_SERVER} · Eliminación de datos: {DATA_REMOVAL} · Solicitudes legales formales: {OWNER_CONTACT}"
            ),

            "community_title": f"{get_emoji('user')} Política de Comunidad",
            "community_body": (
                "**Fecha de vigencia:** " + EFFECTIVE_DATE + "\n\n"
                "Estas expectativas de comunidad aplican a cada servidor que usa Niko. Al añadir el bot a un servidor, "
                "los propietarios y administradores aceptan mantener estos estándares, además de los Términos de Servicio "
                "y Normas de la Comunidad de Discord.\n\n"
                "**Discriminación y acoso**\n"
                "Los servidores no deben permitir ni promover discriminación, acoso ni discurso de odio por etnia, origen nacional, "
                "religión, discapacidad, género, identidad o expresión de género, orientación sexual, edad, condición de veterano "
                "u otra característica protegida.\n\n"
                "**Contenido ilegal y malicioso**\n"
                "Los servidores no deben crear, alojar, compartir ni distribuir contenido ilegal o malicioso. Esto incluye, entre otros: "
                "material de abuso sexual infantil (CSAM), malware u otro software malicioso, contenido gore o chocante, medios y/o software piratas, "
                "contenido que promueva violencia o terrorismo, estafas y phishing, y cualquier otro contenido ilegal según la ley aplicable.\n\n"
                "**Otros conductas prohibidas**\n"
                "Los servidores no deben usar Niko para facilitar doxxing, campañas de acoso dirigido, sextorsión, trata de personas "
                "o la sexualización de menores en cualquier forma.\n\n"
                "**Aplicación e investigaciones**\n"
                "Cuando se reporta o marca un servidor por una posible violación de esta política, Niko enviará un aviso de advertencia al servidor, "
                "seguido de una investigación por parte del staff de Niko. Los servidores que cooperen de buena fe y no estén violando las políticas "
                "no recibirán ninguna acción adicional.\n\n"
                "**Obstrucción de investigaciones**\n"
                "Banear, expulsar o eliminar de otra forma al staff enviado a investigar, u ocultar, borrar o manipular posibles evidencias, "
                "se trata como una admisión de culpa. Esto resultará en el baneo permanente del servidor — y de cualquier usuario involucrado — "
                "de Niko, además de cualquier otra acción que la investigación justifique.\n\n"
                "**Reportes**\n"
                "Si crees que un servidor que usa Niko viola esta política, repórtalo en el servidor de soporte de Niko. "
                "Los reportes son revisados por el staff y manejados de forma confidencial.\n\n"
                f"-# Política completa: {COMMUNITY}"
            ),

            "footer_privacy": f"Política completa: {PRIVACY}",
            "footer_terms":   f"Soporte y contacto: {SUPPORT_SERVER}",
            "footer_community": f"Política completa: {COMMUNITY}",
            "legal_overview": (
                "Usa `/legal privacy` para la **Política de Privacidad**, `/legal terms` para los **Términos de Servicio** "
                f"o `/legal community` para la **Política de Comunidad**. En línea: {WEBSITE}"
            ),
        },
    }
}

msg = make_msg(MESSAGES)


def _send_legal(ctx: commands.Context, title_key: str, body_key: str):
    """Build a cv2 LayoutView for a legal document page."""
    title = msg(ctx, title_key)
    body  = msg(ctx, body_key)

    text = f"### {title}\n\n{body}"

    view      = discord.ui.LayoutView()
    container = discord.ui.Container(
        discord.ui.TextDisplay(content=text)
    )
    view.add_item(container)
    return view


class LegalCog(commands.Cog, name="Legal"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_group(
        name="legal",
        description="Privacy policy, terms of service and community policy for Niko",
        invoke_without_command=True,
    )
    async def legal(self, ctx: commands.Context):
        """Shows an overview pointing to the sub-commands."""
        icon = get_emoji("important")
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"### {icon} Legal\n"
                    + msg(ctx, "legal_overview")
                )
            )
        ))
        await ctx.send(view=view, ephemeral=True)

    @legal.command(
        name="privacy",
        description="Read Niko's privacy policy",
    )
    async def privacy(self, ctx: commands.Context):
        """Displays Niko's Privacy Policy."""
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=True)
        view = _send_legal(ctx, "privacy_title", "privacy_body")
        await ctx.send(view=view, ephemeral=True)

    @legal.command(
        name="terms",
        description="Read Niko's terms of service",
    )
    async def terms(self, ctx: commands.Context):
        """Displays Niko's Terms of Service."""
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=True)
        view = _send_legal(ctx, "terms_title", "terms_body")
        await ctx.send(view=view, ephemeral=True)

    @legal.command(
        name="community",
        description="Read Niko's community policy for servers",
    )
    async def community(self, ctx: commands.Context):
        """Displays Niko's Community Policy."""
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=True)
        view = _send_legal(ctx, "community_title", "community_body")
        await ctx.send(view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(LegalCog(bot))
