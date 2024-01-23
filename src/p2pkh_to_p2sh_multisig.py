from bitcoinutils.setup import setup
from bitcoinutils.keys import P2shAddress, PrivateKey, PublicKey, P2pkhAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.utils import to_satoshis
from node_rpc import TestnetNodeProxy
from user_input import UserInput



def send_funds_to(destination_addr: P2shAddress, source_sk:PrivateKey, amount_sats: int) -> str:
    """
    - This is just a test method I initially wrote to fund the multisig address

    - Sends funds to a P2SH address from a P2PKH address that already has funds.
    - This corresponds to the initial funding step. The source address and keys 
    - are hardcoded for simplicity.

    - The following address is used to fund the provided address.
    - Initially funded with 0.05 tBTC
    - Address:  mxhTXpLKqJM86MigH5gmrcpvCfigVJep4q
    """
    
    source_addr = source_sk.get_public_key().get_address()
    available_amount, utxos = TestnetNodeProxy.get_balance(source_addr.to_string())   

    # estimated tx size = (num of inputs * 148) + (num of outputs * 34) + base tx size 
    estimated_tx_size = (len(utxos) * 148) + (2 * 34) + 10
    fee_kb = TestnetNodeProxy.get_fee_per_kb()
    fee = int(estimated_tx_size * fee_kb * 0.001)

    change_amount = available_amount - amount_sats - fee
    if change_amount < 0:
        raise Exception("Error: Insufficient funds.")


    # Creating the transaction inputs and ouputs
    txinputs, txoutputs = [], []
    for utxo in utxos:
        txinputs.append(TxInput(utxo['txid'], utxo['vout']))

    txoutputs.append(TxOutput(amount_sats, destination_addr.to_script_pub_key()))
    txoutputs.append(TxOutput(change_amount, source_addr.to_script_pub_key()))

    tx = Transaction(txinputs, txoutputs)

    # Signing the transaction
    for i in range(len(txinputs)):
        sig = source_sk.sign_input(tx, i, source_addr.to_script_pub_key())
        pk = source_sk.get_public_key().to_hex()
        script_sig = Script([sig, pk])
        txinputs[i].script_sig = script_sig   

    return TestnetNodeProxy.broadcast(tx)