from api_requests.tx_constructor import evm_tx_native, sol_tx_native, sui_tx_native, ton_tx_native
from utils.ecosysten_configs import get_ecosystem_config
import os

def process_transaction(ecosystem, evm_chain, vault_id, destination, value, custom_note):
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
        smallest_unit = int(float_value * config["decimals"])
        assert smallest_unit > 0, f"{config['unit_name']} amount must be positive!"
        print(f"Sending {float_value} {config['unit_name']}!")
        
        tx_functions = {
            "sol": sol_tx_native,
            "evm": evm_tx_native,
            "sui": sui_tx_native,
            "ton": ton_tx_native
        }
        if tx_functions[ecosystem] == evm_tx_native:
            return tx_functions[ecosystem](evm_chain, vault_id, destination, custom_note, str(smallest_unit))
        else:
            return tx_functions[ecosystem](vault_id, destination, custom_note, str(smallest_unit))
    except ValueError:
        print(f"❌ Invalid {config['unit_name']} amount provided")
        exit(1)