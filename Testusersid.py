import requests
import base64
import urllib3

urllib3.disable_warnings()

ADO_URL = "https://ado.global.standardchartered.com/sc-ado-op"
PAT = "YOUR_NEW_PAT"

# Take one SID from your output
SID = "S-1-5-21-3226412287-358294239-3603207364-1349750"

token = base64.b64encode(f":{PAT}".encode()).decode()

headers = {
    "Authorization": f"Basic {token}"
}

url = (
    f"{ADO_URL}/_apis/identities"
    f"?searchFilter=General"
    f"&filterValue={SID}"
    f"&api-version=7.1-preview.1"
)

response = requests.get(
    url,
    headers=headers,
    verify=False
)

print("Status Code:", response.status_code)
print("Response:")
print(response.text)
