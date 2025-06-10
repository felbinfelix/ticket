import requests
import csv
import time
from datetime import datetime, timedelta, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

# Setup session with retry logic
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)

def fetch_tickets_in_chunks(start_date, end_date):
    page = 1
    all_tickets = []

    while page <= 10:
        query = f"(status:8 OR status:16) AND created_at:>'{start_date}' AND created_at:<'{end_date}'"
        url = f"https://{DOMAIN}.freshdesk.com/api/v2/search/tickets?query=\"{query}\"&page={page}"
        print(f"📦 Fetching {start_date} → {end_date} | Page {page}")

        try:
            response = session.get(url, auth=AUTH, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            break

        result = response.json()
        tickets = result.get("results", [])
        if not tickets:
            break

        all_tickets.extend(tickets)
        page += 1
        time.sleep(1)

    return all_tickets

def write_tickets_to_csv(tickets, writer):
    for ticket in tickets:
        if ticket.get("group_id") in VALID_GROUP_IDS:
            cf = ticket.get("custom_fields", {})
            created_str = ticket.get("created_at", "")
            try:
                created_date = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                now_utc = datetime.now(timezone.utc)
                age_days = (now_utc - created_date).days
            except Exception:
                age_days = ""

            writer.writerow([
                ticket.get("id"),
                ticket.get("subject", ""),
                GROUP_MAP.get(ticket["group_id"], "Unknown"),
                ticket.get("status", ""),
                ticket.get("priority", ""),
                created_str,
                age_days,
                ", ".join(ticket.get("tags", [])),
                ticket.get("requester_email", ""),
                ticket.get("responder_id", ""),
                cf.get("cf_school_code", ""),
                cf.get("cf_priority_reason", ""),
                cf.get("cf_module", ""),
                ticket.get("type", "")
            ])

def run_full_export():
    start = datetime(2024, 4, 1, tzinfo=timezone.utc)
    end = datetime.now(timezone.utc)
    delta = timedelta(days=1)

    seen_ids = set()

    with open("all_unresolved_tickets_full.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "ID", "Subject", "Group Name", "Status", "Priority", "Created At",
            "Age (in Days)",
            "Tags", "Requester Email", "Responder ID",
            "School Code", "Priority Reason", "Module", "Type"
        ])

        while start < end:
            chunk_start = start.strftime("%Y-%m-%d")
            chunk_end = (start + delta).strftime("%Y-%m-%d")
            tickets = fetch_tickets_in_chunks(chunk_start, chunk_end)

            unique = [t for t in tickets if t["id"] not in seen_ids]
            seen_ids.update(t["id"] for t in unique)

            write_tickets_to_csv(unique, writer)
            start += delta

    print("✅ Export completed with de-duplicated ticket set including age.")

if __name__ == "__main__":
    run_full_export()
