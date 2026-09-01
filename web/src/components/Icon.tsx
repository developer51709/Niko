export function Icon({ name }: { name: string }) {
  const paths: Record<string, string> = {
    arrow: "M5 12h14m-6-6 6 6-6 6",
    grid: "M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z",
    terminal: "m5 7 5 5-5 5m8 0h6",
    chart: "M4 19V5m0 14h16M8 16v-4m4 4V8m4 8v-7",
    shield: "M12 3 20 6v5c0 5-3.4 8.5-8 10-4.6-1.5-8-5-8-10V6z",
    spark: "m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7z",
    users: "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m7-10a4 4 0 1 0-8 0 4 4 0 0 0 8 0m7-7a4 4 0 0 1 0 7.8M22 21v-2a4 4 0 0 0-3-3.9",
    settings: "M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7m0-12v2m0 13v2m9-8h-2M5 12H3m15.4-6.4-1.4 1.4M7 17l-1.4 1.4m12.8 0L17 17M7 7 5.6 5.6",
    book: "M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22zm0 0v16",
    external: "M14 4h6v6m-1-5-8 8m-7 4V6a2 2 0 0 1 2-2h5",
    menu: "M4 6h16M4 12h16M4 18h16",
    close: "m6 6 12 12M18 6 6 18",
    lock: "M6 10h12v10H6zM8 10V7a4 4 0 0 1 8 0v3",
  };
  return (
    <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={paths[name] || paths.grid} />
    </svg>
  );
}