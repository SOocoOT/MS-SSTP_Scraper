from flask import Flask
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

app = Flask(__name__)

# ساده: تشخیص اینکه متن احتمالاً کشور است
def looks_like_country(text: str) -> bool:
    if not text:
        return False
    # حذف چیزهای رایج غیرکشور
    bad_tokens = ["sessions", "Mbps", "Ping", "TCP", "UDP", "OpenVPN", "L2TP", "SSL-VPN", "Logging", "GB", "users", "Hostname"]
    if any(tok.lower() in text.lower() for tok in bad_tokens):
        return False
    # کشورها معمولاً بدون عدد و کوتاه هستند
    if re.search(r"\d", text):
        return False
    # طول معقول و فقط حروف، فاصله و خط فاصله
    if len(text) > 30:
        return False
    if not re.fullmatch(r"[A-Za-z\s\-]+", text):
        return False
    return True

def extract_sessions(text: str) -> str:
    # مثال‌ها: "97 sessions", "42 sessions 6 days"
    m = re.search(r"(\d[\d,\.]*)\s+sessions", text, re.IGNORECASE)
    return m.group(0) if m else ""

def extract_bw_ping(text: str):
    bw = ""
    ping = ""
    m_bw = re.search(r"([\d\.]+)\s*Mbps", text)
    m_ping = re.search(r"Ping:\s*([\d\.]+)\s*ms", text, re.IGNORECASE)
    if m_bw:
        bw = f"{m_bw.group(1)} Mbps"
    if m_ping:
        ping = f"{m_ping.group(1)} ms"
    return bw, ping

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
            if not cells:
                continue

            # پیش‌اسکن برای کشور، سشن‌ها و BW/Ping در همان ردیف
            country = ""
            sessions = ""
            bandwidth = ""
            ping = ""

            for cell in cells:
                txt = cell.get_text(" ", strip=True)

                # کشور
                if not country and looks_like_country(txt):
                    country = txt

                # سشن‌ها
                if not sessions and "sessions" in txt.lower():
                    sessions = extract_sessions(txt)

                # پهنای‌باند و پینگ
                if ("mbps" in txt.lower()) or ("ping:" in txt.lower()):
                    bw, p = extract_bw_ping(txt)
                    if bw and not bandwidth:
                        bandwidth = bw
                    if p and not ping:
                        ping = p

            # جستجوی MS-SSTP و استخراج hostname:port
            for cell in cells:
                text = cell.get_text(" ", strip=True)
                if "MS-SSTP" in text:
                    m = re.search(r"SSTP\s*Hostname\s*:\s*([^\s]+)", text, re.IGNORECASE)
                    if m:
                        host = m.group(1)
                        # فقط رکوردهای دارای پورت (مثلاً host:443)
                        if ":" in host:
                            servers.append((country, host, sessions, bandwidth, ping))

    last_update = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # حذف تکراری‌ها و مرتب‌سازی ساده (اول کمترین پینگ)
    unique = []
    seen = set()
    for item in servers:
        key = item[1]  # hostname:port
        if key not in seen:
            seen.add(key)
            unique.append(item)

    def ping_val(p):
        try:
            return float(p.replace(" ms", "")) if p else 9999.0
        except:
            return 9999.0

    unique.sort(key=lambda x: ping_val(x[4]))

    if not unique:
        return f"<h2>No SSTP servers with port found</h2><p>Last updated: {last_update}</p>"

    html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f6f9; padding: 20px; }}
            h2 {{ color: #2c3e50; text-align: center; }}
            p {{ text-align: center; color: #555; }}
            table {{ border-collapse: collapse; width: 98%; margin: auto; background: #fff; }}
            th, td {{ border: 1px solid #e5e7eb; padding: 10px; text-align: center; }}
            th {{ background-color: #1f2937; color: white; }}
            tr:nth-child(even) {{ background-color: #f9fafb; }}
            tr:hover {{ background-color: #eef6ff; }}
            button {{ padding: 6px 12px; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer; }}
            button:hover {{ background: #1d4ed8; }}
            #toast {{
                visibility: hidden;
                min-width: 240px;
                margin-left: -120px;
                background-color: #111827;
                color: #fff;
                text-align: center;
                border-radius: 6px;
                padding: 10px;
                position: fixed;
                z-index: 1000;
                left: 50%;
                bottom: 24px;
                font-size: 14px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            }}
            #toast.show {{
                visibility: visible;
                -webkit-animation: fadein 0.35s, fadeout 0.35s 2.65s;
                animation: fadein 0.35s, fadeout 0.35s 2.65s;
            }}
            @keyframes fadein {{
                from {{bottom: 0; opacity: 0;}}
                to {{bottom: 24px; opacity: 1;}}
            }}
            @keyframes fadeout {{
                from {{bottom: 24px; opacity: 1;}}
                to {{bottom: 0; opacity: 0;}}
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
        <h2>MS-SSTP servers (with port)</h2>
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

    for country, host, sessions, bandwidth, ping in unique[:12]:
        html += f"""
            <tr>
                <td>{country or "-"}</td>
                <td>{host}</td>
                <td>{sessions or "-"}</td>
                <td>{bandwidth or "-"}</td>
                <td>{ping or "-"}</td>
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
