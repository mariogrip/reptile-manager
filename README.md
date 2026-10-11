# 🦎 Reptile Manager

**[Deutsch](#deutsch) | [English](#english)**

---

<a name="deutsch"></a>
## Deutsch

Ein selbst gehostetes Haltungsmanagement-Tool für Reptilien — als Home Assistant Add-on.

Ich hab das für mich selbst gebaut, weil mir keine bestehende Lösung gefallen hat die sowohl in HA integrierbar ist als auch offline läuft. Wer seine Haltung gerne dokumentiert und HA nutzt, wird damit hoffentlich genauso gut klarkommen.

### Installation (empfohlen)

**Option A — Ein-Klick:**

[![Repository hinzufügen](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fmariogrip%2Freptile-manager)

**Option B — Manuell:**

1. HA → **Einstellungen → Add-ons → Add-on Store**
2. Oben rechts **⋮ → Repositories**
3. URL eintragen:
   ```
   https://github.com/mariogrip/reptile-manager
   ```
4. Seite neu laden → **Reptile Manager** erscheint im Store
5. Installieren → Konfigurieren → Starten

### Konfiguration

| Option | Bedeutung |
|---|---|
| `admin_username` | Login-Benutzername |
| `admin_password` | Login-Passwort (bitte ändern!) |
| `api_url` | Leer lassen oder `http://HA-IP:8000/api` bei Netzwerkfehlern |

### Was es kann

- **Tierverwaltung** — Art, Morph, Geschlecht, Herkunft, Foto, eigene Tiernummer (ID)
- **Fütterungsprotokoll** — Futterart, Größe, Anzahl, live/TK, Akzeptanz
- **Fütterungserinnerung** — individuelle Warnschwelle pro Tier, deaktivierbar
- **Häutungsprotokoll** — Vollständigkeit, Blauphase, Notizen
- **Zucht** — Paare, Eiablage, Gelegegröße; Nachzucht direkt anlegen (auch 50+ Tiere auf einmal)
- **Status** — Aktiv / Inaktiv / Verkauft
- **Haltungsbedingungen** — Temperatur, Luftfeuchtigkeit, Terrariengröße, Substrat, UV
- **Stammbaum** — Eltern-Kind-Beziehungen mit visueller Darstellung
- **Schild-Generator** — druckfertige Schilder (PNG, 300 dpi) inkl. Tierfoto, QR-Code, Haltungsinfos
- **Herkunftsnachweis** — PDF-Nachweis nach § 46 BNatSchG, als Blanko-Version für Börsen
- **Bestandsexport** — CSV mit allen aktiven Tieren, direkt in Excel öffnen
- **Home Assistant Integration** — Webhooks, REST-Sensoren, Sidebar-Eintrag
- **Mehrsprachig** — Deutsch und Englisch, weitere Sprachen einfach ergänzbar

### HA Sensoren

```yaml
# configuration.yaml
sensor:
  - platform: rest
    resource: http://DEIN_SERVER:8000/api/ha/sensors
    scan_interval: 300
    name: reptile_manager_data
    json_attributes:
      - summary
      - animals

template:
  - sensor:
      - name: "Reptilien aktiv"
        state: "{{ state_attr('sensor.reptile_manager_data', 'summary')['active_animals'] | default(0) }}"
        unit_of_measurement: "Tiere"
        icon: mdi:snake
      - name: "Reptilien nicht gefüttert"
        state: "{{ state_attr('sensor.reptile_manager_data', 'summary')['animals_not_fed'] | default(0) }}"
        unit_of_measurement: "Tiere"
        icon: mdi:food-off
```

### Datenspeicherung

```
/mnt/data/supervisor/addons/data/local_reptile_manager/
├── reptile.db      ← Datenbank
├── uploads/        ← Tierfotos
└── .secret_key     ← JWT-Schlüssel (auto-generiert)
```

Backup:
```bash
cp /mnt/data/supervisor/addons/data/local_reptile_manager/reptile.db \
   ~/reptile-backup-$(date +%Y%m%d).db
```

### Weitere Sprache hinzufügen

Anleitung in [`reptile_manager/frontend/src/i18n/ADDING_LANGUAGES.md`](reptile_manager/frontend/src/i18n/ADDING_LANGUAGES.md)

### Mitmachen

Issues und PRs willkommen — Anleitung in [CONTRIBUTING.md](.github/CONTRIBUTING.md).

### Lizenz

[MIT](LICENSE) — demrios-de

---

<a name="english"></a>
## English

A self-hosted reptile husbandry management tool — as a Home Assistant Add-on.

I built this because I couldn't find anything that was both properly integrated with HA and worked fully offline. If you like keeping detailed records of your animals and use Home Assistant, hopefully this works as well for you as it does for me.

### Installation (recommended)

**Option A — One-click:**

[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fmariogrip%2Freptile-manager)

**Option B — Manual:**

1. HA → **Settings → Add-ons → Add-on Store**
2. Top right **⋮ → Repositories**
3. Enter URL:
   ```
   https://github.com/mariogrip/reptile-manager
   ```
4. Reload page → **Reptile Manager** appears in the store
5. Install → Configure → Start

### Configuration

| Option | Description |
|---|---|
| `admin_username` | Login username |
| `admin_password` | Login password (please change!) |
| `api_url` | Leave empty or set `http://HA-IP:8000/api` if network errors occur |

### Features

- **Animal management** — species, morph, sex, origin, photo, custom tracking ID
- **Feeding log** — prey type, size, count, live/frozen, acceptance
- **Feeding reminders** — individual threshold per animal, can be disabled
- **Shedding log** — completeness, blue phase, notes
- **Breeding** — pairs, egg laying, clutch size; add offspring in bulk (50+ at once)
- **Status** — Active / Inactive / Sold
- **Husbandry conditions** — temperature, humidity, enclosure size, substrate, UV
- **Family tree** — parent-child relationships with visual display
- **Label generator** — print-ready labels (PNG, 300 dpi) with animal photo and QR code
- **Origin certificate** — PDF document for origin documentation per § 46 BNatSchG, blank version for animal fairs
- **Inventory export** — CSV with all active animals, opens directly in Excel
- **Home Assistant integration** — webhooks, REST sensors, sidebar entry
- **Multilingual** — German and English, more languages easily added

### HA Sensors

```yaml
# configuration.yaml
sensor:
  - platform: rest
    resource: http://YOUR_SERVER:8000/api/ha/sensors
    scan_interval: 300
    name: reptile_manager_data
    json_attributes:
      - summary
      - animals

template:
  - sensor:
      - name: "Reptiles active"
        state: "{{ state_attr('sensor.reptile_manager_data', 'summary')['active_animals'] | default(0) }}"
        unit_of_measurement: "animals"
        icon: mdi:snake
      - name: "Reptiles not fed"
        state: "{{ state_attr('sensor.reptile_manager_data', 'summary')['animals_not_fed'] | default(0) }}"
        unit_of_measurement: "animals"
        icon: mdi:food-off
```

### Data storage

```
/mnt/data/supervisor/addons/data/local_reptile_manager/
├── reptile.db      ← database
├── uploads/        ← animal photos
└── .secret_key     ← JWT key (auto-generated)
```

Backup:
```bash
cp /mnt/data/supervisor/addons/data/local_reptile_manager/reptile.db \
   ~/reptile-backup-$(date +%Y%m%d).db
```

### Adding a new language

See [`reptile_manager/frontend/src/i18n/ADDING_LANGUAGES.md`](reptile_manager/frontend/src/i18n/ADDING_LANGUAGES.md)

### Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](.github/CONTRIBUTING.md).

### License

[MIT](LICENSE) — demrios-de
