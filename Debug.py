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

print(f"\nTotal members returned: {len(members)}")


# ==================================================
# DEBUG - Check member format
# ==================================================
print("\nFirst 20 members returned:\n")

for index, member in enumerate(members[:20], start=1):
    print(f"{index}. {member}")

exit()
