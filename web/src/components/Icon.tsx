import {
  ArrowRight,
  BarChart3,
  BookOpen,
  ExternalLink,
  LayoutGrid,
  LockKeyhole,
  Menu,
  Search,
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
  search: Search,
  doc: BookOpen,
  utility: Settings,
  icon_home: LayoutGrid,
  icon_settings: Settings,
  icon_economy: BarChart3,
  icon_leveling: BarChart3,
  icon_moderation: Shield,
  icon_automod: Shield,
  icon_heart: Sparkles,
  icon_utility: Settings,
  icon_bot: Users,
  icon_ai: Sparkles,
  icon_lightbulb: Sparkles,
};

export function Icon({
  name,
  size,
  className = "",
}: {
  name: string;
  size?: number;
  className?: string;
}) {
  const Glyph = icons[name] || LayoutGrid;
  return (
    <Glyph
      className={`icon ${className}`.trim()}
      aria-hidden="true"
      focusable="false"
      strokeWidth={1.8}
      style={size ? { width: size, height: size } : undefined}
    />
  );
}