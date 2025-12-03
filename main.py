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
    table = soup.find("table", {"class": "vg_table"})
    if table:
        rows = table.find_all("tr")
        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) > 0:
                hostname = cells[0].get_text(strip=True)
                uptime = cells[1].get_text(strip=True)
                sessions = cells[2].get_text(strip=True)
                if "MS-SSTP" in row.get_text():
                    servers.append((hostname, uptime, sessions))

    servers_to_show = servers[:10]
    last_update = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f6f9; padding: 20px; }}
            h2 {{ color: #2c3e50; text-align: center; }}
            p {{ text-align: center; color: #555; }}
            #countdown {{ text-align: center; font-weight: bold; color: #e74c3c; }}
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
            @-webkit-keyframes fadein {{ from {{bottom: 0; opacity: 0;}} to {{bottom: 30px; opacity: 1;}} }}
            @keyframes fadein {{ from {{bottom: 0; opacity: 0;}} to {{bottom: 30px; opacity: 1;}} }}
            @-webkit-keyframes fadeout {{ from {{bottom: 30px; opacity: 1;}} to {{bottom: 0; opacity: 0;}} }}
            @keyframes fadeout {{ from {{bottom: 30px; opacity: 1;}} to {{bottom: 0; opacity: 0;}} }}
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
            // Auto-refresh هر 5 دقیقه
            var refreshTime = 300; // ثانیه
            function startCountdown() {{
                var countdownElem = document.getElementById("countdown");
                var timeLeft = refreshTime;
                var timer = setInterval(function() {{
                    countdownElem.innerHTML = "Next refresh in: " + timeLeft + "s";
                    timeLeft -= 1;
                    if (timeLeft < 0) {{
                        clearInterval(timer);
                        window.location.reload();
                    }}
                }}, 1000);
            }}
            window.onload = startCountdown;
        </script>
    </head>
    <body>
        <h2>Top 10 MS-SSTP Servers</h2>
        <p>Last updated: {last_update}</p>
        <p id="countdown"></p>
        <table>
            <tr>
                <th>Hostname</th>
                <th>Uptime</th>
                <th>Sessions</th>
                <th>Action</th>
            </tr>
    """

    for host, uptime, ses in servers_to_show:
        html += f"""
            <tr>
                <td>{host}</td>
                <td>{uptime}</td>
                <td>{ses}</td>
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
