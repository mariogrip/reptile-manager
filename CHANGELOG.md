# Changelog

## [1.2.3] – 2026-09-19

### Fixed
- Creating an animal (and any other list/create call) failed with `502` behind Home Assistant Ingress: the frontend calls `/api/animals` (no trailing slash) while the backend only registered `/api/animals/`, so FastAPI answered `307 Temporary Redirect` — the redirect drops the ingress path prefix and Home Assistant returns `502`. All collection routes (`animals`, `feedings`, `sheddings`, `breeding`) now serve both variants directly, no redirect involved.

---

## [1.2.2] – 2025-06-04

### Fixed
- Animal detail page still showing "Alter" instead of "Age" when UI language set to English
- Label generator (sign creator) was not translated — all UI strings now fully localised (size presets, colour themes, content checkboxes, QR options, resolution selector)
- Several remaining untranslated strings in animal detail (feeding reminder label, blue phase field, tab entry counts, form buttons)

---

## [1.2.1] – 2025-06-03

### Changed
- Sex display now uses standard reptile/spider notation (1.0.0 / 0.1.0 / 0.0.1) everywhere: animal list cards, animal detail, breeding overview, family tree, and label canvas
- Form dropdowns keep readable text labels (Male/Female/Unknown) for usability

### Fixed
- `panel_admin` set to `false` — sidebar entry now visible to all HA users, not just admins
- Label canvas still showed ♂/♀ symbols instead of numeric notation
- Sex symbols in breeding cards, animal detail parent section and family tree not updated

---

## [1.2.0] – 2025-06-02

### Added
- **Origin Certificate (Herkunftsnachweis)** — print-ready PDF legal proof of origin according to § 46 BNatSchG, with seller profile saved in settings, buyer fields, origin type selection (stock / breeding / import / other), and GitHub link in the footer
- **Blank certificate mode** — generate a certificate without buyer details and date, for use at animal fairs/markets (fill in by hand)
- **Inventory export (CSV)** — all active animals as a CSV file, opens directly in Excel/LibreOffice with correct encoding (UTF-8 BOM). Includes tracking ID, species, sex, morph, husbandry conditions, weight, length
- **Sex notation** — standard reptile/spider notation (1.0.0 / 0.1.0 / 0.0.1) in PDFs
- **Quick certificate button** — 📜 button on each animal card and detail page, opens the certificate page with the animal pre-selected
- **Breeder profile in settings** — name, address, phone saved once, applied to all certificates automatically
- **Full UI translation** — Feedings, Sheddings, Breeding, Dashboard, Animal list now fully translated. Language switcher in sidebar applies immediately across all views

### Fixed
- Build failure due to syntax error in i18n locale files (stray comma introduced by automated script)
- Export page still showing German when UI language was set to English
- "Add animal" button in animal list not translated
- Dashboard stat labels not translated

---

## [1.1.1] – 2025-05-31

### Fixed
- Login page inaccessible after update (removed external vue-i18n dependency, replaced with lightweight custom implementation requiring no npm package)
- Printing labels on A4 generated 5 blank pages plus one with content (print CSS completely rewritten)
- Breeding page showed blank screen when opening the form (females() function missing after refactoring)
- Feeding reminder showed warning even when disabled for that animal
- AnimalBulkCreate schema defined before AnimalCreate, causing Pydantic v2 startup errors
- Duplicate frontend source files prevented clean Vite builds

### Improved
- Label generator: two separate print buttons (exact label size / fit on A4)
- Label generator: QR code target now selectable — Browser, HA Companion App (opens directly to that animal), or custom link
- Language selector now a dropdown with flags instead of simple toggle

---

## [1.1.0] – 2025-05-28

### Added
- Husbandry conditions per animal (temperature, humidity, enclosure size, substrate, UV) — shown as tiles in animal detail and on labels
- Label generator: animal photo on label
- Label generator: husbandry conditions selectable for label
- Animal status: Active / Inactive / Sold
- Animal tracking ID (auto-assigned sequentially, manually overridable — useful for Herkunftsnachweis)
- Multilingual UI: German and English, additional languages can be added by dropping a file in `frontend/src/i18n/`
- Bulk offspring creation from breeding event (1–500 animals at once, useful for tarantula egg sacs)
- Per-animal feeding reminder with individual threshold and option to disable
- Dashboard: click warning card to see overview of animals with overdue feedings
- Mobile-friendly layout: sidebar as overlay with hamburger, responsive tables
- Editing an animal no longer accidentally clears an existing uploaded photo
- HA sensor YAML updated to modern platform structure

### Fixed
- Breeding page crashed when a parent animal had been deleted
- Photo not displayed after upload (URL resolution for direct API port)
- Sex dropdown showed garbled characters instead of options (vue-i18n object iteration issue)

---

## [1.0.0] – 2025-05-20

Initial release.

### Features
- Animal management with photo, morph, origin, parents
- Feeding log (prey type, size, acceptance)
- Shedding log (completeness, blue phase)
- Breeding (pairs, egg laying, clutch size)
- Family tree view
- Label generator (PNG, QR code, 8 colour themes, 300 dpi print)
- Home Assistant integration (webhooks, REST sensors, sidebar entry)
- JWT authentication
