from bitcoinutils.setup import setup
from bitcoinutils.proxy import NodeProxy
from bitcoinutils.keys import Address, P2shAddress, PrivateKey, PublicKey, P2pkhAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.utils import to_satoshis


def main():
   
    setup("testnet")


    address = 'tb1qpccp98n9g0mdx3zjdnpw3v66j5ysqx3gy8cqw6'



    sk = PrivateKey()
    addr = sk.get_public_key().get_address()

    print("Address: ", addr.to_string())
    print("SK: ", sk.to_wif())





if __name__ == "__main__":
    main()