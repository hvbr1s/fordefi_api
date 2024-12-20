import os
import requests
import datetime
import json
from solana.rpc.api import Client
import asyncio
import base58
import base64
from api_requests.broadcast import get_tx
from signing.signer import sign
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.instruction import Instruction
from solders.transaction import Transaction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.transaction_status import TransactionConfirmationStatus
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solana.exceptions import SolanaRpcException
from jito_sdk.jito_jsonrpc_sdk import JitoJsonRpcSDK

transaction_id = "8e4ae9b0-1141-45a3-9b12-a053ab9bacfe"
access_token = os.getenv("FORDEFI_API_TOKEN")
path = f"/api/v1/transactions/{transaction_id}"
request_body = ""
timestamp = datetime.datetime.now().strftime("%s")
payload = f"{path}|{timestamp}|{request_body}"
quicknode_key = os.getenv("QUICKNODE_MAINNET_KEY")

api_signer_sig = sign(payload=payload)

######

# async def check_transaction_status(client: AsyncClient, signature_str: str):
#     print("Checking transaction status...")
#     max_attempts = 60  # 60 seconds
#     attempt = 0
    
#     signature = Signature.from_string(signature_str)
    
#     while attempt < max_attempts:
#         try:
#             response = await client.get_signature_statuses([signature])
            
#             if response.value[0] is not None:
#                 status = response.value[0]
#                 slot = status.slot
#                 confirmations = status.confirmations
#                 err = status.err
#                 confirmation_status = status.confirmation_status

#                 print(f"Slot: {slot}")
#                 print(f"Confirmations: {confirmations}")
#                 print(f"Confirmation status: {confirmation_status}")
                
#                 if err:
#                     print(f"Transaction failed with error: {err}")
#                     return False
#                 elif confirmation_status == TransactionConfirmationStatus.Finalized:
#                     print("Transaction is finalized.")
#                     return True
#                 elif confirmation_status == TransactionConfirmationStatus.Confirmed:
#                     print("Transaction is confirmed but not yet finalized.")
#                 elif confirmation_status == TransactionConfirmationStatus.Processed:
#                     print("Transaction is processed but not yet confirmed or finalized.")
#             else:
#                 print("Transaction status not available yet.")
            
#             await asyncio.sleep(1)
#             attempt += 1
#         except Exception as e:
#             print(f"Error checking transaction status: {e}")
#             await asyncio.sleep(1)
#             attempt += 1
    
#     print(f"Transaction not finalized after {max_attempts} attempts.")
#     return False

async def send_transaction_with_priority_fee(sdk, raw_transaction_base58, solana_client, sender, receiver, amount, jito_tip_amount, priority_fee, compute_unit_limit=100_000):
    try:
        recent_blockhash = await solana_client.get_latest_blockhash()

        sender_pubkey =  Pubkey.from_string(str(sender))
        receiver_pubkey = Pubkey.from_string(str(receiver))
        lamports = int(amount)
        
        # Transfer to the known receiver
        transfer_ix = transfer(TransferParams(from_pubkey=sender_pubkey, to_pubkey=receiver_pubkey, lamports=lamports))
        
        # Jito tip transfer
        jito_tip_account = Pubkey.from_string(sdk.get_random_tip_account())
        jito_tip_ix = transfer(TransferParams(from_pubkey=sender_pubkey, to_pubkey=jito_tip_account, lamports=jito_tip_amount))
        
        # Priority Fee
        priority_fee_ix = set_compute_unit_price(priority_fee)

        # transaction = Transaction.new_signed_with_payer(
        #     [priority_fee_ix, transfer_ix, jito_tip_ix],
        #     sender_pubkey,
        #     [sender],
        #     recent_blockhash.value.blockhash
        # )
        
        print(f"Sending transaction with priority fee: {priority_fee} micro-lamports per compute unit")
        print(f"Transfer amount: {amount} lamports to {receiver}")
        print(f"Jito tip amount: {jito_tip_amount} lamports to {jito_tip_account}")
        print(f"Serialized transaction: {raw_transaction_base58}")
        
        response = sdk.send_txn(params=raw_transaction_base58, bundleOnly=False)

        if response['success']:
            print(f"Full Jito SDK response: {response}")
            signature_str = response['data']['result']
            print(f"Transaction signature: {signature_str}")

            # finalized = await check_transaction_status(solana_client, signature_str)
            
            # if finalized:
            #     print("Transaction has been finalized.")
            #     solscan_url = f"https://solscan.io/tx/{signature_str}"
            #     print(f"View transaction details on Solscan: {solscan_url}")
            # else:
            #     print("Transaction was not finalized within the expected time.")
            
            return signature_str
        else:
            print(f"Error sending transaction: {response['error']}")
            return None

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None


async def main():
    # solana_client = AsyncClient(f"https://winter-solemn-sun.solana-mainnet.quiknode.pro/{quicknode_key}/")
    solana_client = AsyncClient("https://api.mainnet-beta.solana.com")
    print(solana_client)
    sdk = JitoJsonRpcSDK(url="https://mainnet.block-engine.jito.wtf/api/v1")

    # Fetch tx
    fetch_raw_tx = get_tx(path, access_token, api_signer_sig, timestamp, request_body)
    # print(fetch_raw_tx)
    # Fetch raw tx
    raw_transaction_base64 = fetch_raw_tx['raw_transaction']
    raw_bytes = base64.b64decode(raw_transaction_base64)
    raw_transaction_base58 = base58.b58encode(raw_bytes).decode('ascii')
    # print(f"Raw tx as base58 -> {raw_transaction_base58}")
    # Fetch sender
    sender = fetch_raw_tx['sender']['address']
    print(f"Sender -> {sender}")
    # Fetch receiver
    receiver =  fetch_raw_tx['solana_transaction_type_details']['recipient']['address']
    print(f"Receiver -> {receiver}")
    # Fetch amount
    amount = fetch_raw_tx["mined_result"]["effects"]["transfers"][0]["amount"]
    print(f"Amount -> {amount}")

    priority_fee = 1000  # Lamport for priority fee
    jito_tip_amount = 1000  # Lamports for Jito tip

    signature = await send_transaction_with_priority_fee(sdk, raw_transaction_base58, solana_client, sender, receiver, amount, jito_tip_amount, priority_fee)

    if signature:
        print(f"Transaction process completed. Signature: {signature}")

    await solana_client.close()

asyncio.run(main())