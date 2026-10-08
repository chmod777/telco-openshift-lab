import json
import time
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

from rich.console import Console
from rich.table import Table

url = "http://localhost:8081/index.html"
start = time.perf_counter()

try:
    with urlopen(url, timeout=3) as response:
        data = json.load(response)
        if data.get("service") != "packet-core" or data.get("status") != "UP":
            raise ValueError("Unexpected service response")
    status = "[green]UP[/green]"
    detail = f"{(time.perf_counter() - start) * 1000:.0f} ms"
except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
    status = "[red]DOWN[/red]"
    detail = str(exc)

table = Table(title="Telco OpenShift Lab")
table.add_column("Service")
table.add_column("Status")
table.add_column("Response")
table.add_row("Packet Core (simulated)", status, detail)

Console().print(table)
