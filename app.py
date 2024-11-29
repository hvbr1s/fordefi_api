import os
import json
import datetime
import ecdsa
import hashlib
from dotenv import load_dotenv
from api_requests.tx_constructor import evm_tx_native, sol_tx_native, sui_tx_native, ton_tx_native
from api_requests.broadcast import broadcast_tx

load_dotenv()

## User interface
vault_id = input("👋 Welcome! Please enter the vault ID name: ").strip().lower() or "default"
destination =  input("🚚 Sounds good! Where should we send the funds to? ").strip() or "default"

while True:
    ecosystem = input("🌐 Great! On which network should we broadcast the transaction? (SOL/EVM/SUI/TON): ").strip().lower()
    if ecosystem in ["sol", "evm", "sui", "ton"]:
        break
    else:
        print("❌ Invalid input. Please choose SOL or EVM")

value =  input("🌐 Ok! How much would you like to spend? Please use SOL, SUI, TON or ETH as unit: ").strip().lower()

custom_note = input("🗒️  Would you like to add a note? ").strip().lower() or "note!"
        
print(f"🚀 Excellent! Sending from vault {vault_id} to {destination} on {ecosystem.upper()}.")

## Building transaction

if ecosystem == "sol":
    try:
        if vault_id == "default":
            vault_id = os.getenv("SOL_VAULT_ID") # default vault
        if destination == "default":
            destination = "8o6kJ9gPNMnRAgdyWLt6Pd1khnb5yfTYtvSz313cN9Lp"
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
        if vault_id == "default":
            vault_id = os.getenv("EVM_VAULT_ID") # default vault
        if destination == "default":
            destination = "0x83c1C2a52d56dFb958C52831a3D683cFAfC34c75"
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
elif ecosystem == "sui":
    try:
        if vault_id == "default":
            vault_id = os.getenv("SUI_VAULT_ID")
        if destination == "default":
            destination = "0xa1af935c826ec92f50da6c4eb9e880b12c18c154f546a993830ee7f000c842bc"
        value = value.replace(",", ".")
        float_value = float(value)
        mist = int(float_value * 1_000_000_000)  # Convert to Mist
        assert mist > 0, "SUI amount must be positive!"
        print(f"Sending {float_value} SUI!")
        value = str(mist) 
    except ValueError:
        print("❌ Invalid SUI amount provided")
        exit(1)
    request_json = sui_tx_native(vault_id, destination, custom_note, value)
elif ecosystem == "ton":
    try:
        if vault_id == "default":
            vault_id = os.getenv("TON_VAULT_ID")
        if destination == "default":
            destination = "UQCXmikxWsyKnP-3yQVAUiu94NGtjAKug4tsiFO1jZ6jOjmt"
        value = value.replace(",", ".")
        float_value = float(value)
        mist = int(float_value * 1_000_000_000)  # Convert to Nanoton
        assert mist > 0, "TON amount must be positive!"
        print(f"Sending {float_value} TON!")
        value = str(mist) 
    except ValueError:
        print("❌ Invalid TON amount provided")
        exit(1)
    request_json = ton_tx_native(vault_id, destination, custom_note, value)

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