from flask import Flask
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def show_servers():
    url = "https://www.vpngate.net/en/"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    servers = []
    rows = soup.find_all("tr")
    for row in rows:
        sstp_cell = row.find("td", string=re.compile("MS-SSTP", re.I))
        if sstp_cell:
            text = sstp_cell.get_text(" ", strip=True)
            match = re.search(r"SSTP Hostname\s*:\s*([^\s]+)", text)
            if match:
                hostname = match.group(1)
                servers.append(hostname)

    return "<br>".join(servers) or "هیچ سروری پیدا نشد"
    
def MAINshow_servers():
    url = "https://www.vpngate.net/en/"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    servers = []
    rows = soup.find_all("tr")
    for row in rows:
        sstp_cell = row.find("td", string=re.compile("MS-SSTP", re.I))
        if sstp_cell:
            text = sstp_cell.get_text(" ", strip=True)
            match = re.search(r"SSTP Hostname\s*:\s*([^\s]+)", text)
            if match:
                hostname = match.group(1)
                if ":" in hostname:
                    uptime_days = None
                    sessions = None
                    cells = row.find_all("td")
                    for cell in cells:
                        cell_text = cell.get_text(" ", strip=True).lower()
                        day_match = re.search(r"(\d+)\s*days", cell_text)
                        if day_match:
                            uptime_days = int(day_match.group(1))
                        session_match = re.search(r"(\d+)\s*sessions", cell_text)
                        if session_match:
                            sessions = int(session_match.group(1))
                    if uptime_days is not None and sessions is not None:
                        servers.append((hostname, uptime_days, sessions))

    servers_sorted = sorted(servers, key=lambda x: (x[1], x[2]))
    servers_to_show = servers_sorted[:10]

    last_update = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    html = f"<h2>Top 10 MS-SSTP Servers</h2><p>Last updated: {last_update}</p><table border=1>"
    html += "<tr><th>Hostname</th><th>Uptime</th><th>Sessions</th></tr>"
    for host, days, ses in servers_to_show:
        html += f"<tr><td>{host}</td><td>{days}</td><td>{ses}</td></tr>"
    html += "</table>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
