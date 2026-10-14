import {
  ArrowRight,
  AlertTriangle,
  BarChart3,
  BookOpen,
  Bot,
  Brush,
  Check,
  ClipboardList,
  Coins,
  DoorOpen,
  Gauge,
  Headset,
  Layers3,
  ExternalLink,
  LayoutGrid,
  Link2,
  LockKeyhole,
  LogOut,
  Menu,
  MessageCircle,
  Minus,
  Paintbrush,
  Plus,
  RefreshCw,
  Search,
  Settings,
  Shield,
  Sparkles,
  Terminal,
  TrendingUp,
  Trophy,
  Users,
  X,
  type LucideIcon,
} from "lucide-react";

const icons: Record<string, LucideIcon> = {
  arrow: ArrowRight,
  alert: AlertTriangle,
  grid: LayoutGrid,
  terminal: Terminal,
  chart: BarChart3,
  check: Check,
  shield: Shield,
  spark: Sparkles,
  users: Users,
  link: Link2,
  settings: Settings,
  book: BookOpen,
  external: ExternalLink,
  menu: Menu,
  message: MessageCircle,
  close: X,
  minus: Minus,
  plus: Plus,
  paint: Paintbrush,
  refresh: RefreshCw,
  lock: LockKeyhole,
  logout: LogOut,
  search: Search,
  guild_overview: Gauge,
  guild_leveling: TrendingUp,
  guild_economy: Coins,
  guild_achievements: Trophy,
  guild_moderation: Shield,
  guild_server: Layers3,
  guild_onboarding: DoorOpen,
  guild_tickets: Headset,
  guild_applications: ClipboardList,
  guild_ai: Bot,
  guild_customization: Brush,
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