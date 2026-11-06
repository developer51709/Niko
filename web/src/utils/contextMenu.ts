/**
 * Element-specific rows for the site's context menu.
 *
 * The menu is mounted once, above every page, so it cannot reach into the state
 * of the components it is opened on. Instead a component that owns an element
 * with actions of its own registers a resolver: when the menu opens it asks
 * every registered resolver what the pressed element has to offer, and draws
 * those rows above the page-wide ones.
 *
 * A resolver answers `null` for everything it does not own, so any number of
 * them can be registered at the same time and each one stays with the component
 * whose state it reads.
 */

/** One row contributed by a component, drawn exactly like the menu's own rows. */
export type ContextMenuExtra = {
  /** Unique across the whole menu: it also becomes the row's element id. */
  key: string;
  label: string;
  /** A name from `Icon`'s map. */
  icon: string;
  action: () => void;
};

type Resolver = (target: Element) => ContextMenuExtra[] | null;

const resolvers = new Set<Resolver>();

/**
 * Teach the context menu about one element. Returns the unregister function to
 * call on unmount, or before registering again with newer state.
 */
export function registerContextMenuExtras(resolver: Resolver) {
  resolvers.add(resolver);
  return () => {
    resolvers.delete(resolver);
  };
}

/** Every registered component's rows for the element that was pressed. */
export function contextMenuExtras(target: Element | null): ContextMenuExtra[] {
  if (!target) return [];
  const extras: ContextMenuExtra[] = [];
  for (const resolver of resolvers) {
    const rows = resolver(target);
    if (rows?.length) extras.push(...rows);
  }
  return extras;
}
