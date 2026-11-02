import type { ChangeEvent } from "react";
import { Check, X } from "lucide-react";
import type { GuildResources } from "../../types";
import { RolePicker } from "./RolePicker";

type Role = GuildResources["roles"][number];

type Props = {
  roles: Role[];
  value: string | string[];
  onChange: (value: string | string[]) => void;
  multiple?: boolean;
  placeholder?: string;
  disabled?: boolean;
  ariaLabel?: string;
};

/**
 * A role field. Picking one role is `RolePicker`; picking several is a native
 * multi-select with chips, since only a listbox with several choices at once
 * (and a chip per chosen role) can show a set that large.
 */
export function RoleSelect({ roles, value, onChange, multiple = false, placeholder = "Choose a role", disabled, ariaLabel }: Props) {
  if (!multiple) return <RolePicker
    roles={roles}
    value={String(value || "")}
    onChange={onChange}
    placeholder={placeholder}
    ariaLabel={ariaLabel}
    disabled={disabled}
  />;

  const selected = (Array.isArray(value) ? value : []).map(String).filter(Boolean);
  const knownIds = new Set(roles.map((role) => String(role.id)));
  const options = [
    ...selected
      .filter((id, index) => !knownIds.has(id) && selected.indexOf(id) === index)
      .map((id) => ({ id, name: `Unavailable role (${id})` })),
    ...roles,
  ];
  const roleFor = (id: string) => options.find((role) => String(role.id) === id);
  const handleChange = (event: ChangeEvent<HTMLSelectElement>) => {
    onChange(Array.from(event.currentTarget.selectedOptions, (option) => option.value));
  };
  const remove = (id: string) => onChange(selected.filter((selectedId) => selectedId !== id));

  return <div className="role-select role-select-multiple">
    <span className="role-select-control">
      <select
        value={selected}
        onChange={handleChange}
        multiple
        disabled={disabled}
        aria-label={ariaLabel}
        size={Math.min(Math.max(options.length, 3), 7)}
      >
        {options.map((role) => <option value={String(role.id)} key={role.id}>@{role.name}</option>)}
      </select>
    </span>
    {selected.length > 0 && <div className="role-select-selected" aria-label={`${selected.length} selected roles`}>
      {selected.map((id) => <span className="role-select-chip" key={id}><Check size={12} aria-hidden="true" /> @{roleFor(id)?.name || `Role ${id}`}<button type="button" onClick={() => remove(id)} aria-label={`Remove @${roleFor(id)?.name || `role ${id}`}`} disabled={disabled}><X size={12} aria-hidden="true" /></button></span>)}
    </div>}
  </div>;
}
