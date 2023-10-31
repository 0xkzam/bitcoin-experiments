from bitcoinutils.setup import setup
from bitcoinutils.keys import P2shAddress, PrivateKey, PublicKey
from bitcoinutils.script import Script
from user_input import UserInput


def main(pk1_hex: str, pk2_hex: str, pk3_hex: str):

    setup("testnet")
    
    # Creating the redeem script
    # Note: full public keys are required to perform OP_CHECKMULTISIG
    redeem_script = Script(["OP_2", pk1_hex, pk2_hex, pk3_hex, "OP_3", "OP_CHECKMULTISIG"])

    # create a P2SH address from the redeem script
    addr = P2shAddress.from_script(redeem_script)

    print("P2SH Multisig Address:", addr.to_string())


if __name__ == "__main__":

    # The user input of 3 public keys strings are assumed to be taken as
    # commandline arguments. In this case I'm loading them from another
    # class for simplicity
    pk1_hex = UserInput.PK1 # User input 1: pub key no. 1
    pk2_hex = UserInput.PK2 # User input 2: pub key no. 2
    pk3_hex = UserInput.PK3 # User input 3: pub key no. 3

    main(pk1_hex, pk2_hex, pk3_hex)