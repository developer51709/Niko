"""
Legal cog — /legal privacy, /legal terms, /legal community
Trilingual EN/DE/ES, cv2 LayoutView, normal/cafe personalities.
Content mirrors the public website's /privacy, /terms and /community pages
(web/src/pages/LegalPage.tsx) and must be kept in sync with them.
"""

import discord
from discord.ext import commands
from config.emojis import get_emoji
from config.links import SUPPORT_SERVER, PRIVACY, TOS, COMMUNITY, WEBSITE
from utils.i18n import make_msg

EFFECTIVE_DATE = "<t:1790812800:F>"  # 1 October 2026

MESSAGES = {
    "normal": {
        "en": {
            # ── Privacy ──────────────────────────────────────────────
            "privacy_title": f"{get_emoji('icon_important')} Privacy Policy",
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
                "**5. Your rights**\n"
                "You may request deletion of all data associated with your User ID at any time by contacting "
                f"the bot owner in the support server: {SUPPORT_SERVER}\n\n"
                "**6. Third-party services**\n"
                "When the AI feature is enabled, your message and a short anonymised context are sent to "
                "OpenAI's API to generate a reply. OpenAI's privacy policy applies to that data: https://openai.com/policies/privacy-policy\n"
                "Other features may contact their respective services (e.g. social platforms for the notifier, Google Translate for translations); "
                "only the minimum data needed for the feature is shared.\n\n"
                "**7. Changes**\n"
                "Material changes to this policy will be announced in the support server. "
                "Continued use of Niko after a change constitutes acceptance.\n\n"
                f"-# Full policy: {PRIVACY} · Questions? Join the support server: {SUPPORT_SERVER}"
            ),

            # ── Terms ────────────────────────────────────────────────
            "terms_title": f"{get_emoji('icon_important')} Terms of Service",
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
                "**7. Limitation of liability**\n"
                "Niko and its operator are not liable for any direct, indirect, or consequential damages "
                "arising from the use or inability to use Niko.\n\n"
                "**8. Contact**\n"
                f"For questions or concerns: {SUPPORT_SERVER}\n\n"
                f"-# Full terms: {TOS} · By interacting with Niko you confirm you have read and agreed to these Terms."
            ),

            # ── Community ────────────────────────────────────────────
            "community_title": f"{get_emoji('icon_users')} Community Policy",
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
            "privacy_title": f"{get_emoji('icon_important')} Datenschutzerklärung",
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
                "**5. Deine Rechte**\n"
                "Du kannst jederzeit die Löschung aller mit deiner Nutzer-ID verknüpften Daten verlangen. "
                f"Wende dich dafür an den Bot-Betreiber im Support-Server: {SUPPORT_SERVER}\n\n"
                "**6. KI-Drittanbieter**\n"
                "Wenn die KI-Funktion aktiviert ist, werden deine Nachricht und ein kurzer anonymisierter Kontext "
                "an die OpenAI-API gesendet. Es gilt OpenAIs Datenschutzrichtlinie: https://openai.com/policies/privacy-policy\n"
                "Andere Funktionen kontaktieren ggf. ihre jeweiligen Dienste (z. B. Social-Plattformen für den Notifier, Google Translate für Übersetzungen); "
                "geteilt werden nur die für die Funktion nötigen Daten.\n\n"
                "**7. Änderungen**\n"
                f"Wesentliche Änderungen werden im Support-Server angekündigt: {SUPPORT_SERVER}"
            ),

            "terms_title": f"{get_emoji('icon_important')} Nutzungsbedingungen",
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
                "**7. Haftungsausschluss**\n"
                "Niko und sein Betreiber haften nicht für direkte oder indirekte Schäden durch die Nutzung des Bots.\n\n"
                f"**8. Kontakt:** {SUPPORT_SERVER}"
            ),

            "community_title": f"{get_emoji('icon_users')} Community-Richtlinie",
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
            "privacy_title": f"{get_emoji('icon_important')} Política de Privacidad",
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
                "**5. Tus derechos**\n"
                "Puedes solicitar la eliminación de todos tus datos contactando al operador del bot "
                f"en el servidor de soporte: {SUPPORT_SERVER}\n\n"
                "**6. Servicios de terceros**\n"
                "Cuando la función de IA está activada, tu mensaje y un contexto breve anonimizado se envían "
                "a la API de OpenAI. Se aplica la política de privacidad de OpenAI: https://openai.com/policies/privacy-policy\n"
                "Otras funciones pueden contactar a sus respectivos servicios (p. ej. plataformas sociales para el notificador, Google Translate para traducciones); "
                "solo se comparte lo mínimo necesario para la función.\n\n"
                "**7. Cambios**\n"
                f"Los cambios importantes se anunciarán en el servidor de soporte: {SUPPORT_SERVER}"
            ),

            "terms_title": f"{get_emoji('icon_important')} Términos de Servicio",
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
                "**7. Limitación de responsabilidad**\n"
                "Niko y su operador no son responsables de daños directos o indirectos derivados del uso del bot.\n\n"
                f"**8. Contacto:** {SUPPORT_SERVER}"
            ),

            "community_title": f"{get_emoji('icon_users')} Política de Comunidad",
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

# Cafe personality mirrors normal — same legal text, wrapped with cozy framing
MESSAGES["cafe"] = MESSAGES["normal"]

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
        icon = get_emoji("icon_important")
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
