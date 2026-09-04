# CLAUDE.md

## Project: شیطان بزرگ — The Great Devil

Jekyll static site at **https://thegreatdevil.com** — documenting US interventions in Iran's internal affairs.

**GitHub repo:** https://github.com/aminsaedi/thegreatdevil  
**Local working dir:** /home/amin/w/thegreatdevil

## Structure

- `_events/*.md` — Event data files (one per historical event)
- `_layouts/default.html` — Main HTML template (Liquid)
- `assets/style.scss` — All styles (Sass, compiled by Jekyll)
- `index.html` — Homepage template that loops over `site.events`
- `_config.yml` — Jekyll configuration

## Adding Events

Create a new file in `_events/` with this front matter:

```yaml
---
title: "Event title in Farsi"
year: "Year display string"
order: 1                  # REQUIRED — display order within the era (chronological, unique per era_id)
era_id: era-XXXX          # Links to era section anchor
era_title: "Era title"
era_range: "Era subtitle"
era_label: "Short nav label"
category: military        # coup|sanction|military|cyber|diplo|intel
category_label: "فارسی label"
featured: false           # true = spans 2 rows in grid
image: "/assets/images/events/name.jpg"   # optional
description: "One-sentence summary for cards and meta tags"
sources:                  # REQUIRED — cite a specific article URL, never a site homepage
  - title: "Source title"
    url: "https://example.com/article"
    publisher: "Publisher"
    year: 2026
    type: news            # news|official|academic|ngo|reference
    type_label: "فارسی label"
---
Event description in Farsi here.
```

`index.html` sorts events within each era by `order`, so every event file must have one.

## Build & Deploy

GitHub Actions workflow at `.github/workflows/deploy.yml` builds with Jekyll and deploys to GitHub Pages on every push to `main`.

## Local Development

```bash
bundle install
bundle exec jekyll serve
```
