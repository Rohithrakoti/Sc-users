import requests
import base64
import json
import urllib3

urllib3.disable_warnings()

ADO_URL = "https://ado.global.standardchartered.com/sc-ado-op"
PAT = "YOUR_NEW_PAT"

SID = "System.Security.Principal.WindowsIdentity;S-1-5-21-3226412287-358294239-3603207364-1349750"

token = base64.b64encode(f":{PAT}".encode()).decode()

headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json"
}

url = (
    f"{ADO_URL}/_api/_identity/ReadIdentities"
    f"?descriptors={SID}"
)

response = requests.get(
    url,
    headers=headers,
    verify=False
)

print("Status:", response.status_code)
print(json.dumps(response.json(), indent=2))
