// Every badge the profile popups can draw, in one place.
//
// The keys are exactly what ``/api/discord/users/<id>`` and the exported
// transcript send, the artwork lives in ``web/public/assets`` (the HypeSquad
// houses under ``hypesquad/`` and everything else under ``badges/``), and the
// label + description are what the badge popup shows. Niko's own role badges
// are generated from the same SVGs the bot uploads as application emojis, see
// scripts/build-badge-art.mjs.

export type ProfileBadge = {
  key: string;
  src: string;
  label: string;
  description: string;
};

// Discord keeps the lower tier until the next one is reached, so only these
// month counts have their own boosting artwork.
export const BOOSTING_TIER_MONTHS = [1, 2, 3, 6, 9, 12, 15, 18, 24];

function boostingBadge(months: number): { src: string; label: string; description: string } {
  const unit = months === 1 ? "month" : "months";
  return {
    src: `/assets/badges/boosting_${months}_months.svg`,
    label: `Boosting a server for ${months} ${unit}`,
    description:
      `Boosted a server for ${months} ${unit}. The badge art upgrades at 1, 2, 3, 6, 9, 12, 15, 18 and 24 months.`,
  };
}

const CATALOG: Record<string, { src: string; label: string; description: string }> = {
  // ── Discord's own profile badges ──────────────────────────────────────────
  "staff": { src: "/assets/badges/staff.svg", label: "Discord Staff", description: "Part of the Discord team." },
  "partner": { src: "/assets/badges/partner.svg", label: "Partnered Server Owner", description: "Owns a server that is partnered with Discord." },
  "hypesquad_events": { src: "/assets/hypesquad/events.svg", label: "HypeSquad Events", description: "Helped host an official HypeSquad event." },
  "bug_hunter_level_1": { src: "/assets/badges/bug_hunter_level_1.svg", label: "Bug Hunter", description: "Reported a valid bug to Discord." },
  "hypesquad_bravery": { src: "/assets/hypesquad/bravery.svg", label: "HypeSquad Bravery", description: "Member of House Bravery." },
  "hypesquad_brilliance": { src: "/assets/hypesquad/brilliance.svg", label: "HypeSquad Brilliance", description: "Member of House Brilliance." },
  "hypesquad_balance": { src: "/assets/hypesquad/balance.svg", label: "HypeSquad Balance", description: "Member of House Balance." },
  "early_supporter": { src: "/assets/badges/early_supporter.svg", label: "Early Supporter", description: "Supported Discord before October 10, 2018." },
  "bug_hunter_level_2": { src: "/assets/badges/bug_hunter_level_2.svg", label: "Bug Hunter (Gold)", description: "Reported several valid bugs to Discord." },
  "early_verified_developer": { src: "/assets/badges/early_verified_developer.svg", label: "Early Verified Bot Developer", description: "Verified bot developer before August 19, 2020." },
  "certified_moderator": { src: "/assets/badges/certified_moderator.svg", label: "Moderator Programs Alumni", description: "Took part in Discord's Moderator Programs." },
  "supports_commands": { src: "/assets/badges/supports_commands.svg", label: "Supports Commands", description: "This app supports slash commands." },
  "active_developer": { src: "/assets/badges/active_developer.svg", label: "Active Developer", description: "Ran a slash command in the past 30 days." },
  // ── Niko's own role badges ────────────────────────────────────────────────
  "niko_owner": { src: "/assets/badges/niko_owner.svg", label: "Niko Owner", description: "Owns and runs Niko." },
  "niko_staff": { src: "/assets/badges/niko_staff.svg", label: "Niko Staff", description: "Part of the Niko team." },
  "niko_head_admin": { src: "/assets/badges/niko_head_admin.svg", label: "Head Admin", description: "Leads Niko's moderation team." },
  "niko_moderator": { src: "/assets/badges/niko_moderator.svg", label: "Moderator", description: "Keeps Niko's servers in order." },
  "niko_head_support": { src: "/assets/badges/niko_head_support.svg", label: "Head of Support", description: "Leads the Niko support team." },
  "niko_support": { src: "/assets/badges/niko_support.svg", label: "Support Team", description: "Answers tickets and helps members." },
  "niko_graphic_designer": { src: "/assets/badges/niko_graphic_designer.svg", label: "Graphic Designer", description: "Draws Niko's art and brand." },
  "niko_event_coordinator": { src: "/assets/badges/niko_event_coordinator.svg", label: "Event Coordinator", description: "Runs Niko's community events." },
  "niko_partnerships_promotions_lead": { src: "/assets/badges/niko_partnerships_promotions_lead.svg", label: "Partnerships & Promotions Lead", description: "Leads partnerships and promotions." },
  "niko_partnership_manager": { src: "/assets/badges/niko_partnership_manager.svg", label: "Partnership Manager", description: "Manages Niko's partner servers." },
  "niko_supporter": { src: "/assets/badges/niko_supporter.svg", label: "Supporter", description: "Donated to keep Niko's hosting running." },
  "niko_bug_hunter": { src: "/assets/badges/niko_bug_hunter.svg", label: "Bug Bounty Hunter", description: "Reported a bug that made Niko better." },
  "niko_partner": { src: "/assets/badges/niko_partner.svg", label: "Partner", description: "Owns a server partnered with Niko." },
};

