import { type ReactElement, type ReactNode, cloneElement, isValidElement, useId } from "react";
import { ChannelSelect } from "./ChannelSelect";
import { RolePicker } from "./RolePicker";
import { RoleSelect } from "./RoleSelect";
import { Select } from "./Select";

/** Children that can be pointed at with `htmlFor`. */
const LABELABLE_CONTROLS = ["input", "select", "textarea"];

/** Custom pickers that cannot take an id, so they take the label as their name. */
const NAMED_CONTROLS: ReadonlyArray<unknown> = [RoleSelect, ChannelSelect, RolePicker, Select];

/**
 * A settings field: its label, one control, and an optional hint.
 *
 * The label points at its control with `htmlFor` instead of wrapping it, so the
 * click area stays the control itself rather than the label text, the hint, and
 * the rest of the stretched grid cell. Custom pickers cannot be labelled that
 * way, so they get the field label as their accessible name instead.
 *
 * Every settings panel — public dashboard tabs and the staff workspace — uses
 * this one field, so a row behaves the same wherever it is rendered.
 */
export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  const generatedId = useId();
  const control = isValidElement(children) && typeof children.type === "string" && LABELABLE_CONTROLS.includes(children.type)
    ? children as ReactElement<{ id?: string }>
    : null;
  const picker = isValidElement(children) && NAMED_CONTROLS.includes(children.type)
    ? children as ReactElement<{ ariaLabel?: string }>
    : null;
  const controlId = control ? `${generatedId}-control` : undefined;
  return <div className="form-field">
    <label className="form-label" htmlFor={controlId}>{label}</label>
    {control ? cloneElement(control, { id: controlId }) : picker ? cloneElement(picker, { ariaLabel: picker.props.ariaLabel || label }) : children}
    {hint && <small>{hint}</small>}
  </div>;
}
