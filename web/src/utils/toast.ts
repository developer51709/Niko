import toast from "react-hot-toast";

/**
 * Success and failure messages for the whole app.
 *
 * The dashboard used to print each result as small text inside the card that
 * produced it — above the panel, or in the settings footer — so the same
 * "Saved." message appeared in a different place on every tab. These helpers
 * route those messages through the single `<ToastHost />` stack instead.
 *
 * Pass an `id` when a surface can report the same thing repeatedly (a save
 * button, a per-account row): the new toast replaces the previous one, which is
 * what the old single status line did, instead of stacking duplicates.
 */
/**
 * Show the loading state react-hot-toast ships for work in progress.
 *
 * Calling this with the same `id` the result will use turns the spinner into
 * the outcome in place (`toast.loading` → `toast.success` / `toast.error`),
 * which is the recommended pattern from the package docs:
 * https://react-hot-toast.com/docs/toast#loading-state
 */
export function notifyLoading(message: string, id?: string) {
  toast.loading(message, { id });
}

export function notifySuccess(message: string, id?: string) {
  toast.success(message, { id });
}

export function notifyError(message: string, id?: string) {
  toast.error(message, { id });
}

/** Clear queued messages, for a view that reloads from scratch. */
export function clearToasts(id?: string) {
  toast.dismiss(id);
}
