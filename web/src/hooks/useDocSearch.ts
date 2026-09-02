import { useState, useMemo, useCallback } from "react";
import type { DocPage, DocCategory, SearchFilters, SearchResult } from "../types";
import { DOCS } from "../data/docs";

// ── Search hook ───────────────────────────────────────────────────────────────

export function useDocSearch() {
  const [filters, setFilters] = useState<SearchFilters>({
    query: "",
    category: "",
    tags: [],
  });

  // Update query
  const setQuery = useCallback((query: string) => {
    setFilters((f) => ({ ...f, query: query.toLowerCase(), tags: [] }));
  }, []);

  // Update category filter
  const setCategory = useCallback((category: DocCategory | "") => {
    setFilters((f) => ({ ...f, category, tags: [] }));
  }, []);

  // Toggle a tag filter
  const toggleTag = useCallback((tag: string) => {
    setFilters((f) => {
      const tags = f.tags.includes(tag)
        ? f.tags.filter((t) => t !== tag)
        : [...f.tags, tag];
      return { ...f, tags, query: "" };
    });
  }, []);

  // Clear all filters
  const clearFilters = useCallback(() => {
    setFilters({ query: "", category: "", tags: [] });
  }, []);

  // Perform search
  const results = useMemo(() => {
    const { query, category, tags } = filters;

    if (!query && !category && tags.length === 0) {
      return DOCS.map((page) => ({
        page,
        score: 1,
        highlights: [],
      }));
    }

    const searchResults: SearchResult[] = [];

    for (const page of DOCS) {
      // Category filter
      if (category && page.category !== category) continue;

      // Tag filter
      if (tags.length > 0 && !tags.some((t) => page.tags.includes(t))) continue;

      // Query search
      if (query) {
        const score = calculateScore(page, query);
        if (score === 0) continue;

        const highlights = extractHighlights(page, query);
        searchResults.push({ page, score, highlights });
      } else {
        searchResults.push({ page, score: 1, highlights: [] });
      }
    }

    // Sort by score (highest first), then by order
    searchResults.sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      return a.page.order - b.page.order;
    });

    return searchResults;
  }, [filters]);

  const hasActiveFilters = filters.query !== "" || filters.category !== "" || filters.tags.length > 0;

  return {
    filters,
    setQuery,
    setCategory,
    toggleTag,
    clearFilters,
    results,
    hasActiveFilters,
    resultCount: results.length,
  };
}

// ── Scoring function ──────────────────────────────────────────────────────────

function calculateScore(page: DocPage, query: string): number {
  let score = 0;

  const q = query.toLowerCase();

  // Exact title match (highest weight)
  if (page.title.toLowerCase() === q) {
    score += 100;
  }
  // Title contains query
  else if (page.title.toLowerCase().includes(q)) {
    score += 50;
  }

  // Excerpt contains query
  if (page.excerpt.toLowerCase().includes(q)) {
    score += 25;
  }

  // Content contains query
  if (page.content.toLowerCase().includes(q)) {
    score += 10;
  }

  // Tag matches
  for (const tag of page.tags) {
    if (tag.toLowerCase().includes(q)) {
      score += 15;
    }
  }

  // Category match
  if (page.category.toLowerCase().includes(q)) {
    score += 5;
  }

  return score;
}

// ── Highlight extraction ──────────────────────────────────────────────────────

function extractHighlights(page: DocPage, query: string): string[] {
  const highlights: string[] = [];
  const q = query.toLowerCase();
  const maxHighlights = 3;

  // Check title
  if (page.title.toLowerCase().includes(q)) {
    highlights.push(page.title);
    if (highlights.length >= maxHighlights) return highlights;
  }

  // Check excerpt
  if (page.excerpt.toLowerCase().includes(q)) {
    highlights.push(page.excerpt);
    if (highlights.length >= maxHighlights) return highlights;
  }

  // Check content for sentences containing query
  const contentLines = page.content.split("\n").filter((line) => line.trim());
  for (const line of contentLines) {
    if (line.toLowerCase().includes(q)) {
      // Clean up the line for display
      const cleanLine = line.replace(/#{1,6}\s?/g, "").trim();
      if (cleanLine.length > 10) {
        highlights.push(cleanLine);
        if (highlights.length >= maxHighlights) break;
      }
    }
  }

  return highlights;
}

// ── Tag cloud helper ──────────────────────────────────────────────────────────

export function useTagCloud() {
  const tags = useMemo(() => {
    const tagCounts: Record<string, number> = {};
    DOCS.forEach((doc) => {
      doc.tags.forEach((tag) => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    });
    return Object.entries(tagCounts)
      .map(([tag, count]) => ({ tag, count }))
      .sort((a, b) => b.count - a.count);
  }, []);

  return tags;
}