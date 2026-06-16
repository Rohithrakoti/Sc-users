import requests
import base64
import csv
import json
import urllib3

# Ignore SSL certificate warnings for internal ADO server
urllib3.disable_warnings()

# ==================================================
# Configuration
# ==================================================
ADO_URL = "https://ado.global.standardchartered.com/sc-ado-op"
PAT = "YOUR_PAT_TOKEN"
GROUP_NAME = "All ADO Users"

# ==================================================
# Authentication
# ==================================================
token = base64.b64encode(f":{PAT}".encode()).decode()

headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json"
}

# ==================================================
# Step 1 - Find "All ADO Users" group
# ==================================================
group_url = (
    f"{ADO_URL}/_apis/identities"
    f"?searchFilter=General"
    f"&filterValue={GROUP_NAME}"
    f"&queryMembership=None"
    f"&api-version=7.1-preview.1"
)

response = requests.get(group_url, headers=headers, verify=False)

if response.status_code != 200:
    print("Failed to find group")
    print(response.status_code)
    print(response.text)
    exit()

data = response.json()

groups = data.get("value", [])

if not groups:
    print("All ADO Users group not found")
    exit()

group = groups[0]

group_name = (
    group.get("displayName")
    or group.get("FriendlyDisplayName")
    or group.get("providerDisplayName")
    or group.get("customDisplayName")
    or "Unknown Group"
)

group_id = (
    group.get("id")
    or group.get("TeamFoundationId")
    or group.get("teamFoundationId")
)

print("\nGroup found:", group_name)
print("Group ID:", group_id)

if not group_id:
    print("Could not get Group ID")
    exit()


# ==================================================
# Step 2 - Get group details with membership expanded
# ==================================================
members_url = (
    f"{ADO_URL}/_apis/identities"
    f"?identityIds={group_id}"
    f"&queryMembership=Expanded"
    f"&api-version=7.1-preview.1"
)

response = requests.get(
    members_url,
    headers=headers,
    verify=False
)

if response.status_code != 200:
    print("Failed to get members")
    print(response.status_code)
    print(response.text)
    exit()

members_data = response.json()

print("\nMembership API response:")
print(json.dumps(members_data, indent=2))


# ==================================================
# Step 3 - Extract members
# ==================================================
identities = members_data.get("value", [])

members = []

for item in identities:
    for member in item.get("members", []):
        members.append(member)

print("\nTotal members found:", len(members))


# ==================================================
# Step 4 - Export CSV
# ==================================================
csv_file = "All_ADO_Users.csv"

with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "Display Name",
        "Unique Name",
        "Descriptor"
    ])

    for user in members:
        writer.writerow([
            user.get("displayName")
            or user.get("FriendlyDisplayName", ""),
            user.get("uniqueName", ""),
            user.get("descriptor", "")
        ])

print("\nExport completed successfully")
print("CSV created:", csv_file)
