from bitcoinutils.proxy import NodeProxy
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2shAddress, PrivateKey, P2pkhAddress
from bitcoinutils.script import Script
from bitcoinutils.utils import to_satoshis
from decimal import Decimal
from typing import Optional, List, Dict
from user_input import UserInput


class TestnetNodeProxy:
    """
    - This class is used for rpc calls to interact with the testnet node.
    - For the sake of simplicity, I have hardcoded some input parameters 
    - and also used minimal error handling.
    """

    # Connection to the testnet node running on another host
    # Make sure to set rpcuser, rpcpassword, rpcbind, rpcallowip in the test section of bitcoin.conf
    proxy = NodeProxy("krpcadmin", "ps456b6", host="192.168.1.5", port=18332).get_proxy()

    @classmethod
    def get_utxos(cls, address: str) -> Optional[List[Dict]]:
        """
        :param address: Address as a string
        :returns: A list of UTXOs of given the address
        """

        # Scan for UTXOs
        try:            
            result = cls.proxy.scantxoutset('start', ['addr({})'.format(address)])
            if result['success']:
                return result.get('unspents')
        except Exception as e:
            raise Exception("Error(Retrieving UTXO data):", e)

        return None

    @classmethod
    def get_balance(cls, address: str) -> (int, []):
        """
        - Get the total balance in Sats given the address
        
        :param address: Address as a string
        :returns: (amount in sats, list of UTXOs)
        """
        utxos = cls.get_utxos(address)
        balance = 0
        if utxos:
            balance = to_satoshis(sum([Decimal(utxo['amount']) for utxo in utxos]))
        else:
            raise Exception("Error: No UTXOs available.")

        return (balance, utxos)

    @classmethod
    def broadcast(cls, tx:Transaction) -> str:
        return cls.proxy.sendrawtransaction(tx.serialize())
    
    @classmethod
    def test_broadcast(cls, tx:Transaction) -> bool:
        """
        Checks the whether the provided transaction is valid and whether it'll be 
        accepted by the bitcoin node by testing the mempool acceptance.

        :returns: True if the transaction is valid and ready to broadcast,throws 
        Exception otherwise.
        """
        json = cls.proxy.testmempoolaccept([tx.serialize()])

        if json[0]['allowed']:
            return True
        else:
            raise Exception("Invalid transaction:", json[0]['reject-reason'])
            
        
    @classmethod
    def get_fee_per_kb(cls, fallback_fee_kb = 2000) -> int:
        """      
        - This is a safe stratergy to calculate fee per kB
        - NOT optimal
        
        - Get the minimum relay fee per kB for current network conditions 
        - Get current estimated fee per kB for tx confimation with 5 blocks
        - fee per kB = (min relay fee + min estimated fee) per kB
        - If exception thrown, returns a fallback value

        :param fallback_fee_kb: Optional
        :returns: fee per kB in sats, upon failure returns 2000 sats
        """
        try:
            network_info = cls.proxy.getnetworkinfo()
            if 'relayfee' in network_info:
                min_fee_per_kb = network_info['relayfee']

                json = cls.proxy.estimatesmartfee(5)
                if 'feerate' in json:
                    fee = to_satoshis(min_fee_per_kb) + to_satoshis(json['feerate'])
                    print("\nEstimated fee per kB (sats): ", fee)
                    return fee
        except Exception:   
            pass         

        print("\nEstimated fee per kB (sats): Using fallback value of ", fallback_fee_kb)
        return fallback_fee_kb


    @classmethod
    def send_funds_to(cls, destination_addr: P2shAddress, source_sk:PrivateKey, amount_sats: int) -> str:
        """
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

        return cls.broadcast(tx)