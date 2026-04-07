# V.I.T.A.L Wiki Schema

## Domain
Voice health checkup for burnout detection using Apple HealthKit + voice biomarkers. Alan x Mistral hackathon project.

## Conventions
- File names: lowercase, hyphens (e.g., `hrv-biomarkers.md`)
- Every page has YAML frontmatter (title, created, updated, type, tags, sources)
- Use `[[wikilinks]]` for internal links (min 2 per page)
- Update `updated` date when modifying pages
- Add new pages to `index.md`
- Log all actions in `log.md`

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query
tags: [from taxonomy]
sources: [raw/path/to/source.md]
---
```

## Tag Taxonomy
**Metrics:** metric, biomarker, hrv, sleep, heart-rate, voice-biomarker
**Research:** burnout, stress, detection, clinical-study, paper
**Technical:** healthkit, api, ios, python, fastapi, mistral, voxtral
**Compliance:** rgpd, samd, hds, privacy, regulation
**Project:** vital, hackathon, alan, implementation

## Page Thresholds
- Create page when entity/concept appears in 2+ sources OR central to V.I.T.A.L
- Split pages over 200 lines
- Archive superseded content to `_archive/`

## Update Policy
New info conflicts with existing? Note both positions with dates/sources. Flag for review.
