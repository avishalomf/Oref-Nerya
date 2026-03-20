import json, urllib.request, os

ALERTS_URL  = "https://www.oref.org.il/warningMessages/alert/Alerts.json"
HISTORY_URL = "https://www.oref.org.il/WarningMessages/History/AlertsHistory.json"
FILTER_AREA = "נריה"

HEADERS = {
    "Referer": "https://www.oref.org.il/",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0",
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as r:
        raw = r.read().decode("utf-8-sig").strip()
        return json.loads(raw) if raw else None

# --- התראות פעילות ---
try:
    data = fetch(ALERTS_URL)
    if data and isinstance(data.get("data"), list):
        data["data"] = [a for a in data["data"] if FILTER_AREA in a]
    with open("alerts.json", "w", encoding="utf-8") as f:
        json.dump(data or {}, f, ensure_ascii=False, indent=2)
    print("alerts.json ✓")
except Exception as e:
    print(f"alerts error: {e}")
    # שמור קובץ ריק כדי שהאפליקציה לא תתרסק
    if not os.path.exists("alerts.json"):
        with open("alerts.json", "w") as f:
            json.dump({}, f)

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
