import { Icon } from "./Icon";
import type { DocCategory, DocSection } from "../types";

interface DocFiltersProps {
  selectedCategory: DocCategory | "";
  onSelectCategory: (category: DocCategory | "") => void;
  sections: DocSection[];
  allCategoriesLabel?: string;
}

export function DocFilters({
  selectedCategory,
  onSelectCategory,
  sections,
  allCategoriesLabel = "All Categories",
}: DocFiltersProps) {
  return (
    <div className="doc-filters">
      <div className="filter-tabs" role="tablist" aria-label="Filter by category">
        <button
          role="tab"
          aria-selected={selectedCategory === ""}
          className={`filter-tab ${selectedCategory === "" ? "active" : ""}`}
          onClick={() => onSelectCategory("")}
        >
          {allCategoriesLabel}
        </button>
        {sections.map((section) => (
          <button
            key={section.id}
            role="tab"
            aria-selected={selectedCategory === section.id}
            className={`filter-tab ${selectedCategory === section.id ? "active" : ""}`}
            onClick={() => onSelectCategory(section.id as DocCategory)}
          >
            <Icon name={section.icon as "icon_home" | "icon_settings" | "icon_economy" | "icon_leveling" | "icon_moderation" | "icon_automod" | "icon_heart" | "icon_utility" | "icon_bot" | "icon_ai" | "icon_lightbulb"} size={14} />
            <span>{section.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}