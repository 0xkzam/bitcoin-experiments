from bitcoinutils.setup import setup
from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey
import random


def derive_address():
    setup('testnet')

    pub = PublicKey.from_hex('04c1acdac799fb0308b4b6475ddf7967676759d31484ab55555482472f3bc7c3e7addc4cbba6656a4be4bc6933a6af712b897a543a09c4b899e5f7b943d38108a8')
    print(pub.get_address(compressed=False).to_string())

    pubc = PublicKey.from_hex('02c1acdac799fb0308b4b6475ddf7967676759d31484ab55555482472f3bc7c3e7')
    print(pubc.get_address().to_string())


def vanity_addresses():
    setup('mainnet')
    vanity_string = '1KK'
    found = False
    attempts = 0

    while(not found):
        p = PrivateKey(secret_exponent = random.getrandbits(256))
        a = p.get_public_key().get_address()
        print('.', end='', flush=True)
        attempts += 1
        if(a.to_string().startswith(vanity_string)):
            found = True

    print("\nAttempts: {}".format(attempts))
    print("Address: {}".format(a.to_string()))


def key_operations():
    setup('mainnet')

    # create a private key (deterministically)
    priv = PrivateKey(secret_exponent = 1)    
    print("Private key WIF:", priv.to_wif(compressed=False))
    print("Private key WIFC:", priv.to_wif(compressed=True))
    print("\n")

    # public key
    pub = priv.get_public_key()
    print("Public key uncompressed:", pub.to_hex(compressed=False))
    print("Public key compressed:", pub.to_hex(compressed=True))
    print("\n")

    print("Address:", pub.get_address().to_string())
    print("Taproot Address:", pub.get_taproot_address().to_string())
    print("Segwit Address:", pub.get_segwit_address().to_string())



derive_address()
vanity_addresses()
key_operations()