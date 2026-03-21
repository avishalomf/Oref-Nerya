import json, urllib.request, os
from datetime import datetime, timezone, timedelta

ALERTS_URL  = "https://api.tzevaadom.co.il/alerts"
HISTORY_URL = "https://api.tzevaadom.co.il/alerts-history"
FILTER_AREA = "נריה"
LOG_FILE    = "alert_log.json"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as r:
        raw = r.read().decode("utf-8").strip()
        return json.loads(raw) if raw else None

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_log(log):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    log = [e for e in log if datetime.fromisoformat(e["detectedAt"].replace("Z","+00:00")) > cutoff]
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"alert_log.json ✓ ({len(log)} רשומות)")

# --- התראות פעילות ---
active_cities = []
try:
    data = fetch(ALERTS_URL)
    # tzevaadom מחזיר רשימת ישובים ישירות
    if isinstance(data, list):
        active_cities = [c for c in data if FILTER_AREA in c]
    
    active = {}
    if active_cities:
        active = {
            "data": active_cities,
            "cat": 1,
            "alertDate": now_iso(),
            "title": "ירי רקטות וטילים",
        }
    
    with open("alerts.json", "w", encoding="utf-8") as f:
        json.dump(active, f, ensure_ascii=False, indent=2)
    print(f"alerts.json ✓ ({len(active_cities)} התראות)")
except Exception as e:
    print(f"alerts error: {e}")
    if not os.path.exists("alerts.json"):
        with open("alerts.json", "w") as f:
            json.dump({}, f)

# --- יומן ---
try:
    log = load_log()
    if active_cities:
        existing = {(e.get("alertDate"), str(e.get("areas"))) for e in log}
        entry_id = (now_iso()[:16], str(active_cities))  # דקה מינימום
        if entry_id not in existing:
            log.append({
                "detectedAt": now_iso(),
                "alertDate":  now_iso(),
                "category":   1,
                "title":      "ירי רקטות וטילים",
                "areas":      active_cities,
            })
    save_log(log)
except Exception as e:
    print(f"log error: {e}")
    with open(LOG_FILE, "w") as f:
        json.dump([], f)

# --- היסטוריה ---
try:
    history = fetch(HISTORY_URL)
    nerya_history = []
    if isinstance(history, list):
        for event in history:
            for alert in (event.get("alerts") or []):
                cities = alert.get("cities", [])
                if any(FILTER_AREA in c for c in cities):
                    nerya_history.append({
                        "alertDate": datetime.fromtimestamp(
                            alert["time"], tz=timezone.utc
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "data": FILTER_AREA,
                        "title": "ירי רקטות וטילים",
                        "category": 1,
                        "threat": alert.get("threat", 0),
                    })
    
    nerya_history.sort(key=lambda x: x["alertDate"], reverse=True)
    
    with open("alerts_history.json", "w", encoding="utf-8") as f:
        json.dump(nerya_history, f, ensure_ascii=False, indent=2)
    print(f"alerts_history.json ✓ ({len(nerya_history)} רשומות)")
except Exception as e:
    print(f"history error: {e}")
    if not os.path.exists("alerts_history.json"):
        with open("alerts_history.json", "w") as f:
            json.dump([], f)
