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
            for i, cell in enumerate(cells):
                text = cell.get_text(" ", strip=True)
                if "MS-SSTP" in text:
                    # استخراج hostname و پورت
                    match = re.search(r"SSTP Hostname\s*:\s*([^\s]+)", text)
                    if match:
                        host = match.group(1)
                        if ":" in host:  # فقط سرورهایی که پورت دارند
                            country = ""
                            sessions = ""
                            bandwidth = ""
                            ping = ""

                            # کشور معمولاً در سلول‌های قبلی
                            if i >= 1:
                                country = cells[i-1].get_text(" ", strip=True)
                            # sessions معمولاً در دو سلول قبل
                            if i >= 2:
                                sessions = cells[i-2].get_text(" ", strip=True)
                            # bandwidth و ping معمولاً در سه سلول قبل
                            if i >= 3:
                                bw_ping_text = cells[i-3].get_text(" ", strip=True)
                                bw_match = re.search(r"([\d\.]+ Mbps)", bw_ping_text)
                                ping_match = re.search(r"Ping:\s*([\d\.]+ ms)", bw_ping_text)
                                if bw_match:
                                    bandwidth = bw_match.group(1)
                                if ping_match:
                                    ping = ping_match.group(1)

                            servers.append((country, host, sessions, bandwidth, ping))

    last_update = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if not servers:
        return f"<h2>No SSTP Servers with port found (Last updated: {last_update})</h2>"

    html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f6f9; padding: 20px; }}
            h2 {{ color: #2c3e50; text-align: center; }}
            p {{ text-align: center; color: #555; }}
            table {{ border-collapse: collapse; width: 95%; margin: auto; background: #fff; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: center; }}
            th {{ background-color: #2c3e50; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            tr:hover {{ background-color: #e6f7ff; }}
            button {{ padding: 5px 10px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #2980b9; }}
            #toast {{
                visibility: hidden;
                min-width: 200px;
                margin-left: -100px;
                background-color: #333;
                color: #fff;
                text-align: center;
                border-radius: 4px;
                padding: 10px;
                position: fixed;
                z-index: 1;
                left: 50%;
                bottom: 30px;
                font-size: 14px;
            }}
            #toast.show {{
                visibility: visible;
                -webkit-animation: fadein 0.5s, fadeout 0.5s 2.5s;
                animation: fadein 0.5s, fadeout 0.5s 2.5s;
            }}
        </style>
        <script>
            function copyToClipboard(text) {{
                navigator.clipboard.writeText(text).then(function() {{
                    showToast("Copied: " + text);
                }}, function(err) {{
                    showToast("Failed to copy: " + err);
                }});
            }}
            function showToast(message) {{
                var toast = document.getElementById("toast");
                toast.innerHTML = message;
                toast.className = "show";
                setTimeout(function(){{ toast.className = toast.className.replace("show", ""); }}, 3000);
            }}
        </script>
    </head>
    <body>
        <h2>MS-SSTP Servers with Port</h2>
        <p>Last updated: {last_update}</p>
        <table>
            <tr>
                <th>Country</th>
                <th>Hostname:Port</th>
                <th>Sessions</th>
                <th>Bandwidth</th>
                <th>Ping</th>
                <th>Action</th>
            </tr>
    """

    for country, host, sessions, bandwidth, ping in servers[:10]:
        html += f"""
            <tr>
                <td>{country}</td>
                <td>{host}</td>
                <td>{sessions}</td>
                <td>{bandwidth}</td>
                <td>{ping}</td>
                <td><button onclick="copyToClipboard('{host}')">Copy</button></td>
            </tr>
        """

    html += """
        </table>
        <div id="toast"></div>
    </body>
    </html>
    """

    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
