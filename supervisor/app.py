import json
import time
from datetime import datetime, timezone
from urllib.request import urlopen

from rich.console import Console
from rich.table import Table

CONFIG_PATH = "/etc/telco/config.json"
console = Console()


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as stream:
        config = json.load(stream)

    for key in ("interval_seconds", "timeout_seconds"):
        value = config[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} must be a number")
        if not 0 < value <= 300:
            raise ValueError(f"{key} must be between 0 and 300")

    services = config["services"]
    if not isinstance(services, list) or not services:
        raise ValueError("services must be a non-empty list")

    for service in services:
        if not isinstance(service, dict):
            raise ValueError("Each service must be an object")
        if not isinstance(service.get("name"), str) or not service["name"]:
            raise ValueError("Each service needs a name")
        url = service.get("url")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise ValueError("Each service needs an HTTP or HTTPS URL")

    return config


def check(service, timeout):
    start = time.perf_counter()
    try:
        with urlopen(service["url"], timeout=timeout) as response:
            data = json.load(response)
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object")
        if data.get("service") != service["name"] or data.get("status") != "UP":
            raise ValueError("Unexpected service response")
        elapsed = (time.perf_counter() - start) * 1000
        return "UP", f"{elapsed:.0f} ms"
    except (OSError, ValueError) as exc:
        return "DOWN", str(exc)


while True:
    try:
        config = load_config()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        console.print(f"CONFIG ERROR: {exc}", markup=False)
        time.sleep(10)
        continue

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    interval = config["interval_seconds"]
    table = Table(title=f"Telco Lab | {timestamp} | pause={interval}s")
    table.add_column("Simulated service")
    table.add_column("Status")
    table.add_column("Response / Error")

    for service in config["services"]:
        status, detail = check(service, config["timeout_seconds"])
        table.add_row(
            service["name"],
            status,
            detail,
            style="green" if status == "UP" else "red",
        )

    console.print(table)
    time.sleep(interval)
