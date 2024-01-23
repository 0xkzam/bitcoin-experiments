class UserInput:
    # Just to avoid the hassle of loading a properties file :)

    # There might be tBTC available in the following addresses. Not going to remove the private keys, so be responsible :)
    ##########################################################################
    # Private keys used to create the P2SH Multsig address
    SK1 = "cQCP4tNRF96xdv2iidyZwjQHwD47b3evCBdvYVTcBx8PaNjQejT4"
    SK2 = "cVmSqqXC28aZXL9ENVdM4JNsrfpMeifMyEouhNFHH3UiEpDbCr3d"
    SK3 = "cQT5aG2S6QH9YbRo5jPAFWeMqZvwXCW2KuRrvRnS64HwjCymTCJE"

    # Derived public keys from the above private keys
    PK1 = "03e79e8f98a34f1b35ee6dff76d6a9e93f315fbfec798836df43db557f12e5de92"
    PK2 = "0328b43df1372ce92d9efa6819c6eea501ac4a030ef76da2937435e4c218951879"
    PK3 = "03609c80ce85252695afbe2ae26d59f4d7b90ff499c31854db0add8b9313489dcf"

    # Multisig address created using above keys
    P2SH_ADDR = "2N5wY7GggFihwLyLq9bVtSh3tXrisM1jREV"
    ##########################################################################

    ##########################################################################
    # P2PKH address which is used to fund the P2PH address
    P2PKH_ADDR = "mxhTXpLKqJM86MigH5gmrcpvCfigVJep4q"

    # Private key of above address
    P2PKH_SK = "cSiDHNFUmmCZMmhij8chhUe9fFVHPByacvsuwmxFjBeCFuvsxnkR"
    ##########################################################################

    ##########################################################################
    # Node access details
    RPC_USER = "krpcadmin"
    RPC_PW = "ps456b6"
    HOST = "192.168.1.5"
    PORT = 18332  # testnet
    ##########################################################################ß