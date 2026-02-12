import json
import hashlib
from algosdk.v2client import algod
from algosdk import transaction, mnemonic, account

MNEMONIC = "manage quote exclude diary stomach bubble pigeon fitness ramp bottom sponsor wool penalty trust differ change shed lab force gate ensure over beauty about response"

private_key = mnemonic.to_private_key(MNEMONIC)
sender_address = account.address_from_private_key(private_key)

algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)


def store_expense_on_blockchain(expense_data):
    expense_json = json.dumps(expense_data)
    expense_hash = hashlib.sha256(expense_json.encode()).hexdigest()

    params = algod_client.suggested_params()

    txn = transaction.PaymentTxn(
        sender=sender_address,
        sp=params,
        receiver=sender_address,
        amt=0,
        note=expense_hash.encode()
    )

    signed_txn = txn.sign(private_key)
    txid = algod_client.send_transaction(signed_txn)

    return txid
