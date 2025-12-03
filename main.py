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
            if len(cells) >= 6:
                country = cells[0].get_text(strip=True)
                hostname = cells[1].get_text(strip=True)
                uptime = cells[3].get_text(strip=True)
                sessions = cells[4].get_text(strip=True)
                protocols = cells[5].get_text(" ", strip=True)  # پروتکل‌ها با فاصله
                # دیباگ: چاپ پروتکل‌ها
                print("DEBUG protocols:", protocols)
                if "SSTP" in protocols:
                    servers.append((country, hostname, uptime, sessions))

    if not servers:
        return "<h2>هیچ سرور SSTP پیدا نشد (یا VPNGate فعلاً سرور SSTP نداره)</h2>"

    html = "<h2>Top 10 MS-SSTP Servers</h2><table border=1>"
    html += "<tr><th>Country</th><th>Hostname/IP</th><th>Uptime</th><th>Sessions</th></tr>"
    for country, host, uptime, ses in servers[:10]:
        html += f"<tr><td>{country}</td><td>{host}</td><td>{uptime}</td><td>{ses}</td></tr>"
    html += "</table>"
    return html
