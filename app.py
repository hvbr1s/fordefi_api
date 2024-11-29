import os
import requests
import base64
import json
import datetime
import ecdsa
import hashlib
from dotenv import load_dotenv
from api_request.json_request import evm_tx_native, sol_tx_native

load_dotenv()

## User inputs

vault_id = input("👋 Welcome! Please enter the vault ID name: ").strip().lower()
destination =  input("🚚 Sounds good! Where should we send the funds to?")

while True:
    ecosystem = input("🌐 Great! On which network should we broadcast the transaction? (SOL/EVM): ").strip().lower()
    if ecosystem in ["sol", "evm"]:
        break
    else:
        print("❌ Invalid input. Please choose SOL or EVM")

value =  input("🌐 Ok! How much would you like to spend? Please use SOL or ETH as unit").strip().lower()

custom_note = input("🗒️ Would you like to add a note? ").strip().lower()
        
print(f"🚀 Excellent! Sending from Vault -> {vault_id.capitalize()} to {destination} on {ecosystem}.")

## Building transaction

if ecosystem == "sol":
    try:
        value = value.replace(",", ".")
        value = int(float(value) * 1_000_000_000)  # Convert to lamports
    except ValueError:
        print("❌ Invalid SOL amount provided")
        exit(1)
    request_json = sol_tx_native(vault_id, destination, custom_note, value)
elif ecosystem == "evm":
    try:
        value = value.replace(",", ".")
        value = int(float(value) * 1_000_000_000_000_000_000)  # Convert to Wei (1 ETH = 10^18 Wei)
    except ValueError:
        print("❌ Invalid ETH amount provided")
        exit(1)
    request_json = evm_tx_native(vault_id, destination, custom_note, value)

## Broadcasting transaction

access_token = os.getenv("FORDEFI_API_TOKEN")
request_body = json.dumps(request_json)
private_key_file = "./secret/private.pem"
path = "/api/v1/transactions"
timestamp = datetime.datetime.now().strftime("%s")
payload = f"{path}|{timestamp}|{request_body}"

with open(private_key_file, "r") as f:
    signing_key = ecdsa.SigningKey.from_pem(f.read())

signature = signing_key.sign(
    data=payload.encode(), hashfunc=hashlib.sha256, sigencode=ecdsa.util.sigencode_der
)

resp_tx = requests.post(
    f"https://api.fordefi.com{path}",
    headers={
        "Authorization": f"Bearer {access_token}",
        "x-signature": base64.b64encode(signature),
        "x-timestamp": timestamp.encode(),
    },
    data=request_body,
)

# Local start command: uvicorn app:app --reload --port 8800