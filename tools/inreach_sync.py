#!/usr/bin/env python3
"""Pull the Garmin inReach MapShare feed into trip/days/<date>.json.

Run by .github/workflows/inreach-sync.yml on a schedule. Fetches the KML
feed at share.garmin.com/Feed/Share/<INREACH_MAPSHARE> for the last few
days, groups the track points by local date, and merges them into the same
day files the road trip pages use. Existing "stay" and "notes" fields are
preserved, and points already in a file (from the phone tracker or an
earlier run) are kept, deduplicated by timestamp.

Env:
  INREACH_MAPSHARE  the MapShare name, the XXXX in share.garmin.com/XXXX (required)
  INREACH_PASSWORD  the MapShare password, if one is set (optional)

Writes only under trip/days/. Exits 0 quietly if INREACH_MAPSHARE is unset
so the scheduled run does not fail before setup.
"""

import base64
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DAYS_DIR = REPO_ROOT / "trip" / "days"
FEED_URL = "https://share.garmin.com/Feed/Share/{name}?d1={d1}"
LOOKBACK_DAYS = 4
KML_NS = "{http://www.opengis.net/kml/2.2}"


def fetch_feed(name, password):
    d1 = (datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).strftime(
        "%Y-%m-%dT00:00Z"
    )
    req = urllib.request.Request(FEED_URL.format(name=name, d1=d1))
    if password:
        # mapshare protects the feed with basic auth: empty user, the password
        token = base64.b64encode((":" + password).encode()).decode()
        req.add_header("Authorization", "Basic " + token)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def parse_points(kml_bytes):
    """Yield (lat, lon, unix_seconds) from the feed's point placemarks."""
    root = ET.fromstring(kml_bytes)
    for pm in root.iter(KML_NS + "Placemark"):
        when = pm.find(f"./{KML_NS}TimeStamp/{KML_NS}when")
        coords = pm.find(f"./{KML_NS}Point/{KML_NS}coordinates")
        if when is None or coords is None or not when.text or not coords.text:
            continue
        try:
            t = int(
                datetime.fromisoformat(when.text.strip().replace("Z", "+00:00"))
                .astimezone(timezone.utc)
                .timestamp()
            )
            lon, lat = (float(v) for v in coords.text.strip().split(",")[:2])
        except (ValueError, OverflowError):
            continue
        if lat == 0 and lon == 0:
            continue
        yield (round(lat, 5), round(lon, 5), t)


def local_date(lat, lon, t):
    """Local calendar date for a point, from its longitude.

    round(lon/15) is solar time; the +1 matches north american daylight
    time for this summer trip (toronto -4, winnipeg -5, vancouver -7).
    """
    offset = round(lon / 15) + 1
    return (
        datetime.fromtimestamp(t, timezone.utc) + timedelta(hours=offset)
    ).strftime("%Y-%m-%d")


def merge_day(date, new_points):
    path = DAYS_DIR / f"{date}.json"
    day = {"date": date, "stay": "", "points": []}
    if path.exists():
        day = json.loads(path.read_text())
    by_time = {p[2]: p for p in day.get("points", [])}
    for p in new_points:
        by_time.setdefault(p[2], list(p))
    merged = [by_time[t] for t in sorted(by_time)]
    if merged == day.get("points", []):
        return False
    day["points"] = merged
    DAYS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(day, separators=(",", ":")) + "\n")
    return True


def main():
    name = os.environ.get("INREACH_MAPSHARE", "").strip()
    if not name:
        print("INREACH_MAPSHARE not set; nothing to sync.")
        return 0
    kml = fetch_feed(name, os.environ.get("INREACH_PASSWORD", "").strip())
    by_date = {}
    for lat, lon, t in parse_points(kml):
        by_date.setdefault(local_date(lat, lon, t), []).append((lat, lon, t))
    changed = [d for d, pts in sorted(by_date.items()) if merge_day(d, pts)]
    total = sum(len(v) for v in by_date.values())
    print(f"{total} feed points across {len(by_date)} day(s); updated: "
          + (", ".join(changed) if changed else "nothing"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
