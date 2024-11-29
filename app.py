import os
import requests
import base64
import json
import datetime
import ecdsa
import hashlib
from dotenv import load_dotenv
from api_request.json_request import evm_tx_native

load_dotenv() 
request_json = evm_tx_native()

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
