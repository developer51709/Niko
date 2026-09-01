import {
  ArrowRight,
  BarChart3,
  BookOpen,
  ExternalLink,
  LayoutGrid,
  LockKeyhole,
  Menu,
  Settings,
  Shield,
  Sparkles,
  Terminal,
  Users,
  X,
  type LucideIcon,
} from "lucide-react";

const icons: Record<string, LucideIcon> = {
  arrow: ArrowRight,
  grid: LayoutGrid,
  terminal: Terminal,
  chart: BarChart3,
  shield: Shield,
  spark: Sparkles,
  users: Users,
  settings: Settings,
  book: BookOpen,
  external: ExternalLink,
  menu: Menu,
  close: X,
  lock: LockKeyhole,
};

export function Icon({ name }: { name: string }) {
  const Glyph = icons[name] || LayoutGrid;
  return <Glyph className="icon" aria-hidden="true" focusable="false" strokeWidth={1.8} />;
}