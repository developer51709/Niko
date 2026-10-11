import type { ChangeEvent } from "react";
import { Check, X } from "lucide-react";
import type { GuildResources } from "../../types";

type Role = GuildResources["roles"][number];

type Props = {
  roles: Role[];
  value: string | string[];
  onChange: (value: string | string[]) => void;
  multiple?: boolean;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  ariaLabel?: string;
};

export function RoleSelect({ roles, value, onChange, multiple = false, placeholder = "Choose a role", required, disabled, ariaLabel }: Props) {
  const selected = (Array.isArray(value) ? value : [value]).map(String).filter(Boolean);
  const knownIds = new Set(roles.map((role) => String(role.id)));
  const options = [
    ...selected
      .filter((id, index) => !knownIds.has(id) && selected.indexOf(id) === index)
      .map((id) => ({ id, name: `Unavailable role (${id})` })),
    ...roles,
  ];
  const roleFor = (id: string) => options.find((role) => String(role.id) === id);
  const handleChange = (event: ChangeEvent<HTMLSelectElement>) => {
    onChange(multiple
      ? Array.from(event.currentTarget.selectedOptions, (option) => option.value)
      : event.currentTarget.value);
  };
  const remove = (id: string) => onChange(selected.filter((selectedId) => selectedId !== id));

  return <div className={`role-select${multiple ? " role-select-multiple" : ""}`}>
    <span className="role-select-control">
      <select
        value={multiple ? selected : selected[0] || ""}
        onChange={handleChange}
        multiple={multiple}
        required={required}
        disabled={disabled}
        aria-label={ariaLabel}
        size={multiple ? Math.min(Math.max(roles.length + options.length - roles.length, 3), 7) : undefined}
      >
        {!multiple && <option value="">{placeholder}</option>}
        {options.map((role) => <option value={String(role.id)} key={role.id}>@{role.name}</option>)}
      </select>
      {!multiple && <span className="role-select-chevron" aria-hidden="true">⌄</span>}
    </span>
    {multiple && selected.length > 0 && <div className="role-select-selected" aria-label={`${selected.length} selected roles`}>
      {selected.map((id) => <span className="role-select-chip" key={id}><Check size={12} aria-hidden="true" /> @{roleFor(id)?.name || `Role ${id}`}<button type="button" onClick={() => remove(id)} aria-label={`Remove @${roleFor(id)?.name || `role ${id}`}`} disabled={disabled}><X size={12} aria-hidden="true" /></button></span>)}
    </div>}
  </div>;
}
