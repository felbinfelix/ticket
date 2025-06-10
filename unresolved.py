import requests

# Freshdesk API credentials
API_KEY = "ntL1UBMbp66sgxrDXnD5"
DOMAIN = "entab"
AUTH = (API_KEY, "X")

# Group ID to Name mapping
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

# Ticket types from Freshdesk config
TICKET_TYPES = [
    "Query", "Incident", "Change Request", "Deviation", "3rd Party Instance",
    "Proactive Task", "Call Transfer", "Prod. Enhancement", "Wishlist",
    "Escalation", "VOC (Voice of Customer)", "Integration", "New Website"
]

# Status IDs considered unresolved (exclude 5 = Closed, 27 = Not Feasible)
UNRESOLVED_STATUS_IDS = [
    2, 3, 4, 6, 7, 8, 9, 10, 11,
    12, 13, 14, 16, 17, 20, 21,
    23, 24, 25, 26
]

def fetch_all_unresolved_tickets(group_id):
    url = f"https://{DOMAIN}.freshdesk.com/api/v2/search/tickets"
    status_query = " OR ".join([f"status:{s}" for s in UNRESOLVED_STATUS_IDS])
    query = f'"group_id:{group_id} AND ({status_query})"'

    tickets = []
    page = 1

    while True:
        params = {"query": query, "page": page}
        response = requests.get(url, auth=AUTH, params=params)

        if response.status_code != 200:
            print(f"❌ Error fetching tickets for group {group_id}: {response.status_code} - {response.text}")
            break

        data = response.json()
        results = data.get("results", [])
        tickets.extend(results)

        if len(results) < 30:
            break  # No more pages
        page += 1

    return tickets

def count_types(tickets):
    type_count = {}
    for t in tickets:
        t_type = t.get("type", "Unspecified")
        type_count[t_type] = type_count.get(t_type, 0) + 1
    return type_count

# Print Report
print(f"{'Group':<25} | {'Ticket Type':<25} | {'Count':>5}")
print("-" * 60)

for group_id, group_name in GROUPS.items():
    tickets = fetch_all_unresolved_tickets(group_id)
    type_counts = count_types(tickets)

    for t_type in TICKET_TYPES:
        count = type_counts.get(t_type, 0)
        if count > 0:
            print(f"{group_name:<25} | {t_type:<25} | {count:>5}")
