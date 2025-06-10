import requests
from datetime import datetime, timezone
from collections import defaultdict, Counter
import os
import time

# Config
API_KEY = "ntL1UBMbp66sgxrDXnD5"
DOMAIN = "entab"
AUTH = (API_KEY, "X")

GROUPS = {
    1060000223277: "10X-Parvez-PD",
    1060000223275: "10X-Arpit-PD",
    1060000191930: "10X-Atul-PD",
    1060000191937: "10X-Sandhya-PD",
    1060000223274: "10X-Shobia-PD",
    1060000241323: "Backlog",
    1060000338969: "Delta Backlog",
    1060000192412: "10X-Upgrade",
}

UNRESOLVED_STATUS_IDS = [
    2, 3, 4, 6, 7, 8, 9, 10, 11,
    12, 13, 14, 16, 17, 20, 21,
    23, 24, 25, 26
]

agent_cache = {}

# Agent resolver
def get_agent_name(agent_id):
    if not agent_id:
        return "Unassigned"
    if agent_id in agent_cache:
        return agent_cache[agent_id]
    url = f"https://{DOMAIN}.freshdesk.com/api/v2/agents/{agent_id}"
    try:
        res = requests.get(url, auth=AUTH, timeout=10)
        if res.status_code != 200:
            name = f"Agent {agent_id}"
        else:
            name = res.json().get("contact", {}).get("name", f"Agent {agent_id}")
    except:
        name = f"Agent {agent_id}"
    agent_cache[agent_id] = name
    return name

# Ticket fetcher with retry
def fetch_unresolved_tickets(group_id):
    url = f"https://{DOMAIN}.freshdesk.com/api/v2/search/tickets"
    status_query = " OR ".join(f"status:{s}" for s in UNRESOLVED_STATUS_IDS)
    query = f'"group_id:{group_id} AND ({status_query})"'
    tickets, page = [], 1

    while True:
        params = {"query": query, "page": page}
        try:
            res = requests.get(url, auth=AUTH, params=params, timeout=20)
            if res.status_code != 200:
                print(f"❌ Error {res.status_code} on group {group_id}, page {page}")
                break
            results = res.json().get("results", [])
            if not results:
                break
            tickets.extend(results)
            if len(results) < 30:
                break
            page += 1
        except requests.exceptions.ReadTimeout:
            print(f"❌ Failed to fetch page {page} for group {group_id}: timeout")
            break
        except Exception as e:
            print(f"❌ Exception on group {group_id}, page {page}: {e}")
            break

    return tickets

# Build HTML report
def build_html(data):
    today = datetime.now(timezone.utc)
    lines = [
        "<html><head><meta charset='utf-8'><title>Unresolved Tickets</title><style>",
        "body{font-family:sans-serif;padding:20px;background:#fff;}",
        "table{border-collapse:collapse;width:100%;margin-bottom:40px;}",
        "th,td{border:1px solid #ccc;padding:8px;font-size:13px;}",
        "th{background:#006699;color:#fff;}",
        "tr:nth-child(even){background:#f9f9f9;}",
        ".overdue{background:#ffe0e0;}",
        ".summary{background:#f0f0f0;padding:10px;margin-bottom:20px;}",
        "</style>",
        "</head><body><h1>📊 Unresolved Ticket Report</h1>"
    ]

    for group_name, type_map in data.items():
        all_tickets = [t for tks in type_map.values() for t in tks]
        overdue_counts = Counter()
        agent_counts = Counter()
        type_counts = Counter()

        for t in all_tickets:
            created = datetime.strptime(t["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            days = (today - created).days
            if days > 7:
                overdue_counts['>7 days'] += 1
            elif days > 3:
                overdue_counts['4-7 days'] += 1
            elif days > 0:
                overdue_counts['1-3 days'] += 1
            else:
                overdue_counts['today'] += 1
            agent_counts[get_agent_name(t.get("responder_id"))] += 1
            type_counts[t.get("type", "Unspecified")] += 1

        # Summary block
        lines.append(f"<div class='summary'><h2>{group_name}</h2>")
        lines.append(f"<strong>Total:</strong> {len(all_tickets)}<br>")
        lines.append("<strong>Overdue:</strong> " + ", ".join(f"{k}: {v}" for k, v in overdue_counts.items()) + "<br>")
        lines.append("<strong>Top Agents:</strong> " + ", ".join(f"{k}: {v}" for k, v in agent_counts.most_common(3)) + "<br>")
        lines.append("<strong>Top Types:</strong> " + ", ".join(f"{k}: {v}" for k, v in type_counts.most_common(3)))
        lines.append("</div>")

        for ttype, tickets in type_map.items():
            lines.append(f"<h3>{ttype} ({len(tickets)} tickets)</h3>")
            lines.append("<table><tr><th>ID</th><th>Agent</th><th>Created</th><th>Overdue (days)</th><th>Subject</th></tr>")
            for t in tickets:
                created = datetime.strptime(t["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                days = (today - created).days
                agent = get_agent_name(t.get("responder_id"))
                cls = "overdue" if days > 3 else ""
                lines.append(f"<tr class='{cls}'><td>{t['id']}</td><td>{agent}</td><td>{created.date()}</td><td>{days}</td><td>{t['subject'][:80]}</td></tr>")
            lines.append("</table>")

    lines.append("</body></html>")
    return "\n".join(lines)

# Main execution
data_map = defaultdict(lambda: defaultdict(list))

for gid, gname in GROUPS.items():
    print(f"📡 Fetching for {gname}...")
    tickets = fetch_unresolved_tickets(gid)
    for t in tickets:
        ttype = t.get("type", "Unspecified")
        data_map[gname][ttype].append(t)

# Save HTML
output_file = "unresolved_tickets_report.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(build_html(data_map))

print(f"\n✅ Report ready: http://127.0.0.1:3000/{output_file}")
