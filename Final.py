import requests
import base64
import csv
import urllib3
import json

# Ignore SSL warnings
urllib3.disable_warnings()

# =====================================
# Configuration
# =====================================
ADO_URL = "https://ado.global.standardchartered.com/sc-ado-op"
PAT = "YOUR_NEW_PAT"

# All ADO Users Group ID
GROUP_ID = "f2d207aa-884a-490b-9dba-dce325bb4804"


# =====================================
# Authentication
# =====================================
token = base64.b64encode(
    f":{PAT}".encode()
).decode()

headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json"
}


# =====================================
# Read All ADO Users
# =====================================
url = (
    f"{ADO_URL}/_api/_identity/ReadGroupMembers"
    f"?_v=5"
    f"&scope={GROUP_ID}"
    f"&readMembers=true"
)

print("Getting All ADO Users...")

response = requests.get(
    url,
    headers=headers,
    verify=False
)

print("Status:", response.status_code)

if response.status_code != 200:
    print(response.text)
    exit()


data = response.json()

# Uncomment if you want to see full response
# print(json.dumps(data, indent=2))


# =====================================
# Extract users
# =====================================

users = []

def extract_users(obj):
    """
    Recursively find user objects
    """
    if isinstance(obj, dict):
        if "FriendlyDisplayName" in obj:
            users.append({
                "Display Name": obj.get("FriendlyDisplayName", ""),
                "Username": obj.get("SubHeader", ""),
                "Team Foundation ID": obj.get("TeamFoundationId", "")
            })

        for value in obj.values():
            extract_users(value)

    elif isinstance(obj, list):
        for item in obj:
            extract_users(item)


extract_users(data)

print(f"Users found: {len(users)}")


# Remove duplicates
unique_users = []
seen = set()

for user in users:
    key = (
        user["Display Name"],
        user["Username"]
    )

    if key not in seen:
        seen.add(key)
        unique_users.append(user)


# =====================================
# Export CSV
# =====================================

csv_file = "All_ADO_Users.csv"

with open(
    csv_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "Display Name",
            "Username",
            "Team Foundation ID"
        ]
    )

    writer.writeheader()
    writer.writerows(unique_users)


print("================================")
print("Export completed successfully")
print(f"Total users exported: {len(unique_users)}")
print(f"CSV created: {csv_file}")
print("================================")
