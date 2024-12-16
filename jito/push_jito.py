from sdk.jito_jsonrpc_sdk import JitoJsonRpcSDK
from solders.system_program import TransferParams, transfer
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price


async def send_transaction_with_priority_fee(sdk, solana_client, sender, receiver, amount, jito_tip_amount, priority_fee, compute_unit_limit=100_000):
    try:
        recent_blockhash = await solana_client.get_latest_blockhash()
        
        # Transfer to the known receiver
        transfer_ix = transfer(TransferParams(from_pubkey=sender.pubkey(), to_pubkey=receiver, lamports=amount))
        
        # Jito tip transfer
        jito_tip_account = Pubkey.from_string(sdk.get_random_tip_account())
        jito_tip_ix = transfer(TransferParams(from_pubkey=sender.pubkey(), to_pubkey=jito_tip_account, lamports=jito_tip_amount))
        
        # Priority Fee
        priority_fee_ix = set_compute_unit_price(priority_fee)

        transaction = Transaction.new_signed_with_payer(
            [priority_fee_ix, transfer_ix, jito_tip_ix],
            sender.pubkey(),
            [sender],
            recent_blockhash.value.blockhash
        )

        serialized_transaction = base58.b58encode(bytes(transaction)).decode('ascii')
        
        print(f"Sending transaction with priority fee: {priority_fee} micro-lamports per compute unit")
        print(f"Transfer amount: {amount} lamports to {receiver}")
        print(f"Jito tip amount: {jito_tip_amount} lamports to {jito_tip_account}")
        print(f"Serialized transaction: {serialized_transaction}")
        
        response = sdk.send_txn(params=serialized_transaction, bundleOnly=False)

        if response['success']:
            print(f"Full Jito SDK response: {response}")
            signature_str = response['data']['result']
            print(f"Transaction signature: {signature_str}")

            finalized = await check_transaction_status(solana_client, signature_str)
            
            if finalized:
                print("Transaction has been finalized.")
                solscan_url = f"https://solscan.io/tx/{signature_str}"
                print(f"View transaction details on Solscan: {solscan_url}")
            else:
                print("Transaction was not finalized within the expected time.")
            
            return signature_str
        else:
            print(f"Error sending transaction: {response['error']}")
            return None

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None