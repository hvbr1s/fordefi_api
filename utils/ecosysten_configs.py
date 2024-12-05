__all__ = ['get_ecosystem_config']

def get_ecosystem_config(ecosystem):
    configs = {
        "sol": {
            "vault_env": "SOL_VAULT_ID",
            "default_dest": "8o6kJ9gPNMnRAgdyWLt6Pd1khnb5yfTYtvSz313cN9Lp",
            "decimals": 1_000_000_000,  # lamports
            "unit_name": "SOL"
        },
        "evm": {
            "vault_env": "EVM_VAULT_ID",
            "default_dest": "0x83c1C2a52d56dFb958C52831a3D683cFAfC34c75",
            "decimals": 1_000_000_000_000_000_000,  # wei
            "unit_name": "ETH"
        },
        "sui": {
            "vault_env": "SUI_VAULT_ID",
            "default_dest": "0xa1af935c826ec92f50da6c4eb9e880b12c18c154f546a993830ee7f000c842bc",
            "decimals": 1_000_000_000,  # mist
            "unit_name": "SUI"
        },
        "ton": {
            "vault_env": "TON_VAULT_ID",
            "default_dest": "UQCXmikxWsyKnP-3yQVAUiu94NGtjAKug4tsiFO1jZ6jOjmt",
            "decimals": 1_000_000_000,  # nanotons
            "unit_name": "TON"
        },
        "apt":{
            "vault_env": "APTOS_VAULT_ID",
            "default_dest": "0x08bfeca2e5589e112324dfdcb2f4f3c733d91955b6c8c6ca8ea329587f61d46c",
            "decimals": 100_000_000, # octa
            "unit_name": "APT"
        },
        "btc":{
            "vault_env": "BTC_VAULT_ID",
            "default_dest": "bc1p4m94zze0tv9kp7usnpha7u98lpanemufhshgv9nae4c3myanc5csly8ayl",
            "decimals": 100_000_000, # satoshis
            "unit_name": "BTC"
        }
    }
    return configs.get(ecosystem)
