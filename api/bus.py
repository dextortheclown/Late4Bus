import requests
import os
import sys

def _get_ssl_cert():
    if getattr(sys, "frozen", False):
        # Running as PyInstaller exe
        import certifi
        return certifi.where()
    return True

SSL_CERT = _get_ssl_cert()

BASE_URL = "https://datamall2.mytransport.sg/ltaodataservice/v3"

HEADERS = {
    "AccountKey": "",
    "accept": "application/json"
}

LOAD_MAP = {
    "SEA": "Seats available",
    "SDA": "Standing available",
    "LSD": "Crowded",
    ""   : "Unknown"
}

LOAD_COLOR_MAP = {
    "SEA": "#4ade80",   # green
    "SDA": "#facc15",   # yellow
    "LSD": "#f87171",   # red
    ""   : "#6b7280"    # gray
}

TYPE_MAP = {
    "SD": "Single",
    "DD": "Double",
    "BD": "Bendy",
    "": ""
}


def set_api_key(key: str):
    global HEADERS
    HEADERS = {
        "AccountKey": key,
        "accept": "application/json"
    }


def get_bus_arrivals(stop_code: str, service_no: str = ""):
    from utils.config_manager import get_api_key
    headers = {
        "AccountKey": get_api_key(),
        "accept": "application/json"
    }

    params = {"BusStopCode": stop_code}
    if service_no:
        params["ServiceNo"] = service_no

    try:
        resp = requests.get(
            f"{BASE_URL}/BusArrival",
            headers=headers,
            params=params,
            timeout=8,
            verify=SSL_CERT
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "services": []}

    services = []
    for svc in data.get("Services", []):
        buses = []
        for bus_key in ("NextBus", "NextBus2", "NextBus3"):
            bus = svc.get(bus_key, {})
            arrival = bus.get("EstimatedArrival", "")
            load = bus.get("Load", "")
            bus_type = bus.get("Type", "")
            if arrival:
                from datetime import datetime, timezone
                try:
                    arr_dt = datetime.fromisoformat(arrival)
                    now = datetime.now(timezone.utc)
                    mins = int((arr_dt - now).total_seconds() / 60)
                    mins = max(0, mins)
                except ValueError:
                    mins = None
            else:
                mins = None

            buses.append({
                "arrival_iso": arrival,
                "minutes": mins,
                "load": load,
                "load_label": LOAD_MAP.get(load, "Unknown"),
                "load_color": LOAD_COLOR_MAP.get(load, "#6b7280"),
                "type": bus_type,
                "type_label": TYPE_MAP.get(bus_type, bus_type)
            })

        services.append({
            "service_no": svc.get("ServiceNo", ""),
            "operator": svc.get("Operator", ""),
            "buses": buses
        })

    return {"error": None, "services": services}


def search_bus_stops(query: str, all_stops: list) -> list:
    """
    Filter the cached bus stop list by query string.
    Matches stop code, description, or road name.
    """
    q = query.lower().strip()
    if not q:
        return all_stops[:50]
    results = []
    for stop in all_stops:
        if (q in stop.get("BusStopCode", "").lower() or
                q in stop.get("Description", "").lower() or
                q in stop.get("RoadName", "").lower()):
            results.append(stop)
        if len(results) >= 50:
            break
    return results


def fetch_all_bus_stops() -> list:
    import certifi
    import traceback
    from utils.config_manager import get_api_key

    # Read key fresh from config, same as get_bus_arrivals
    headers = {
        "AccountKey": get_api_key(),
        "accept": "application/json"
    }

    bus_stops_url = "https://datamall2.mytransport.sg/ltaodataservice/BusStops"

    log_path = os.path.join(os.environ.get("APPDATA", ""), "Late4Bus", "debug.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    stops = []
    skip = 0

    try:
        with open(log_path, "w") as log:
            log.write(f"SSL cert path: {certifi.where()}\n")
            log.write(f"API key (first 6): {headers['AccountKey'][:6]}\n")
            log.write(f"BusStops URL: {bus_stops_url}\n")

            while True:
                log.write(f"Fetching skip={skip}\n")
                try:
                    resp = requests.get(
                        bus_stops_url,
                        headers=headers,
                        params={"$skip": skip},
                        timeout=15,
                        verify=certifi.where()
                    )
                    log.write(f"Status: {resp.status_code}\n")
                    log.write(f"Response preview: {resp.text[:300]}\n")
                    resp.raise_for_status()
                    data = resp.json()
                except Exception as e:
                    log.write(f"Request error: {e}\n")
                    traceback.print_exc(file=log)
                    break

                batch = data.get("value", [])
                log.write(f"Batch size: {len(batch)}\n")
                if not batch:
                    break
                stops.extend(batch)
                skip += 500
                if len(batch) < 500:
                    break

            log.write(f"Total stops fetched: {len(stops)}\n")
    except Exception as e:
        with open(log_path, "a") as log:
            log.write(f"Outer error: {e}\n")

    return stops
