from flask import Flask
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

app = Flask(__name__)

COUNTRY_LIST = [
    "Japan","Germany","Iran","United States","South Korea","France","Canada","China","India","Russia","UK","Turkey",
    "Brazil","Italy","Spain","Netherlands","Sweden","Norway","Australia","Singapore","Thailand","Vietnam","Indonesia"
]

def extract_country(text: str) -> str:
    for c in COUNTRY_LIST:
        if c.lower() in text.lower():
            return c
    return ""

def extract_sessions(text: str) -> str:
    m = re.search(r"(\d[\d,\.]*)\s+sessions", text, re.IGNORECASE)
    return m.group(0) if m else ""

def extract_bw_ping(text: str):
    bw = ""
    ping = ""
    m_bw = re.search(r"([\d\.]+)\s*Mbps", text)
    m_ping = re.search(r"Ping:\s*([\d\.]+)\s*ms", text, re.IGNORECASE)
    if m_bw: bw = f"{m_bw.group(1)} Mbps"
    if m_ping: ping = f"{m_ping.group(1)} ms"
    return bw, ping

@app.route("/")
def show_servers():
    url = "https://www.vpngate.net/en/"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    servers = []
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if not cells: continue

            country, sessions, bandwidth, ping = "", "", "", ""
            for cell in cells:
                txt = cell.get_text(" ", strip=True)
                if not country: country = extract_country(txt)
                if not sessions and "sessions" in txt.lower(): sessions = extract_sessions(txt)
                if "mbps" in txt.lower() or "ping:" in txt.lower():
                    bw, p = extract_bw_ping(txt)
                    if bw and not bandwidth: bandwidth = bw
                    if p and not ping: ping = p

            for cell in cells:
                text = cell.get_text(" ", strip=True)
                if "MS-SSTP" in text:
                    m = re.search(r"SSTP\s*Hostname\s*:\s*([^\s]+)", text, re.IGNORECASE)
                    if m:
                        host = m.group(1)
                        if ":" in host:
                            servers.append((country, host, sessions, bandwidth, ping))

    # حذف تکراری‌ها
    unique, seen = [], set()
    for item in servers:
        if item[1] not in seen:
            seen.add(item[1])
            unique.append(item)

    def ping_val(p):
        try: return float(p.replace(" ms","")) if p else 1e9
        except: return 1e9
    unique.sort(key=lambda x: ping_val(x[4]))

    last_update = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    countries = sorted({s[0] for s in unique if s[0]})

    html = f"""
    <html><head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body {{font-family:Arial;background:#f4f6f9;padding:20px;}}
    h2 {{color:#1f2937;text-align:center;}}
    p {{text-align:center;color:#6b7280;}}
    #controls {{display:flex;gap:10px;justify-content:center;align-items:center;margin:12px 0 18px;}}
    select {{padding:6px 10px;border:1px solid #d1d5db;border-radius:6px;background:#fff;}}
    button {{padding:6px 12px;background:#2563eb;color:white;border:none;border-radius:6px;cursor:pointer;}}
    button:hover {{background:#1d4ed8;}}
    #countdown {{font-weight:bold;color:#ef4444;}}
    table {{border-collapse:collapse;width:98%;margin:auto;background:#fff;}}
    th,td {{border:1px solid #e5e7eb;padding:10px;text-align:center;}}
    th {{background:#111827;color:white;}}
    tr:nth-child(even) {{background:#f9fafb;}}
    tr:hover {{background:#eef6ff;}}
    #toast {{visibility:hidden;min-width:240px;margin-left:-120px;background:#111827;color:#fff;text-align:center;
             border-radius:6px;padding:10px;position:fixed;z-index:1000;left:50%;bottom:24px;font-size:14px;
             box-shadow:0 8px 16px rgba(0,0,0,0.15);}}
    #toast.show {{visibility:visible;animation:fadein 0.35s, fadeout 0.35s 2.65s;}}
    @keyframes fadein {{from{{bottom:0;opacity:0;}} to{{bottom:24px;opacity:1;}}}}
    @keyframes fadeout {{from{{bottom:24px;opacity:1;}} to{{bottom:0;opacity:0;}}}}
    </style>
    <script>
    function copyToClipboard(text) {{
        navigator.clipboard.writeText(text).then(()=>showToast("Copied: "+text),
            err=>showToast("Failed to copy: "+err));
    }}
    function showToast(message) {{
        var toast=document.getElementById("toast");
        toast.innerHTML=message;toast.className="show";
        setTimeout(()=>{{toast.className=toast.className.replace("show","");}},3000);
    }}
    var refreshTime=300;
    function startCountdown(){{
        var countdownElem=document.getElementById("countdown");
        var timeLeft=refreshTime;
        var timer=setInterval(function(){{
            countdownElem.innerHTML="Next refresh in: "+timeLeft+"s";
            timeLeft-=1;
            if(timeLeft<0){{clearInterval(timer);window.location.reload();}}
        }},1000);
    }}
    function manualRefresh(){{window.location.reload();}}
    function filterByCountry(){{
        var filter=document.getElementById("countryFilter").value.toLowerCase();
        var rows=document.getElementById("serversTable").getElementsByTagName("tr");
        for(var i=1;i<rows.length;i++){{
            var countryCell=rows[i].getElementsByTagName("td")[0];
            if(countryCell){{
                var country=(countryCell.textContent||countryCell.innerText).toLowerCase();
                rows[i].style.display=(filter==""||country.includes(filter))?"":"none";
            }}
        }}
    }}
    window.onload=startCountdown;
    </script></head><body>
    <h2>MS-SSTP servers (with port)</h2>
    <p>Last updated: {last_update}</p>
    <div id="controls">
        <button onclick="manualRefresh()">Refresh Now</button>
        <span id="countdown"></span>
        <select id="countryFilter" onchange="filterByCountry()">
            <option value="">All countries</option>
    """

    for c in countries:
        html += f'<option value="{c}">{c}</option>'

    html += """
        </select>
    </div>
    <table id="serversTable">
        <tr>
            <th>Country</th><th>Hostname:Port</th><th>Sessions</th><th>Bandwidth</th><th>Ping</th><th>Action</th>
        </tr>
    """

    for country, host, sessions, bandwidth, ping in unique[:20]:
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
    </body></html>
    """

    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
