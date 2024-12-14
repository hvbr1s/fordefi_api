import os
import requests
import datetime
import json
import base64
import base58
import ecdsa
import hashlib
from api_requests.broadcast import get_tx

transaction_id = "76b3048c-4707-4e9b-8089-69ebb998d2e1"
access_token = os.getenv("FORDEFI_API_TOKEN")
path = f"/api/v1/transactions/{transaction_id}"
request_body = ""
private_key_file = "./secret/private.pem"
timestamp = datetime.datetime.now().strftime("%s")
payload = f"{path}|{timestamp}|{request_body}"

with open(private_key_file, "r") as f:
    signing_key = ecdsa.SigningKey.from_pem(f.read())

signature = signing_key.sign(
    data=payload.encode(), hashfunc=hashlib.sha256, sigencode=ecdsa.util.sigencode_der
)

# Fetch raw signature
fetch_raw_signature = get_tx(path, access_token, signature, timestamp, request_body)
raw_transaction_base64 = fetch_raw_signature['raw_transaction']
print(f"Raw signature -> {raw_transaction_base64}")

# Convert base64 to bytes, then to base58
raw_bytes = base64.b64decode(raw_transaction_base64)
raw_transaction_base58 = base58.b58encode(raw_bytes).decode('ascii')

# Jito API endpoint
url = "https://mainnet.block-engine.jito.wtf/api/v1/transactions"

# Prepare the request payload
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "sendTransaction",
    "params": [raw_transaction_base58]
}

# Set headers
headers = {
    "Content-Type": "application/json"
}

try:
    # Send POST request
    response = requests.post(url, headers=headers, json=payload)
    
    # Check if request was successful
    response.raise_for_status()
    
    # Parse response
    result = response.json()
    print(f"Successfully sent transaction to Jito. Response: {json.dumps(result, indent=2)}")
    
except requests.exceptions.RequestException as e:
    print(f"Error sending transaction: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response content: {e.response.text}")