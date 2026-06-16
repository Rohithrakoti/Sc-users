import requests
import base64
import csv
import urllib3

# Ignore SSL warnings for internal ADO server
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
print("Finding All ADO Users group...")

group_url = (
    f"{ADO_URL}/_apis/identities"
    f"?searchFilter=General"
    f"&filterValue={GROUP_NAME}"
    f"&queryMembership=None"
    f"&api-version=7.1-preview.1"
)

response = requests.get(group_url, headers=headers, verify=False)
response.raise_for_status()

groups = response.json().get("value", [])

if not groups:
    print("Group not found")
    exit()

group = groups[0]

group_name = (
    group.get("displayName")
    or group.get("FriendlyDisplayName")
    or group.get("providerDisplayName")
    or "Unknown Group"
)

group_id = (
    group.get("id")
    or group.get("TeamFoundationId")
)

print(f"Group found: {group_name}")
print(f"Group ID: {group_id}")


# ==================================================
# Step 2 - Get group members
# ==================================================
print("\nGetting group members...")

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

response.raise_for_status()

identity_data = response.json().get("value", [])

members = []

for item in identity_data:
    # In ADO OP, members are returned as IDs
    for member_id in item.get("members", []):
        members.append(member_id)

print(f"Total members found: {len(members)}")


# ==================================================
# Step 3 - Resolve member IDs and export CSV
# ==================================================
print("\nExporting users to CSV...")

csv_file = "All_ADO_Users.csv"

with open(csv_file, "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Display Name",
        "Account Name",
        "Unique Name",
        "Team Foundation ID"
    ])

    count = 0

    for member_id in members:

        user_url = (
            f"{ADO_URL}/_apis/identities"
            f"?identityIds={member_id}"
            f"&api-version=7.1-preview.1"
        )

        try:
            response = requests.get(
                user_url,
                headers=headers,
                verify=False
            )

            if response.status_code != 200:
                print(f"Skipping {member_id} - HTTP {response.status_code}")
                continue

            users = response.json().get("value", [])

            if not users:
                continue

            user = users[0]

            display_name = (
                user.get("displayName")
                or user.get("FriendlyDisplayName")
                or user.get("providerDisplayName")
                or ""
            )

            account_name = (
                user.get("providerDisplayName")
                or ""
            )

            unique_name = (
                user.get("uniqueName")
                or ""
            )

            tf_id = (
                user.get("TeamFoundationId")
                or user.get("id")
                or ""
            )

            writer.writerow([
                display_name,
                account_name,
                unique_name,
                tf_id
            ])

            count += 1

            if count % 100 == 0:
                print(f"Processed {count} users...")

        except Exception as e:
            print(f"Error processing {member_id}: {e}")

print("\n================================")
print("Export completed successfully")
print(f"Users exported: {count}")
print(f"CSV file: {csv_file}")
print("================================")
