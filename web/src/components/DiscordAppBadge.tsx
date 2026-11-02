/** Discord's APP tag, with the verified tick it draws for a verified bot. */
export function DiscordAppBadge({ verified, small = false }: { verified: boolean; small?: boolean }) {
  return (
    <span className={`dc-app-badge${small ? " dc-app-badge-small" : ""}`} title={verified ? "Verified bot" : undefined}>
      {verified && (
        <svg className="dc-app-badge-check" viewBox="0 0 12 12" aria-hidden="true" focusable="false">
          <path d="M2.2 6.4 4.7 8.9 9.8 3.3" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      )}
      APP
    </span>
  );
}
