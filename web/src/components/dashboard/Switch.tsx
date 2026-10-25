import { forwardRef, useState, type ChangeEvent, type InputHTMLAttributes, type ReactNode } from "react";
import { Check, X } from "lucide-react";

/**
 * Material Design 3 switch.
 *
 * Adapted from the 21st.dev M3 switch to this dashboard's plain-CSS system
 * (there is no Tailwind/shadcn here): the spring track, morphing handle, press
 * halo, and optional state icons are reproduced with the tokens in
 * `switch.css`. The hidden checkbox keeps native keyboard, form, and screen
 * reader behaviour.
 */
export interface SwitchProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "size" | "onChange" | "type"> {
  /** Controlled value. Omit to let the switch track itself. */
  checked?: boolean;
  defaultChecked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  size?: "default" | "sm";
  variant?: "primary" | "destructive";
  showIcons?: boolean;
  checkedIcon?: ReactNode;
  uncheckedIcon?: ReactNode;
}

export const Switch = forwardRef<HTMLInputElement, SwitchProps>(function Switch(
  {
    className,
    size = "default",
    variant = "primary",
    checked,
    defaultChecked,
    onCheckedChange,
    showIcons = false,
    checkedIcon,
    uncheckedIcon,
    disabled,
    ...props
  },
  ref,
) {
  const [uncontrolled, setUncontrolled] = useState(defaultChecked ?? false);
  const [pressed, setPressed] = useState(false);
  const [hovered, setHovered] = useState(false);
  const isControlled = checked !== undefined;
  const isChecked = isControlled ? checked : uncontrolled;

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (disabled) return;
    const next = event.target.checked;
    if (!isControlled) setUncontrolled(next);
    onCheckedChange?.(next);
  };

  const classes = [
    "m3-switch",
    size === "sm" ? "is-small" : "",
    variant === "destructive" ? "is-destructive" : "",
    isChecked ? "is-checked" : "",
    disabled ? "is-disabled" : "",
    hovered && !disabled ? "is-hovered" : "",
    pressed && !disabled ? "is-pressed" : "",
    className ?? "",
  ]
    .filter(Boolean)
    .join(" ");

  const iconSize = size === "sm" ? 10 : 14;

  return (
    <label
      className={classes}
      onPointerDown={() => !disabled && setPressed(true)}
      onPointerUp={() => setPressed(false)}
      onPointerCancel={() => setPressed(false)}
      onPointerLeave={() => {
        setPressed(false);
        setHovered(false);
      }}
      onPointerEnter={() => !disabled && setHovered(true)}
    >
      <input
        {...props}
        ref={ref}
        type="checkbox"
        className="m3-switch-input"
        checked={isChecked}
        disabled={disabled}
        onChange={handleChange}
      />
      <span className="m3-switch-track" aria-hidden="true">
        <span className="m3-switch-halo" />
        <span className="m3-switch-handle">
          {showIcons && (
            <>
              <span className="m3-switch-icon m3-switch-icon-on">
                {checkedIcon ?? <Check size={iconSize} strokeWidth={4} />}
              </span>
              <span className="m3-switch-icon m3-switch-icon-off">
                {uncheckedIcon ?? <X size={iconSize} strokeWidth={4} />}
              </span>
            </>
          )}
        </span>
      </span>
    </label>
  );
});
