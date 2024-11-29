__all__ = ['tx']

import os
from dotenv import load_dotenv

load_dotenv()

def evm_tx_native():

    """
    Native ETH transfer
    "580000000000000" wei = $2 USD of ETH

    """

    request_json = {
        "signer_type": "api_signer",
        "vault_id": os.getenv("EVM_VAUL_ID"),
        "note": "hello mom",
        "type": "evm_transaction",
        "details": {
            "type": "evm_transfer",
            "gas": {
                "type": "priority",
                "priority_level": "medium"
            },
            "to": "0x83c1C2a52d56dFb958C52831a3D683cFAfC34c75",
            "asset_identifier": {
                "type": "evm",
                "details": {
                    "type": "native",
                    "chain": "evm_ethereum_mainnet"
                }
            },
            "value": {
                "type": "value",
                "value": "580000000000000"
            }
        }
    }
    
    return request_json


def sol_tx_native():

    request_json = {

    "signer_type": "api_signer",
    "type": "solana_transaction",
    "details": {
        "type": "solana_transfer",
        "to": "8o6kJ9gPNMnRAgdyWLt6Pd1khnb5yfTYtvSz313cN9Lp",
        "value": {
            "type": "value",
            "value": "2780000"
        },
        "asset_identifier": {
            "type": "solana",
            "details": {
                "type": "native",
                "chain": "solana_mainnet"
            }
        }
    },
    "note": "Testing transfers!",
    "vault_id": os.getenv("SOL_VAULT_ID")
    }
    
    return request_json
