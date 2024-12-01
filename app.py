import os
import json
import datetime
import ecdsa
import hashlib
from dotenv import load_dotenv
from api_requests.broadcast import broadcast_tx
from utils.tx_processor import process_transaction

load_dotenv()

## User interface

vault_id = input("👋 Welcome! Please enter the vault ID name: ").strip().lower() or "default"
destination =  input("🚚 Sounds good! What is the destination address? ").strip() or "default"

evm_chain = None
token = None
while True:
    ecosystem = input("🌐 Great! On which network should we broadcast the transaction? (SOL/EVM/SUI/TON): ").strip().lower()
    if ecosystem == "evm":
        evm_chain =  input("🌐 Which EVM chain? ").strip().lower() or "ethereum"
        if evm_chain in ["arbitrum", "optimism", "ethereum"]:
            break
        else:
            print("❌ Invalid input. Please choose Arbitrum, Optimism, Ethereum")              
    elif ecosystem in ["sol", "sui", "ton"]:
        break
    else:
        print("❌ Invalid input. Please choose SOL, EVM, SUI, TON")

token = input("🪙 What is the token ticker? If not a token press return: ").strip().lower() or None

value =  input("🌐 Ok! How much would you like to spend? ").strip().lower()

custom_note = input("🗒️  Would you like to add a note? ").strip().lower() or "note!"
        
print(f"🚀 Excellent! Sending from vault {vault_id} to {destination} on {ecosystem.upper()} -> {evm_chain}.")

## Building transaction

request_json = process_transaction(ecosystem, evm_chain, vault_id, destination, value, custom_note, token)

## Broadcast transaction

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