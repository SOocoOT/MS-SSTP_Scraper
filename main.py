from flask import Flask
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def debug_vpngate():
    url = "https://www.vpngate.net/en/"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # پیدا کردن جدول اصلی
    table = soup.find("table", {"class": "vg_table"})
    if not table:
        return "<h2>جدول اصلی پیدا نشد!</h2>"

    rows = table.find_all("tr")
    html = "<h2>Debug: Raw VPNGate Table</h2><table border=1>"
    for i, row in enumerate(rows):
        cells = row.find_all("td")
        html += f"<tr style='background:#eee;'><td colspan='{len(cells)}'><b>Row {i}</b></td></tr>"
        for j, cell in enumerate(cells):
            text = cell.get_text(" ", strip=True)
            html += f"<tr><td>Cell {j}</td><td>{text}</td></tr>"
    html += "</table>"

    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
