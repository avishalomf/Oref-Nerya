import json, urllib.request, os
from datetime import datetime, timezone, timedelta

ALERTS_URL  = "https://www.oref.org.il/warningMessages/alert/Alerts.json"
HISTORY_URL = "https://www.oref.org.il/WarningMessages/History/AlertsHistory.json"
FILTER_AREA = "נריה"
LOG_FILE    = "alert_log.json"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "he-IL,he;q=0.9",
    "Referer": "https://www.oref.org.il/12481-he/Pakar.aspx",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as r:
        raw = r.read().decode("utf-8-sig").strip()
        return json.loads(raw) if raw else None

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_log(log):
    # שמור רק 24 שעות אחרונות
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    log = [e for e in log if datetime.fromisoformat(e["detectedAt"].replace("Z","+00:00")) > cutoff]
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

# --- התראות פעילות ---
active_data = None
try:
    data = fetch(ALERTS_URL)
    if data and isinstance(data.get("data"), list):
        data["data"] = [a for a in data["data"] if FILTER_AREA in a]
    active_data = data
    with open("alerts.json", "w", encoding="utf-8") as f:
        json.dump(data or {}, f, ensure_ascii=False, indent=2)
    print("alerts.json ✓")
except Exception as e:
    print(f"alerts error: {e}")
    if not os.path.exists("alerts.json"):
        with open("alerts.json", "w") as f:
            json.dump({}, f)

# --- יומן עצמאי ---
try:
    log = load_log()
    if active_data and isinstance(active_data.get("data"), list) and active_data["data"]:
        existing = {(e.get("alertDate"), str(e.get("areas"))) for e in log}
        entry_id = (active_data.get("alertDate"), str(active_data["data"]))
        if entry_id not in existing:
            log.append({
                "detectedAt": now_iso(),
                "alertDate":  active_data.get("alertDate", ""),
                "category":   active_data.get("cat", 0),
                "title":      active_data.get("title", ""),
                "areas":      active_data["data"],
            })
            print(f"alert_log.json ✓ — {active_data['data']}")
    save_log(log)
except Exception as e:
    print(f"log error: {e}")
    # צור קובץ ריק אם לא קיים
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

# --- היסטוריה ---
try:
    history = fetch(HISTORY_URL)
    if isinstance(history, list):
        history = [h for h in history if FILTER_AREA in (h.get("data") or "")]
    with open("alerts_history.json", "w", encoding="utf-8") as f:
        json.dump(history or [], f, ensure_ascii=False, indent=2)
    print("alerts_history.json ✓")
except Exception as e:
    print(f"history error: {e}")
    if not os.path.exists("alerts_history.json"):
        with open("alerts_history.json", "w") as f:
            json.dump([], f)
