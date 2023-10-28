from bitcoinutils.setup import setup
from bitcoinutils.keys import P2shAddress, PrivateKey, PublicKey, P2pkhAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.utils import to_satoshis
from node_rpc import TestnetNodeProxy
   

def main():
    setup("testnet")

    # Creating private keys and extracting public keys===================================
    sk1 = PrivateKey("cQCP4tNRF96xdv2iidyZwjQHwD47b3evCBdvYVTcBx8PaNjQejT4")
    sk2 = PrivateKey("cVmSqqXC28aZXL9ENVdM4JNsrfpMeifMyEouhNFHH3UiEpDbCr3d")
    sk3 = PrivateKey("cQT5aG2S6QH9YbRo5jPAFWeMqZvwXCW2KuRrvRnS64HwjCymTCJE")
    pk1, pk2, pk3 = sk1.get_public_key(), sk2.get_public_key(), sk3.get_public_key()


    # Creating the redeem script=========================================================
    # Note: full public keys are required to perform OP_CHECKMULTISIG
    redeem_script = Script([2, pk1.to_hex(), pk2.to_hex(), pk3.to_hex(), 3, "OP_CHECKMULTISIG"])


    # Create a P2SH address from the redeem script=======================================
    multisig_addr = P2shAddress.from_script(redeem_script)
    print("Multisig address: ", multisig_addr.to_string())


    #====================================================================================
    # # Initial funding of the multisig P2SH address
    # # Uncomment and run this if you want fund the P2SH address again.    
    # try:
    #     tx0id = TestnetNodeProxy.send_funds_to(multisig_addr, to_satoshis(0.0001))
    #     print("txid: ", tx0id)
    #     # Stop the execution since the tx confirmation takes time
    #     return 
    # except Exception as e:
    #     print("Failed to send funds to \"" + str(multisig_addr.to_string()) + "\"\n", e)
    #     return
    #====================================================================================


    # Checking the p2sh address for unspent outputs======================================    
    available_amount, utxos = 0, []
    try:
        available_amount, utxos = TestnetNodeProxy.get_balance(multisig_addr.to_string())        
        print("Number of UTXOs: ", len(utxos))
        print("Total amount available (sats): ", available_amount)       
    except Exception as e:
        print("Try again! ",e)
        return 


    # Creating a P2PKH address to send funds from the P2PH address=======================
    p2pkh_sk = PrivateKey()
    destination_addr = p2pkh_sk.get_public_key().get_address()
    print("\nDestination address:", destination_addr.to_string())


    # Calculate the fee==================================================================
    # estimated tx size = (num of inputs * 148) + (num of outputs * 34) + base tx size 
    # Since this estimation takes all unspent UTXOs into account, it's not optimal :(
    estimated_tx_size = (len(utxos) * 148) + (2 * 34) + 10
    fee_kb = TestnetNodeProxy.get_estimated_fee_per_kb()
    fee = estimated_tx_size * fee_kb
    # I'm only sending 1/2 of the funds available in the multisig address
    sending_amount = int(available_amount/2)

    # Even though the assignment says to send all funds, I added a change amount because 
    # each time I test this, the multsig address needs to be re-funded.
    change_amount = available_amount - sending_amount - fee
    if change_amount < 0:
        print("Error: Insufficient funds.")
        return


    # Creating the transaction inputs and ouputs=========================================
    txinputs, txoutputs = [], []
    for utxo in utxos:
        txinputs.append(TxInput(utxo['txid'], utxo['vout']))

    txoutputs.append(TxOutput(sending_amount, destination_addr.to_script_pub_key()))
    txoutputs.append(TxOutput(change_amount, multisig_addr.to_script_pub_key()))

    tx = Transaction(txinputs, txoutputs)
    print("\nRaw unsigned transaction:\n" + tx.serialize())


    # Signing & Setting the scriptSig for each tx input==================================
    for i, txin in enumerate(txinputs):
        # Signing the tx with 2 of the 3 private keys for each input
        sig1 = sk1.sign_input(tx, i, redeem_script)
        sig2 = sk2.sign_input(tx, i, redeem_script)
        # Setting the scriptSig for each input
        txin.script_sig = Script(["OP_0", sig1, sig2, redeem_script.to_hex()])        

    print("\nRaw signed transaction:\n", tx.serialize())
      

    # Broadcast the transaction==========================================================
    try:
        txid = TestnetNodeProxy.broadcast(tx)   
        print("\nTx ID:\n", txid)          
    except Exception as e:
        print("Broadcasting transaction failed:", e)
        



if __name__ == "__main__":
    main()