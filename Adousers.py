import requests
import base64
import csv
import json
import urllib3

# Ignore SSL warnings (for internal ADO servers)
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
# Step 1 - Find All ADO Users group
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

print("Group API Response:")
print(json.dumps(data, indent=2))

groups = data.get("value", [])

if not groups:
    print("All ADO Users group not found")
    exit()

group = groups[0]

# Try different possible field names
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

print(f"\nFound Group: {group_name}")
print(f"Group ID: {group_id}")

if not group_id:
    print("Could not identify group ID. Check the API response above.")
    exit()

# ==================================================
# Step 2 - Get group members
# ==================================================
members_url = (
    f"{ADO_URL}/_apis/identities"
    f"?searchFilter=Membership"
    f"&filterValue={group_id}"
    f"&queryMembership=Direct"
    f"&api-version=7.1-preview.1"
)

response = requests.get(members_url, headers=headers, verify=False)

if response.status_code != 200:
    print("Failed to get members")
    print(response.status_code)
    print(response.text)
    exit()

members_data = response.json()

print("\nMembers API Response:")
print(json.dumps(members_data, indent=2))

members = members_data.get("value", [])

print(f"\nTotal members found: {len(members)}")

# ==================================================
# Step 3 - Export CSV
# ==================================================
csv_file = "All_ADO_Users.csv"

with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "Display Name",
        "Unique Name",
        "Domain",
        "Descriptor"
    ])

    for user in members:
        display_name = (
            user.get("displayName")
            or user.get("FriendlyDisplayName")
            or user.get("providerDisplayName")
            or user.get("customDisplayName")
            or ""
        )

        unique_name = (
            user.get("uniqueName")
            or user.get("providerDisplayName")
            or ""
        )

        domain = user.get("domain", "")

        descriptor = (
            user.get("descriptor")
            or user.get("id")
            or user.get("TeamFoundationId")
            or ""
        )

        writer.writerow([
            display_name,
            unique_name,
            domain,
            descriptor
        ])

print(f"\nExport completed successfully.")
print(f"CSV File Created: {csv_file}")
