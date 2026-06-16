import requests
import base64
import csv
import urllib3
import urllib.parse
import time

# Ignore SSL warnings
urllib3.disable_warnings()

# ==============================
# Configuration
# ==============================
ADO_URL = "https://ado.global.standardchartered.com/sc-ado-op"
PAT = "YOUR_PAT_HERE"

GROUP_ID = "f2d207aa-884a-490b-9dba-dce325bb4804"

# ==============================
# Authentication
# ==============================
token = base64.b64encode(f":{PAT}".encode()).decode()

headers = {
    "Authorization": f"Basic {token}"
}

# ==============================
# Get all users
# ==============================
all_users = []
last_search_result = None
page = 1

while True:

    url = (
        f"{ADO_URL}/_api/_identity/ReadGroupMembers"
        f"?_v=5"
        f"&scope={GROUP_ID}"
        f"&readMembers=true"
    )

    # Add pagination value
    if last_search_result:
        url += "&lastSearchResult=" + urllib.parse.quote(last_search_result)

    print(f"\nGetting page {page}")
    print(url)

    response = requests.get(
        url,
        headers=headers,
        verify=False
    )

    if response.status_code != 200:
        print("Failed:", response.status_code)
        print(response.text)
        break

    data = response.json()

    # ==========================
    # Extract users recursively
    # ==========================
    page_users = []

    def find_users(obj):
        if isinstance(obj, dict):

            if "FriendlyDisplayName" in obj:
                user = {
                    "Display Name": obj.get("FriendlyDisplayName", ""),
                    "Domain": obj.get("Domain", ""),
                    "Account Name": obj.get("AccountName", ""),
                    "Windows User": obj.get("IsWindowsUser", "")
                }

                page_users.append(user)

            for value in obj.values():
                find_users(value)

        elif isinstance(obj, list):
            for item in obj:
                find_users(item)

    find_users(data)

    print(f"Users found in page: {len(page_users)}")

    if not page_users:
        break

    all_users.extend(page_users)

    # Check if more pages exist
    has_more = data.get("hasMore", False)

    print("Has more:", has_more)

    if not has_more:
        break

    # Use last user display name for next request
    last_search_result = page_users[-1]["Display Name"]

    print("Next page starts after:", last_search_result)

    page += 1

    # small delay
    time.sleep(0.5)


# ==============================
# Remove duplicates
# ==============================
unique_users = []
seen = set()

for user in all_users:
    key = (
        user["Domain"],
        user["Account Name"]
    )

    if key not in seen:
        seen.add(key)
        unique_users.append(user)


# ==============================
# Export CSV
# ==============================
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
            "Domain",
            "Account Name",
            "Windows User"
        ]
    )

    writer.writeheader()
    writer.writerows(unique_users)


# ==============================
# Summary
# ==============================
print("\n================================")
print("Export completed successfully")
print("Total users collected :", len(all_users))
print("Unique users exported :", len(unique_users))
print("CSV file created      :", csv_file)
print("================================")
