from bitcoinutils.proxy import NodeProxy
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2shAddress, PrivateKey
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
    rpc_user = UserInput.RPC_USER
    rpc_pw = UserInput.RPC_PW
    host = UserInput.HOST
    port = UserInput.PORT
    proxy = NodeProxy(rpc_user, rpc_pw, host, port).get_proxy()


    @classmethod
    def check_connection(cls) -> bool: 
        """
        - To check the connection with the bitcoin node.

        :return True if connected, raise exception otherwise
        """
        return cls.proxy.getblockcount() > 0

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
        - Get current estimated fee per kB for tx confimation with 10 blocks
        - fee per kB = (min relay fee + min estimated fee) per kB
        - If exception thrown, returns a fallback value

        :param fallback_fee_kb: Optional
        :returns: fee per kB in sats, upon failure returns 2000 sats
        """
        try:
            network_info = cls.proxy.getnetworkinfo()
            if 'relayfee' in network_info:
                relay_fee = network_info['relayfee']
                json = cls.proxy.estimatesmartfee(10)
                if 'feerate' in json:
                    fee = to_satoshis(relay_fee) + to_satoshis(json['feerate'])
                    print("\nEstimated fee per kB (sats): ", fee)
                    return fee
        except Exception:   
            pass         

        print("\nEstimated fee per kB (sats): Using fallback value of ", fallback_fee_kb)
        return fallback_fee_kb