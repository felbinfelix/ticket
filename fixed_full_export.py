
import requests
import csv
import time
from datetime import datetime, timedelta

API_KEY = "ntL1UBMbp66sgxrDXnD5"
DOMAIN = "entab"
AUTH = (API_KEY, "X")

GROUP_MAP = {
    1060000223277: "10X-Parvez-PD",
    1060000223275: "10X-Arpit-PD",
    1060000191930: "10X-Atul-PD",
    1060000191937: "10X-Sandhya-PD",
    1060000223274: "10X-Shobia-PD",
    1060000241323: "Backlog",
    1060000338969: "Delta Backlog",
    1060000116916: "PD- Arpit",
    1060000079287: "PD- Atul",
    1060000079291: "PD- Manju",
    1060000223162: "PD- Narender",
    1060000079292: "PD- Pankaj",
    1060000080833: "PD- Sandhya",
    1060000079294: "PD- Shobia",
    1060000079296: "PD- Ushas",
}
VALID_GROUP_IDS = set(GROUP_MAP.keys())

def fetch_tickets_in_chunks(start_date, end_date):
    page = 1
    all_tickets = []

    while page <= 10:
        query = f"(status:8 OR status:16) AND created_at:>'{start_date}' AND created_at:<'{end_date}'"
        url = f"https://{DOMAIN}.freshdesk.com/api/v2/search/tickets?query=\"{query}\"&page={page}"
        print(f"📦 Fetching {start_date} → {end_date} | Page {page}")
        response = requests.get(url, auth=AUTH)
        if response.status_code != 200:
            print(f"❌ Error page {page}: {response.status_code} - {response.text}")
            break
        result = response.json()
        tickets = result.get("results", [])
        if not tickets:
            break
        all_tickets.extend(tickets)
        page += 1
        time.sleep(1)

    return all_tickets

def run_full_export():
    start = datetime(2023, 1, 1)
    end = datetime(2025, 5, 18)
    delta = timedelta(days=1)

    all_rows = []
    seen_ids = set()

    while start < end:
        chunk_start = start.strftime("%Y-%m-%d")
        chunk_end = (start + delta).strftime("%Y-%m-%d")
        tickets = fetch_tickets_in_chunks(chunk_start, chunk_end)

        for ticket in tickets:
            if ticket.get("group_id") in VALID_GROUP_IDS:
                ticket_id = ticket.get("id")
                if ticket_id in seen_ids:
                    continue
                seen_ids.add(ticket_id)

                cf = ticket.get("custom_fields", {})
                all_rows.append([
                    ticket_id,
                    ticket.get("subject", ""),
                    GROUP_MAP.get(ticket["group_id"], "Unknown"),
                    ticket.get("status", ""),
                    ticket.get("priority", ""),
                    ticket.get("created_at", ""),
                    ", ".join(ticket.get("tags", [])),
                    ticket.get("requester_email", ""),
                    ticket.get("responder_id", ""),
                    cf.get("cf_school_code", ""),
                    cf.get("cf_priority_reason", ""),
                    cf.get("cf_module", ""),
                    ticket.get("type", "")
                ])
        start += delta

    with open("all_unresolved_tickets_full.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "ID", "Subject", "Group Name", "Status", "Priority", "Created At",
            "Tags", "Requester Email", "Responder ID",
            "School Code", "Priority Reason", "Module", "Type"
        ])
        writer.writerows(all_rows)

    print(f"✅ Export completed. Total unique tickets written: {len(all_rows)}")

if __name__ == "__main__":
    run_full_export()
