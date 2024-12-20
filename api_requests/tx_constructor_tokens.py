__all__ = ['evm_tx_tokens', 'sol_tx_tokens']

from dotenv import load_dotenv

load_dotenv()

def evm_tx_tokens(evm_chain, vault_id, destination, custom_note, value, token):

    print(f"Preparing to send {value} {token} on {evm_chain}")

    if evm_chain == "arbitrum" and token =="usdc":
        contract_address = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"
    else:
        contract_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48" # USDC contract address on Ethereum mainnet

    request_json =  {
    "signer_type": "api_signer",
    "type": "evm_transaction",
    "details": {
        "type": "evm_transfer",
        "gas": {
          "type": "priority",
          "priority_level": "medium"
        },
        "to": destination,
        "value": {
           "type": "value",
           "value": value
        },
        "asset_identifier": {
             "type": "evm",
             "details": {
                 "type": "erc20",
                 "token": {
                     "chain": f"evm_{evm_chain}_mainnet",
                     "hex_repr": contract_address
                 }
             }
        }
    },
    "note": custom_note,
    "vault_id": vault_id
}

    return request_json

def sol_tx_tokens(vault_id, destination, custom_note, value, token):

    print(f"Sending {value} {token} from {vault_id} to {destination}")

    if token =="usdc":
        program_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    else:
        program_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

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
                    "type": "spl_token",
                    "token": {
                        "chain": "solana_mainnet",
                        "base58_repr": program_address
                    }
                }
            }
        },
        "note": custom_note,
        "vault_id": vault_id
    }


    return request_json