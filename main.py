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
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            for cell in cells:
                text = cell.get_text(" ", strip=True)
                # اگر متن شامل MS-SSTP بود
                if "MS-SSTP" in text:
                    # استخراج hostname با regex
                    match = re.search(r"SSTP Hostname\s*:\s*([^\s]+)", text)
                    if match:
                        hostname = match.group(1)
                        servers.append(hostname)

    last_update = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if not servers:
        return f"<h2>No SSTP Servers Found (Last updated: {last_update})</h2>"

    html = f"<h2>Top MS-SSTP Servers</h2><p>Last updated: {last_update}</p><table border=1>"
    html += "<tr><th>Hostname</th></tr>"
    for host in servers[:10]:
        html += f"<tr><td>{host}</td></tr>"
    html += "</table>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