const PROFILE_BADGES: Record<string, { src: string; label: string; description: string }> = {
  ...CATALOG,
  ...Object.fromEntries(BOOSTING_TIER_MONTHS.map((months) => [`boosting_${months}_months`, boostingBadge(months)])),
};

/** Discord's own profile badges, in the order the bot's card lists them. */
export const DISCORD_BADGE_KEYS = [
  "staff", "partner", "hypesquad_events", "bug_hunter_level_1", "hypesquad_bravery",
  "hypesquad_brilliance", "hypesquad_balance", "early_supporter", "bug_hunter_level_2",
  "early_verified_developer", "certified_moderator", "supports_commands", "active_developer",
];

/** The tiers of Discord's server-boosting badge, ascending. */
export const BOOSTING_BADGE_KEYS = BOOSTING_TIER_MONTHS.map((months) => `boosting_${months}_months`);

/** Niko's own role badges, in the order the bot's card lists them. */
export const NIKO_BADGE_KEYS = [
  "niko_owner", "niko_head_admin", "niko_moderator", "niko_head_support", "niko_graphic_designer",
  "niko_support", "niko_event_coordinator", "niko_partnerships_promotions_lead",
  "niko_partnership_manager", "niko_staff", "niko_supporter", "niko_bug_hunter", "niko_partner",
];

/** One badge by key, or ``undefined`` for a key with no artwork. */
export function profileBadge(key: string): ProfileBadge | undefined {
  const badge = PROFILE_BADGES[key];
  return badge ? { key, ...badge } : undefined;
}

/** The badges behind a list of keys, skipping the ones with no artwork. */
export function profileBadges(keys?: string[] | null): ProfileBadge[] {
  return (keys || []).map(profileBadge).filter((badge): badge is ProfileBadge => Boolean(badge));
}

/** The catalogue, grouped for the rendering lab's badge section. */
export const BADGE_GROUPS: { title: string; blurb: string; keys: string[] }[] = [
  {
    title: "Discord badges",
    blurb: "Discord's own profile badges, read from the member's public flags.",
    keys: DISCORD_BADGE_KEYS,
  },
  {
    title: "Discord boosting tiers",
    blurb: "The server-boosting badge has its own art per tier; a streak keeps the lower one until the next is reached.",
    keys: BOOSTING_BADGE_KEYS,
  },
  {
    title: "Niko badges",
    blurb: "Niko's role badges, decided in src/utils/member_badges.py and drawn from the same art the bot uploads as emojis.",
    keys: NIKO_BADGE_KEYS,
  },
];
