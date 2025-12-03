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

    # گرفتن همه جدول‌ها
    tables = soup.find_all("table")
    if not tables:
        return "<h2>هیچ جدول در صفحه پیدا نشد!</h2>"

    html = "<h2>Debug: All Tables in VPNGate</h2>"
    for t_index, table in enumerate(tables):
        html += f"<h3>Table {t_index}</h3><table border=1>"
        rows = table.find_all("tr")
        for r_index, row in enumerate(rows):
            cells = row.find_all(["td", "th"])
            html += f"<tr style='background:#eee;'><td colspan='{len(cells)}'><b>Row {r_index}</b></td></tr>"
            for c_index, cell in enumerate(cells):
                text = cell.get_text(" ", strip=True)
                html += f"<tr><td>Cell {c_index}</td><td>{text}</td></tr>"
        html += "</table><br>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
