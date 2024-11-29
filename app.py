import os
import json
import datetime
import ecdsa
import hashlib
from dotenv import load_dotenv
from api_requests.tx_constructor import evm_tx_native, sol_tx_native, sui_tx_native, ton_tx_native
from api_requests.broadcast import broadcast_tx
from utils.ecosysten_configs import get_ecosystem_config

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

def process_transaction(ecosystem, vault_id, destination, value, custom_note):
    config = get_ecosystem_config(ecosystem)
    if not config:
        raise ValueError("Invalid ecosystem")

    if vault_id == "default":
        vault_id = os.getenv(config["vault_env"])
    if destination == "default":
        destination = config["default_dest"]

    try:
        value = value.replace(",", ".")
        float_value = float(value)
        smallest_unit = int(float_value * config["decimals"])
        assert smallest_unit > 0, f"{config['unit_name']} amount must be positive!"
        print(f"Sending {float_value} {config['unit_name']}!")
        
        tx_functions = {
            "sol": sol_tx_native,
            "evm": evm_tx_native,
            "sui": sui_tx_native,
            "ton": ton_tx_native
        }
        
        return tx_functions[ecosystem](vault_id, destination, custom_note, str(smallest_unit))
    except ValueError:
        print(f"❌ Invalid {config['unit_name']} amount provided")
        exit(1)


request_json = process_transaction(ecosystem, vault_id, destination, value, custom_note)

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