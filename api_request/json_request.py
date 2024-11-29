__all__ = ['tx']

from dotenv import load_dotenv

load_dotenv()

def evm_tx_native(vault_id, destination, custom_note, value):

    print(f"Preparing tx for {value} gwei!")

    """
    Native ETH transfer
    "580000000000000" wei = $2 USD of ETH

    """

    request_json = {
        "signer_type": "api_signer",
        "vault_id": vault_id,
        "note": custom_note,
        "type": "evm_transaction",
        "details": {
            "type": "evm_transfer",
            "gas": {
                "type": "priority",
                "priority_level": "medium"
            },
            "to": destination,
            "asset_identifier": {
                "type": "evm",
                "details": {
                    "type": "native",
                    "chain": "evm_ethereum_mainnet"
                }
            },
            "value": {
                "type": "value",
                "value": value
            }
        }
    }
    
    return request_json


def sol_tx_native(vault_id, destination, custom_note, value):

    print(f"Preparing transaction for {value} lamports!")

    request_json = {

    "signer_type": "api_signer",
    "type": "solana_transaction",
    "details": {
        "type": "solana_transfer",
        "to": destination,
        "value": {
            "type": "value",
            "value": value
        },
        "asset_identifier": {
            "type": "solana",
            "details": {
                "type": "native",
                "chain": "solana_mainnet"
            }
        }
    },
    "note": custom_note,
    "vault_id": vault_id
    }
    
    return request_json
