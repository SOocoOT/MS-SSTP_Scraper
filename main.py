from flask import Flask
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def show_servers():
    try:
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
                # بررسی تعداد ستون‌ها
                if len(cells) >= 6:
                    country = cells[0].get_text(strip=True)   # ستون اول: کشور
                    hostname = cells[1].get_text(strip=True)  # ستون دوم: IP/Hostname
                    uptime = cells[3].get_text(strip=True)    # ستون چهارم: Uptime
                    sessions = cells[4].get_text(strip=True)  # ستون پنجم: Sessions
                    protocols = cells[5].get_text(strip=True) # ستون ششم: Protocols
                    # فقط سرورهایی که SSTP دارند
                    if "SSTP" in protocols:
                        servers.append((country, hostname, uptime, sessions))

        last_update = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        # اگر هیچ سروری پیدا نشد
        if not servers:
            return f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background: #f4f6f9; text-align: center; padding: 50px; }}
                    h2 {{ color: #e74c3c; }}
                    p {{ color: #555; }}
                    button {{ padding: 8px 15px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }}
                    button:hover {{ background: #2980b9; }}
                </style>
                <script>
                    function manualRefresh() {{
                        window.location.reload();
                    }}
                </script>
            </head>
            <body>
                <h2>No SSTP Servers Found</h2>
                <p>Last updated: {last_update}</p>
                <p>It seems VPNGate did not return any SSTP servers at this time.</p>
                <button onclick="manualRefresh()">Try Again</button>
            </body>
            </html>
            """

        servers_to_show = servers[:10]

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
                function manualRefresh() {{
                    window.location.reload();
                }}
                window.onload = startCountdown;
            </script>
        </head>
        <body>
            <h2>Top 10 MS-SSTP Servers</h2>
            <p>Last updated: {last_update}</p>
            <p id="countdown"></p>
            <div style="text-align:center; margin:10px;">
                <button onclick="manualRefresh()">Refresh Now</button>
            </div>
            <table>
                <tr>
                    <th>Country</th>
                    <th>Hostname/IP</th>
                    <th>Uptime</th>
                    <th>Sessions</th>
                    <th>Action</th>
                </tr>
        """

        for country, host, uptime, ses in servers_to_show:
            html += f"""
                <tr>
                    <td>{country}</td>
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

    except Exception as e:
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f4f6f9; text-align: center; padding: 50px; }}
                h2 {{ color: #e74c3c; }}
                p {{ color: #555; }}
                button {{ padding: 8px 15px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }}
                button:hover {{ background: #2980b9; }}
            </style>
            <script>
                function manualRefresh() {{
                    window.location.reload();
                }}
            </script>
        </head>
        <body>
            <h2>Network Error</h2>
            <p>Last attempt: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
            <p>There was a problem connecting to VPNGate. Please check your connection or try again later.</p>
            <button onclick="manualRefresh()">Retry</button>
        </body>
        </html>
        """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
