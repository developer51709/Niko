import { useState, useRef, useEffect } from "react";
import { Icon } from "./Icon";
import { useStrings } from "../i18n";

const IS_APPLE = typeof navigator !== "undefined" && /Mac|iPhone|iPad|iPod/.test(navigator.userAgent);

interface DocSearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  /** Screen-reader copy, passed in so the page's catalogue owns the wording. */
  ariaLabel?: string;
  clearLabel?: string;
  /** Shared copy is the fallback: a page that passes its own wording wins. */
  onFocus?: () => void;
  onBlur?: () => void;
  onEnter?: () => void;
}

export function DocSearchBar({
  value,
  onChange,
  placeholder,
  ariaLabel,
  clearLabel,
  onFocus,
  onBlur,
  onEnter,
}: DocSearchBarProps) {
  const { t } = useStrings("shared");
  const resolvedPlaceholder = placeholder ?? t("docs.searchPlaceholder");
  const resolvedAriaLabel = ariaLabel ?? t("docs.searchAria");
  const resolvedClearLabel = clearLabel ?? t("docs.searchClear");
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleFocus = () => {
    setIsFocused(true);
    setIsExpanded(true);
    onFocus?.();
  };

  const handleBlur = () => {
    setIsFocused(false);
    // Delay closing to allow click events on suggestions
    setTimeout(() => setIsExpanded(false), 200);
    onBlur?.();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Escape") {
      inputRef.current?.blur();
    } else if (e.key === "Enter") {
      onEnter?.();
      setIsExpanded(false);
    }
  };

  return (
    <div className={`doc-search-bar ${isExpanded ? "expanded" : ""}`}>
      <div className="search-input-wrapper">
        <Icon name="search" className="search-icon" />
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder={resolvedPlaceholder}
          className="search-input"
          aria-label={resolvedAriaLabel}
        />
        {!!value && (
          <button
            className="search-clear"
            type="button"
            onClick={() => {
              onChange("");
              inputRef.current?.focus();
            }}
            aria-label={resolvedClearLabel}
          >
            <Icon name="close" size={12} />
          </button>
        )}
        <kbd className="search-shortcut">
          <span className="shortcut-key">{IS_APPLE ? "⌘" : "Ctrl"}</span>{IS_APPLE ? "K" : "+K"}
        </kbd>
      </div>
    </div>
  );
}