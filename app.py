import os
import json
import datetime
import ecdsa
import hashlib
from dotenv import load_dotenv
from api_request.json_request import evm_tx_native, sol_tx_native
from api_request.broadcast import broadcast_tx

load_dotenv()

## User inputs

vault_id = input("👋 Welcome! Please enter the vault ID name: ").strip().lower()
destination =  input("🚚 Sounds good! Where should we send the funds to? ").strip()

while True:
    ecosystem = input("🌐 Great! On which network should we broadcast the transaction? (SOL/EVM): ").strip().lower()
    if ecosystem in ["sol", "evm"]:
        break
    else:
        print("❌ Invalid input. Please choose SOL or EVM")

value =  input("🌐 Ok! How much would you like to spend? Please use SOL or ETH as unit: ").strip().lower()

custom_note = input("🗒️  Would you like to add a note? ").strip().lower()
        
print(f"🚀 Excellent! Sending from Vault {vault_id.capitalize()} to {destination} on {ecosystem.upper()}.")

## Building transaction

if ecosystem == "sol":
    try:
        value = value.replace(",", ".")
        float_value = float(value)
        lamports = int(float_value * 1_000_000_000)  # Convert to lamports
        assert lamports > 0, "SOL amount must be positive!" 
        print(f"Sending {float_value} SOL!")
        value = str(lamports) 
    except ValueError:
        print("❌ Invalid SOL amount provided")
        exit(1)
    request_json = sol_tx_native(vault_id, destination, custom_note, value)
elif ecosystem == "evm":
    try:
        value = value.replace(",", ".")
        float_value = float(value)
        wei = int(float_value * 1_000_000_000_000_000_000)  # Convert to Wei
        assert wei > 0, "ETH amount must be positive!"
        print(f"Sending {float_value} ETH!")
        value = str(wei) 
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

try:
    resp_tx = broadcast_tx(path, access_token, signature, timestamp, request_body)
    print("✅ Transaction submitted successfully!")
    print(f"Transaction ID: {resp_tx.json().get('id', 'N/A')}")
    
except RuntimeError as e:
    print(f"❌ {str(e)}")
    exit(1)
except json.JSONDecodeError as e:
    print(f"❌ Failed to parse response: {str(e)}")
    print(f"Raw response: {resp_tx.text}")
    exit(1)

# Local start command: uvicorn app:app --reload --port 8800