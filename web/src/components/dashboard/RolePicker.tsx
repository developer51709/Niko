import { Select, type SelectOption } from "./Select";
import type { GuildResources } from "../../types";

type Role = GuildResources["roles"][number];

/** Discord's grey, used for roles without a colour. */
const DEFAULT_ROLE_COLOR = "#99aab5";

/** The role's dot fill: one colour, a gradient for gradient roles, grey otherwise. */
function roleDotStyle(colors?: string[] | null) {
  const stops = (colors || []).filter(Boolean);
  if (stops.length === 0) return { background: DEFAULT_ROLE_COLOR };
  if (stops.length === 1) return { background: stops[0] };
  return { background: `linear-gradient(90deg, ${stops.join(", ")})` };
}

function RoleGlyph({ colors }: { colors?: string[] | null }) {
  return <span className="role-picker-dot" style={roleDotStyle(colors)} aria-hidden="true" />;
}

type Props = {
  roles: Role[];
  value: string;
  onChange: (value: string) => void;
  /** Label for the empty choice; pass null to make a role mandatory. */
  placeholder?: string | null;
  ariaLabel?: string;
  disabled?: boolean;
  id?: string;
};

/** A role picker: the shared `Select`, with a dot in each role's colour or gradient. */
export function RolePicker({ roles, value, onChange, placeholder = "Choose a role", ariaLabel, disabled, id }: Props) {
  const options: SelectOption[] = roles.map((role) => ({
    value: String(role.id),
    label: role.name,
    glyph: <RoleGlyph colors={role.colors} />,
  }));

  return <Select
    options={options}
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    placeholderGlyph={placeholder === null ? undefined : <span className="role-picker-glyph" aria-hidden="true">@</span>}
    unknownOption={(saved) => ({ value: saved, label: `Saved role · ${saved}`, glyph: <RoleGlyph /> })}
    ariaLabel={ariaLabel}
    disabled={disabled}
    id={id}
  />;
}
