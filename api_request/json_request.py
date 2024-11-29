__all__ = ['tx']

import os
from dotenv import load_dotenv

load_dotenv()

def tx():

    request_json = {
        "vault_id": os.getenv("FORDEFI_API_TOKEN"),
        "note": "Hello Mom!",
        "signer_type": "api_signer",
        "type": "evm_transaction",
        "details": {
            "type": "evm_raw_transaction",
            "use_secure_node": False,
            "chain": "ethereum_mainnet",
            "gas": {
                "type": "priority",
                "priority_level": "medium"
            },
            "to": "0x83c1C2a52d56dFb958C52831a3D683cFAfC34c75",
            "value": "0",
            "data": {
                "type": "full_details",
                "method_name": "mintPublic",
                "method_arguments": {
                    "quantity": "6"
                }
            }
        }
    }
    
    return request_json
