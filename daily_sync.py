
import pandas as pd
from datetime import datetime
import requests
import time

API_KEY = "ntL1UBMbp66sgxrDXnD5"
DOMAIN = "entab"
AUTH = (API_KEY, "X")

MASTER_FILE = "all_unresolved_tickets_full.csv"
TODAY_FILE = "today_unresolved_tickets.csv"

def fetch_today_tickets():
    page = 1
    all_tickets = []
    while page <= 10:
        query = "(status:8 OR status:16)"
        url = f"https://{DOMAIN}.freshdesk.com/api/v2/search/tickets?query=\"{query}\"&page={page}"
        response = requests.get(url, auth=AUTH)
        if response.status_code != 200:
            print(f"❌ Error page {page}: {response.status_code}")
            break
        result = response.json()
        tickets = result.get("results", [])
        if not tickets:
            break
        for ticket in tickets:
            all_tickets.append({
                "ID": ticket.get("id"),
                "Subject": ticket.get("subject"),
                "Status": ticket.get("status"),
                "Created At": ticket.get("created_at"),
                "Last Seen": datetime.today().strftime("%Y-%m-%d"),
                "Status Today": "Active"
            })
        page += 1
        time.sleep(1)
    df_today = pd.DataFrame(all_tickets)
    df_today.to_csv(TODAY_FILE, index=False)
    return df_today

def compare_with_full_export(df_today):
    try:
        df_master = pd.read_csv(MASTER_FILE)
    except FileNotFoundError:
        print("📄 Master file not found.")
        return
    today_ids = set(df_today["ID"])
    master_ids = set(df_master["ID"])

    new_ids = today_ids - master_ids
    df_new = df_today[df_today["ID"].isin(new_ids)]
    df_new.to_csv("new_tickets_today.csv", index=False)

    closed_ids = master_ids - today_ids
    df_closed = df_master[df_master["ID"].isin(closed_ids)].copy()
    df_closed["Status Today"] = "Closed"
    df_closed["Last Seen"] = datetime.today().strftime("%Y-%m-%d")
    df_closed.to_csv("closed_tickets_today.csv", index=False)

    print(f"🆕 New Tickets: {len(df_new)}")
    print(f"❌ Closed Tickets: {len(df_closed)}")

def run_daily_sync_against_full_export():
    print("📥 Fetching today's unresolved tickets...")
    df_today = fetch_today_tickets()
    print("🔍 Comparing with full export data...")
    compare_with_full_export(df_today)
    print("✅ Daily sync complete.")

if __name__ == "__main__":
    run_daily_sync_against_full_export()
