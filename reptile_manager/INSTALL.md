# 🦎 Reptile Manager — Home Assistant Add-on

## Installing as a local add-on

### Step 1 — Copy the files to the HA host

Connect to your HA instance via SSH or Samba and copy the
`reptile_manager` folder into the local add-on directory:

```
/addons/
└── reptile_manager/     ← this folder
    ├── config.yaml
    ├── Dockerfile
    ├── run.sh
    ├── supervisord.conf
    ├── nginx.conf
    ├── backend/
    └── frontend/
```

**Via SCP:**
```bash
scp -r reptile_manager/ root@homeassistant.local:/addons/reptile_manager
```

**Via Samba:** `\\homeassistant\addons\` → create a `reptile_manager` folder and copy the contents into it.

---

### Step 2 — Install the add-on

1. HA frontend → **Settings → Add-ons → Add-on Store**
2. Top right: **⋮ → Check for updates** (reloads local add-ons)
3. **Reptile Manager** now appears under "Local add-ons"
4. Click it → **Install** (the build takes 2–5 minutes)

---

### Step 3 — Configure

After installing → **Configuration** tab:

| Option | Description | Default |
|---|---|---|
| `admin_username` | Login username | `admin` |
| `admin_password` | Login password | `admin123` |
| `secret_key` | JWT secret (empty = generated automatically) | *(empty)* |

→ **Save** → **Start**

---

### Step 4 — Open

- **Sidebar**: Reptile Manager appears automatically in the HA sidebar (Ingress)
- **Direct**: `http://homeassistant.local:8099`

---

## Data storage

All data is stored persistently in the add-on's `/data/` folder (managed by HA):

```
/data/
├── reptile.db       ← SQLite database
├── uploads/         ← animal photos
│   └── animals/
└── .secret_key      ← auto-generated JWT key
```

## Updating

To update, replace the files in `/addons/reptile_manager/`
and **Rebuild** → **Restart** the add-on.

## Home Assistant sensors

The `/api/ha/sensors` endpoint is public (no login required) so HA can
poll it. In `configuration.yaml`:

```yaml
rest:
  - resource: http://localhost:8099/api/ha/sensors
    scan_interval: 300
    sensor:
      - name: "Reptiles total"
        value_template: "{{ value_json.summary.active_animals }}"
        icon: mdi:snake
      - name: "Reptiles not fed"
        value_template: "{{ value_json.summary.animals_not_fed }}"
        icon: mdi:food-off
```
