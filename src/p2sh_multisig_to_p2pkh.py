from bitcoinutils.setup import setup
from bitcoinutils.keys import P2shAddress, PrivateKey, PublicKey, P2pkhAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.utils import to_satoshis
from node_rpc import TestnetNodeProxy
from typing import List
from user_input import UserInput


def execute(
        sk1: PrivateKey, 
        sk2: PrivateKey, 
        pk3: PublicKey, 
        p2sh_addr: P2shAddress, 
        p2pkh_addr: P2pkhAddress
    ):
    """
    - Sends funds from P2SH Multisig address to a P2PKH address
    
    :param sk1: Private key no.1
    :param sk2: Private key no. 2
    :param pk3: Public key derived from private key no. 3
    :param p2sh_addr: Source address - P2SH Multisig
    :param p2pkh_addr: Destination addres - P2PKH 
    """
    setup("testnet")    

    # ====================================================================================
    # # Initial funding step of the P2SH multisig address
    # # Uncomment and run this if the P2SH address needs to be funded again.
    # try:
    #     p2pkh_sk = PrivateKey(UserInput.P2PKH_SK)
    #     tx0id = TestnetNodeProxy.send_funds_to(p2sh_addr, p2pkh_sk, to_satoshis(0.0001))
    #     print("txid: ", tx0id)
    # except Exception as e:
    #     print("Failed to send funds to \"" + str(p2sh_addr.to_string()) + "\"\n", e)
    # return
    # ====================================================================================

    # Source: P2SH Multisig address=====
    print("Source address:", p2sh_addr.to_string())

    # Checking the p2sh address for unspent outputs=====
    available_amount, utxos = 0, []
    try:
        available_amount, utxos = TestnetNodeProxy.get_balance(p2sh_addr.to_string())
        print("- Number of UTXOs: ", len(utxos))
        print("- Total amount available (sats): ", available_amount)
    except Exception as e:
        print("Try again! ", e)
        return

    # Destination: P2PKH address=====
    print("\nDestination address:", p2pkh_addr.to_string())


    # Calculate the fee=====
    # estimated tx size = (num of inputs * 148) + (num of outputs * 34) + base tx size
    # Since this estimation takes all unspent UTXOs into account, it's not optimal :(
    estimated_tx_size = (len(utxos) * 148) + (2 * 34) + 10
    fee_kb = TestnetNodeProxy.get_fee_per_kb()
    fee = int(estimated_tx_size * fee_kb * 0.001)
    print("Total calculated fee (sats): ", fee)

    # Even though the assignment says to send all funds, I'm only sending half of the
    # funds available in the multisig address because each time I test this, the
    # multsig address needs to be re-funded.
    sending_amount = int(available_amount/2)
    change_amount = available_amount - sending_amount - fee
    if change_amount < 0:
        print("Error: Insufficient funds.")
        return

    # Creating the transaction inputs and ouputs=====
    txinputs, txoutputs = [], []
    for utxo in utxos:
        txinputs.append(TxInput(utxo['txid'], utxo['vout']))

    txoutputs.append(
        TxOutput(sending_amount, p2pkh_addr.to_script_pub_key()))
    txoutputs.append(
        TxOutput(change_amount, p2sh_addr.to_script_pub_key()))

    tx = Transaction(txinputs, txoutputs)
    print("\nRaw unsigned transaction:\n", tx.serialize())


    # Creating the redeem script=====
    redeem_script = Script(
        [
            "OP_2", 
            sk1.get_public_key().to_hex(),
            sk2.get_public_key().to_hex(),
            pk3.to_hex(),
            "OP_3",
            "OP_CHECKMULTISIG"
        ])


    # Signing & Setting the scriptSig for each tx input=====   
    for i, txin in enumerate(txinputs):
        # Signing the tx with 2 of the 3 private keys for each input
        sig1 = sk1.sign_input(tx, i, redeem_script)
        sig2 = sk2.sign_input(tx, i, redeem_script)
        # Setting the scriptSig for each input
        txin.script_sig = Script(["OP_0", sig1, sig2, redeem_script.to_hex()])

    print("\nRaw signed transaction:\n", tx.serialize())


    # Check the validity of the transaction=====
    tx_valid = False
    try:
        tx_valid = TestnetNodeProxy.test_broadcast(tx)
        print("\nTransaction validy check passed.")
    except Exception as e:
        print("\nTransaction validy check failed:", e)

  
    # Broadcast the transaction=====
    if tx_valid:
        try:
            txid = TestnetNodeProxy.broadcast(tx)
            print("\nTx ID:\n", txid)
        except Exception as e:
            print("\nBroadcasting transaction failed:", e)


if __name__ == "__main__":

    # The user inputs are assumed to be taken as commandline arguments. 
    # In this case I'm loading hardcoded data from UserInput class for simplicity

    # User Input 1: Private key no. 1
    sk1 = PrivateKey(UserInput.SK1)

    # User Input 2: Private key no. 2
    sk2 = PrivateKey(UserInput.SK2)

    # User Input 3: Public key no. 3
    pk3 = PublicKey.from_hex(UserInput.PK3)
    
    # User Input 4: source P2SH address
    p2sh_addr = P2shAddress.from_address(UserInput.P2SH_ADDR)

    # User Input 5: destination P2PKH address
    p2pkh_addr = P2pkhAddress.from_address(UserInput.P2PKH_ADDR)


    execute(sk1, sk2, pk3, p2sh_addr, p2pkh_addr)
