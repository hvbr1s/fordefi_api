__all__ = ['process_transaction']

from api_requests.tx_constructor import evm_tx_native, sol_tx_native, sui_tx_native, ton_tx_native, aptos_tx_native, btc_tx_native
from api_requests.tx_constructor_tokens import evm_tx_tokens, sol_tx_tokens
from utils.ecosysten_configs import get_ecosystem_config
import os

def process_transaction(ecosystem, evm_chain, vault_id, destination, value, custom_note, token):
    config = get_ecosystem_config(ecosystem)
    if not config:
        raise ValueError("Invalid ecosystem")

    if vault_id == "default":
        vault_id = os.getenv(config["vault_env"])
        print(f"Sending from vault {vault_id}")
    if destination == "default":
        destination = config["default_dest"]

    try:
        value = value.replace(",", ".")
        float_value = float(value)
        if token:
            smallest_unit = int(float_value * 1_000_000)
            assert smallest_unit > 0, f"{token} amount must be positive!"
            print(f"Sending {float_value} {token}!")
        else:
            smallest_unit = int(float_value * config["decimals"])
            assert smallest_unit > 0, f"{config['unit_name']} amount must be positive!"
            print(f"Sending {float_value} {config['unit_name']}!")
        
        if token:
            print("Checkpoint!")
            tx_functions = {
                "evm": evm_tx_tokens,
                "sol": sol_tx_tokens,
            }
        else:

            tx_functions = {
                "sol": sol_tx_native,
                "evm": evm_tx_native,
                "sui": sui_tx_native,
                "ton": ton_tx_native,
                "apt": aptos_tx_native,
                "btc": btc_tx_native,
            }

        if tx_functions[ecosystem] == evm_tx_native:
            return tx_functions[ecosystem](evm_chain, vault_id, destination, custom_note, str(smallest_unit))
        elif tx_functions[ecosystem] == evm_tx_tokens:
            return tx_functions[ecosystem](evm_chain, vault_id, destination, custom_note, str(smallest_unit), token)
        elif tx_functions[ecosystem] == sol_tx_tokens:
            return tx_functions[ecosystem](vault_id, destination, custom_note, str(smallest_unit), token)
        else:
            return tx_functions[ecosystem](vault_id, destination, custom_note, str(smallest_unit))
    except ValueError:
        print(f"❌ Invalid {config['unit_name']} amount provided")
        exit(1)