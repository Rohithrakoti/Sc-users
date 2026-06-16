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
PAT = "YOUR_NEW_PAT_TOKEN"   # Replace with your new PAT
GROUP_NAME = "All ADO Users"

# ==================================================
# Authentication
# ==================================================
auth_token = base64.b64encode(f":{PAT}".encode()).decode()

headers = {
    "Authorization": f"Basic {auth_token}",
    "Content-Type": "application/json"
}


# ==================================================
# Step 1 - Find All ADO Users Group
# ==================================================
print("Finding ADO group...")

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
    print(response.text)
    exit()

groups = response.json().get("value", [])

if not groups:
    print("All ADO Users group not found")
    exit()

group = groups[0]

group_name = (
    group.get("displayName")
    or group.get("FriendlyDisplayName")
    or group.get("providerDisplayName")
    or "Unknown"
)

group_id = (
    group.get("id")
    or group.get("TeamFoundationId")
)

print(f"Group found: {group_name}")
print(f"Group ID: {group_id}")


# ==================================================
# Step 2 - Get all members of the group
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

if response.status_code != 200:
    print("Failed to get members")
    print(response.text)
    exit()

identity_data = response.json().get("value", [])

members = []

for item in identity_data:
    for member in item.get("members", []):
        members.append(member)

print(f"Total members returned: {len(members)}")


# ==================================================
# Step 3 - Resolve members and export ADO users
# ==================================================
print("\nExporting ADO users...")

csv_file = "All_ADO_Users.csv"

exported = 0
skipped = 0

with open(csv_file, "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Display Name",
        "Account Name",
        "Unique Name",
        "Team Foundation ID"
    ])

    for member_id in members:

        # Skip Windows SID identities
        if "System.Security.Principal.WindowsIdentity" in member_id:
            skipped += 1
            continue

        user_url = (
            f"{ADO_URL}/_apis/identities"
            f"?identityIds={member_id}"
            f"&api-version=7.1-preview.1"
        )

        try:
            response = requests.get(
                user_url,
                headers=headers,
                verify=False,
                timeout=15
            )

            if response.status_code != 200:
                skipped += 1
                continue

            users = response.json().get("value", [])

            if not users:
                skipped += 1
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

            # Ignore empty or invalid records
            if not display_name:
                skipped += 1
                continue

            writer.writerow([
                display_name,
                account_name,
                unique_name,
                tf_id
            ])

            exported += 1

            if exported % 100 == 0:
                print(f"Exported {exported} users...")

        except Exception as e:
            print(f"Error processing member: {member_id}")
            skipped += 1


# ==================================================
# Summary
# ==================================================
print("\n====================================")
print(f"Total members in group : {len(members)}")
print(f"ADO users exported     : {exported}")
print(f"Skipped identities     : {skipped}")
print(f"CSV file created       : {csv_file}")
print("====================================")
