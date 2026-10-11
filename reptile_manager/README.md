# 🦎 Reptile Manager

A self-hosted reptile husbandry management tool — as a Home Assistant Add-on.

I built this because I couldn't find anything that was both properly integrated with HA and worked fully offline. If you like keeping detailed records of your animals and use Home Assistant, hopefully this works as well for you as it does for me.

## Features

- **Animal management** — species, morph, sex, origin, photo, custom tracking ID
- **Feeding log** — prey type, size, count, live/frozen, acceptance; individual reminder threshold per animal
- **Shedding log** — completeness, blue phase, notes
- **Weight & length tracking** — history per animal with charts and time range filter
- **Dashboard** — weight trends for all animals, with animals losing weight flagged first
- **Breeding** — pairs, egg laying, clutch size; create offspring straight from a breeding event (50+ animals at once)
- **Husbandry conditions** — temperature, humidity, enclosure size, substrate, UV
- **Family tree** — parent-child relationships with visual display
- **Label generator** — print-ready labels (PNG, 300 dpi) with QR code and photo
- **Home Assistant integration** — webhooks on events, REST sensor endpoint, per-animal state push
- **Multilingual** — English (default) and German

## Installation (Home Assistant Add-on)

### Local (development/testing)

1. Copy the `reptile_manager` folder to `/addons/` on the HA host (SSH or Samba)
2. HA → Settings → Add-ons → Add-on Store → ⋮ → Check for updates / reload local add-ons
3. Install "Reptile Manager" (the build takes 2–5 min)
4. Under **Configuration**, set:
   - `admin_username` / `admin_password` — login credentials
   - `api_url` — if network errors occur: `http://HA-IP:8000/api`
5. Start — it appears in the HA sidebar

### Data

Everything is stored persistently in the add-on's `/data/` folder (managed by HA):
```
/data/reptile.db     — SQLite database
/data/uploads/       — animal photos
/data/.secret_key    — auto-generated JWT key
```

## Home Assistant sensors

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

## Tech stack

| Component | Technology |
|---|---|
| Backend | FastAPI (Python 3.12) |
| Database | SQLite (persistent in `/data/`) |
| Frontend | Vue 3 + Tailwind CSS |
| Hosting | Docker (HA Supervisor) |

## Development without Docker

```bash
# Backend
cd backend
pip install -r requirements.txt
DATABASE_URL=sqlite:///./reptile.db uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Backup

```bash
# Copy the database
cp /data/addons/data/local_reptile_manager/reptile.db ~/backup-reptile.db

# Or via SSH
scp root@homeassistant:/data/addons/data/local_reptile_manager/reptile.db .
```

## Contributing

Pull requests and issues are welcome. If you'd like to contribute translations for more languages, the locale files are in `frontend/src/i18n/`.

## License

MIT — details in [LICENSE](LICENSE)
