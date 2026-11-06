/**
 * The card a staff page shows while its data is on the way.
 *
 * Every staff panel used to repeat the same two elements — the spinner and one
 * line of text — inside the dashboard's empty-state panel. They all render this
 * component instead, so the loading state is written once and each page shows
 * the identical card. Its styles live in `styles/loading-card.css`.
 */
export function LoadingCard({ message }: { message: string }) {
  return (
    <div className="loading-card" role="status">
      <div className="loading-ring" aria-hidden="true" />
      <p>{message}</p>
    </div>
  );
}
