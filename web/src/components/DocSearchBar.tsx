import { useState, useRef, useEffect } from "react";
import { Icon } from "./Icon";

interface DocSearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  onFocus?: () => void;
  onBlur?: () => void;
}

export function DocSearchBar({
  value,
  onChange,
  placeholder = "Search documentation...",
  onFocus,
  onBlur,
}: DocSearchBarProps) {
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

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      inputRef.current?.blur();
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
          placeholder={placeholder}
          className="search-input"
          aria-label="Search documentation"
        />
        <kbd className="search-shortcut">
          <span className="shortcut-key">⌘</span>K
        </kbd>
      </div>
      <div className="search-hint">
        Press <kbd>⌘K</kbd> to focus search
      </div>
    </div>
  );
}