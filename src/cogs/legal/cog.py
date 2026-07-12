"""
Legal cog — /legal privacy and /legal terms
Trilingual EN/DE/ES, cv2 LayoutView, normal/cafe personalities.
"""

import discord
from discord.ext import commands
from config.emojis import get_emoji
from utils.i18n import make_msg

SUPPORT = "https://discord.gg/UfDBUGcKqY"
EFFECTIVE_DATE = "2025-01-01"

MESSAGES = {
    "normal": {
        "en": {
            # ── Privacy ──────────────────────────────────────────────
            "privacy_title": f"{get_emoji('icon_important')} Privacy Policy",
            "privacy_body": (
                "**Effective date:** " + EFFECTIVE_DATE + "\n\n"
                "**1. What we collect**\n"
                "Niko stores only what is strictly necessary to provide its features:\n"
                "• **User IDs** — to link economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings to you.\n"
                "• **Server IDs** — to keep per-server configuration (moderation, leveling, tickets, automod, etc.).\n"
                "• **Message content** — read in real time for AI replies, automod, snipe, highlights, and leveling XP; "
                "not stored permanently except for AI conversation history (last 3 exchanges, per-user) and snipe cache (last deleted/edited message per channel, cleared on restart).\n"
                "• **User presence & status** — read to support member-list and bot-status features; not stored.\n"
                "• **Voice state** — used only during active music or VoiceMaster sessions; not stored.\n\n"
                "**2. How we use it**\n"
                "All data is used exclusively to run Niko's features within Discord. "
                "We never sell, share, or transfer your data to third parties.\n\n"
                "**3. Storage & security**\n"
                "Data is stored in JSON files and a local SQLite database on the server hosting Niko. "
                "No cloud database or external analytics service is used.\n\n"
                "**4. Data retention**\n"
                "Economy, leveling, and configuration data persist until you or a server admin removes it. "
                "AI conversation history is capped at your last 3 exchanges and is automatically overwritten. "
                "You may erase your own AI memory at any time with `/clearhistory`.\n\n"
                "**5. Your rights**\n"
                "You may request deletion of all data associated with your User ID at any time by contacting "
                f"the bot owner in the support server: {SUPPORT}\n\n"
                "**6. Third-party AI**\n"
                "When the AI feature is enabled, your message and a short anonymised context are sent to "
                "OpenAI's API to generate a reply. OpenAI's privacy policy applies to that data: https://openai.com/policies/privacy-policy\n\n"
                "**7. Changes**\n"
                "Material changes to this policy will be announced in the support server. "
                "Continued use of Niko after a change constitutes acceptance.\n\n"
                f"-# Questions? Join the support server: {SUPPORT}"
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
                f"For questions or concerns: {SUPPORT}\n\n"
                f"-# By interacting with Niko you confirm you have read and agreed to these Terms."
            ),

            "footer_privacy": f"Full policy: {SUPPORT}",
            "footer_terms":   f"Support & contact: {SUPPORT}",
        },

        "de": {
            "privacy_title": f"{get_emoji('icon_important')} Datenschutzerklärung",
            "privacy_body": (
                "**Gültig ab:** " + EFFECTIVE_DATE + "\n\n"
                "**1. Was wir speichern**\n"
                "Niko speichert nur das Nötigste für seine Funktionen:\n"
                "• **Nutzer-IDs** — zur Verknüpfung von Wirtschaft, XP, Erinnerungen, Geburtstagen, Highlights, KI-Gedächtnis und Verwarnungen.\n"
                "• **Server-IDs** — für serverspezifische Konfigurationen (Moderation, Leveling, Tickets, AutoMod usw.).\n"
                "• **Nachrichteninhalte** — werden für KI-Antworten, AutoMod, Snipe, Highlights und Leveling-XP in Echtzeit gelesen; "
                "dauerhaft gespeichert wird nur der KI-Gesprächsverlauf (letzte 3 Austausche pro Nutzer) sowie der Snipe-Cache (letzte gelöschte/bearbeitete Nachricht pro Kanal, beim Neustart gelöscht).\n"
                "• **Präsenz & Status** — für Mitgliederlisten- und Bot-Status-Funktionen gelesen; nicht gespeichert.\n"
                "• **Voice-Status** — nur während aktiver Musik- oder VoiceMaster-Sitzungen; nicht gespeichert.\n\n"
                "**2. Verwendung**\n"
                "Alle Daten werden ausschließlich für Nikos Funktionen auf Discord genutzt. "
                "Wir verkaufen, teilen oder übertragen deine Daten nicht an Dritte.\n\n"
                "**3. Speicherung & Sicherheit**\n"
                "Daten werden in JSON-Dateien und einer lokalen SQLite-Datenbank auf dem Hosting-Server gespeichert. "
                "Es werden keine Cloud-Datenbanken oder externen Analysedienste genutzt.\n\n"
                "**4. Aufbewahrung**\n"
                "Wirtschafts-, Leveling- und Konfigurationsdaten bleiben gespeichert, bis du oder ein Server-Admin sie entfernst. "
                "Das KI-Gesprächsgedächtnis ist auf die letzten 3 Austausche begrenzt und wird automatisch überschrieben. "
                "Dein KI-Gedächtnis kannst du jederzeit mit `/clearhistory` löschen.\n\n"
                "**5. Deine Rechte**\n"
                "Du kannst jederzeit die Löschung aller mit deiner Nutzer-ID verknüpften Daten verlangen. "
                f"Wende dich dafür an den Bot-Betreiber im Support-Server: {SUPPORT}\n\n"
                "**6. KI-Drittanbieter**\n"
                "Wenn die KI-Funktion aktiviert ist, werden deine Nachricht und ein kurzer anonymisierter Kontext "
                "an die OpenAI-API gesendet. Es gilt OpenAIs Datenschutzrichtlinie: https://openai.com/policies/privacy-policy\n\n"
                "**7. Änderungen**\n"
                f"Wesentliche Änderungen werden im Support-Server angekündigt: {SUPPORT}"
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
                f"**8. Kontakt:** {SUPPORT}"
            ),

            "footer_privacy": f"Vollständige Richtlinie: {SUPPORT}",
            "footer_terms":   f"Support & Kontakt: {SUPPORT}",
        },

        "es": {
            "privacy_title": f"{get_emoji('icon_important')} Política de Privacidad",
            "privacy_body": (
                "**Fecha de vigencia:** " + EFFECTIVE_DATE + "\n\n"
                "**1. Qué recopilamos**\n"
                "Niko almacena solo lo estrictamente necesario para sus funciones:\n"
                "• **IDs de usuario** — para vincular economía, XP, recordatorios, cumpleaños, highlights, memoria de IA y advertencias.\n"
                "• **IDs de servidor** — para configuraciones por servidor (moderación, leveling, tickets, automod, etc.).\n"
                "• **Contenido de mensajes** — leído en tiempo real para respuestas de IA, automod, snipe, highlights y XP; "
                "almacenado permanentemente solo el historial de conversación de IA (últimos 3 intercambios por usuario) y caché de snipe (último mensaje borrado/editado por canal, se borra al reiniciar).\n"
                "• **Presencia y estado** — leído para funciones de lista de miembros; no almacenado.\n"
                "• **Estado de voz** — solo durante sesiones activas de música o VoiceMaster; no almacenado.\n\n"
                "**2. Uso**\n"
                "Todos los datos se usan exclusivamente para las funciones de Niko en Discord. "
                "Nunca vendemos, compartimos ni transferimos tus datos a terceros.\n\n"
                "**3. Almacenamiento y seguridad**\n"
                "Los datos se guardan en archivos JSON y una base de datos SQLite local. "
                "No se usan bases de datos en la nube ni servicios de análisis externos.\n\n"
                "**4. Retención de datos**\n"
                "Los datos de economía, leveling y configuración persisten hasta que tú o un administrador los elimine. "
                "El historial de conversación de IA está limitado a los últimos 3 intercambios. "
                "Puedes borrar tu memoria de IA en cualquier momento con `/clearhistory`.\n\n"
                "**5. Tus derechos**\n"
                "Puedes solicitar la eliminación de todos tus datos contactando al operador del bot "
                f"en el servidor de soporte: {SUPPORT}\n\n"
                "**6. IA de terceros**\n"
                "Cuando la función de IA está activada, tu mensaje y un contexto breve anonimizado se envían "
                "a la API de OpenAI. Se aplica la política de privacidad de OpenAI: https://openai.com/policies/privacy-policy\n\n"
                "**7. Cambios**\n"
                f"Los cambios importantes se anunciarán en el servidor de soporte: {SUPPORT}"
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
                f"**8. Contacto:** {SUPPORT}"
            ),

            "footer_privacy": f"Política completa: {SUPPORT}",
            "footer_terms":   f"Soporte y contacto: {SUPPORT}",
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
        description="Privacy policy and terms of service for Niko",
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
                    "Use `/legal privacy` to read the **Privacy Policy** or "
                    "`/legal terms` to read the **Terms of Service**."
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


async def setup(bot: commands.Bot):
    await bot.add_cog(LegalCog(bot))
