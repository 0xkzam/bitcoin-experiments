from pycoin.key.BIP32Node import BIP32Node
from pycoin.symbols.btc import network
from pycoin.networks.registry import network_for_netcode


def create_private_keys():
    key = network.keys.private(secret_exponent=1)  
    print(key.wif())
    print(key.sec())
    print(key.address())
    print(key.address(is_compressed=False))

    same_key = network.parse.private_key(key.wif())
    print(same_key.address())

def create_BIP32_private_keys():
    key = network.keys.bip32_seed(b"foo")  
    print(key.hwif(as_private=1))
    print(key.hwif())
    print(key.wif())
    print(key.sec())
    print(key.address())


def generate_many(number_of_addresses):
    YEAR = "2016"
    BATCH = "1"
    mpubkey = 'xpub661MyMwAqRbcH37ey3eoQnHgSXokTBkTbqWSBGdJT4puCX1q8mBB5QHe39L5jhkuE2SMremPML7LV2MJC2KE8bvvgJXubkW7wfxeGFTMRoJ'

    key = network.parse.bip32(mpubkey)
    key_path_batch = key.subkey_for_path(YEAR + "/" + BATCH)
    
    for i in range(number_of_addresses):
        subkey = key_path_batch.subkey(i)
        print("{0}".format(subkey.address(1))) # 1 for the internal keypair chain


create_BIP32_private_keys()