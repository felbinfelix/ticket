import requests

# Freshdesk credentials
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

# Status categories
UNRESOLVED_STATUS_IDS = [
    2, 3, 4, 6, 7, 8, 9, 10, 11,
    12, 13, 14, 16, 17, 20, 21,
    23, 24, 25, 26
]

CLOSED_STATUS_IDS = [5, 27]

def get_ticket_count(group_id, status_ids):
    url = f"https://{DOMAIN}.freshdesk.com/api/v2/search/tickets"
    status_query = " OR ".join([f"status:{s}" for s in status_ids])
    query = f'"group_id:{group_id} AND ({status_query})"'
    params = {"query": query}

    response = requests.get(url, auth=AUTH, params=params)
    if response.status_code == 200:
        return response.json().get("total", 0)
    else:
        print(f"Error for group {group_id}: {response.status_code} - {response.text}")
        return 0

# Run and print result
if __name__ == "__main__":
    print(f"{'Group':<25} | {'Unresolved':>10} | {'Closed':>6} | {'Total':>6}")
    print("-" * 60)
    for group_id, group_name in GROUPS.items():
        unresolved = get_ticket_count(group_id, UNRESOLVED_STATUS_IDS)
        closed = get_ticket_count(group_id, CLOSED_STATUS_IDS)
        total = unresolved + closed
        print(f"{group_name:<25} | {unresolved:>10} | {closed:>6} | {total:>6}")
