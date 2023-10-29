from bitcoinutils.setup import setup
from bitcoinutils.keys import P2shAddress, PrivateKey
from bitcoinutils.script import Script

def main():
    setup("testnet")        

    # Generating private keys
    sk1, sk2, sk3 = PrivateKey(), PrivateKey(), PrivateKey()

    # Extract public keys from the private keys
    pk1 = sk1.get_public_key()
    pk2 = sk2.get_public_key()
    pk3 = sk3.get_public_key()
  
    # Creating the script
    # Note: full public keys are required to perform OP_CHECKMULTISIG
    redeem_script = Script([2, pk1.to_hex(), pk2.to_hex(), pk3.to_hex(), 3, "OP_CHECKMULTISIG"])

    # create a P2SH address from the redeem script
    addr = P2shAddress.from_script(redeem_script)

    print("Multisig Address: ", addr.to_string())



if __name__ == "__main__":

    main()