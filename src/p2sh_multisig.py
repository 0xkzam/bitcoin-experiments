from bitcoinutils.setup import setup
from bitcoinutils.keys import Address, P2shAddress, PrivateKey, PublicKey
from bitcoinutils.script import Script


def create_multsig_address(pub1:PublicKey, pub2:PublicKey, pub3:PublicKey) -> Address: 
    """
    - Takes 3 PublicKey objects as parameters 
    - Create a 2 of 3 MULTISIG using P2SH
    - Returns an Address 
    """

    setup("testnet")        
  
    # Creating the scrypt
    redeem_script = Script([2, pub1.to_hex(), pub1.to_hex(), pub1.to_hex(), 3, "OP_CHECKMULTISIG"])

    # create a P2SH address from the redeem script
    addr = P2shAddress.from_script(redeem_script)
    return addr


if __name__ == "__main__":

    # Generating private keys
    p1 = PrivateKey()
    p2 = PrivateKey()
    p3 = PrivateKey()

    # Extract public key from the private keys
    pub1 = p1.get_public_key()
    pub2 = p2.get_public_key()
    pub3 = p3.get_public_key()

    addr = create_multsig_address(pub1, pub2, pub3)
    print("Multisig Address: " + addr.to_string())