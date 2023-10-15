import hashlib
import base58

def format_private_key(version: bytes, private_key: bytes,  compressed: bool = True) -> str:
    """
    Calculate WIF or WIFC of the private key

    return string of WIF or WIFC
    """
    
    # Prefix 0x01 byte if WIFC
    if compressed:
        private_key += b'\x01'

    data = version + private_key 

    # # Double hash data
    # hash = hashlib.sha256(hashlib.sha256(data).digest()).digest()

    # # First 4 bytes of double hashed data
    # checksum = hash[:4]

    # # Suffix checksum
    # data += checksum

    # # Base58Check 
    # wif = base58.b58encode(data)

    wif = base58.b58encode_check(data)
    
    return wif.decode('utf-8')  