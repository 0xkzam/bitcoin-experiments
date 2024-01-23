### Node setup
- 1.1 Initial setup
- 1.2 Bitcoin Core client
- 1.3 Editing bitcoin.conf
- 1.4 Enabling RPC

#### 1.1 Initial setup
In this experiment, I’m setting up a testnet full node. For the node software, although there are several other implementations available, I’m using the Bitcoin-Core client, which is the most widely used implementation.

There are several ways to install Bitcoin Core. 
1. Using official binary release
2. Using the [snap package manager](https://www.geeksforgeeks.org/how-to-install-bitcoin-core-wallet-on-ubuntu/)
3. Using the [source](https://github.com/bitcoin/bitcoin)

I'm using the official binary release of bitcoin-core-25.0 from the GitHub bitcoin repository. You can download it from the following locations.
- https://github.com/bitcoin/bitcoin/releases 
- https://bitcoincore.org/bin/bitcoin-core-25.0/ 

Also, I’m running the full node on a virtual machine ([UTM](https://mac.getutm.app/)) running a linux server (Ubuntu), which is running on an M1 Mac. Please note that for this specific setup, the Bitcoin-Core designed for the aarch64-linux architecture is required, i.e., *bitcoin-25.0-aarch64-linux-gnu.tar.gz*

**NOTE**: 

1. Make sure to set the VM network mode to 'Bridged' to be able for the node access the network.
2. Except for the location of blockchain data download directory, all the following steps can be similarly applied across all platforms (e.g., mac, windows, linux) 
3. Make sure to allocate enough disk space for the VM to avoid the unnecessary hassle of resizing later, something I've already gone through. To resize a UTM Ubuntu VM after setting up, refer to this article: https://www.albertyw.com/note/resizing-ubuntu-utm <br>
As of this writing, to run a bitcoin full node, you need 450GB minimum, and for a tesnet node, you need ~35GB (check here:https://blockchair.com/bitcoin/testnet). There is the option of running a pruned node as well. 

Once the linux server on the VM is properly set up, just run the following commands to download and extract the contents of the tar.gz file. 

```
wget https://bitcoincore.org/bin/bitcoin-core-25.0/bitcoin-25.0-aarch64-linux-gnu.tar.gz
tar xvzf bitcoin-25.0-aarch64-linux-gnu.tar.gz 
```
All files are extracted to bitcoin-25.0 directory and the bitcoin-25.0/bin directory contains all the executables needed to run a bitcoin node. Initially, to run the testnet node, you need to run the bitcoin daemon, i.e., `bitcoind`. 
```
./bin/bitcoin-cli/bitcoind -testnet -daemon
```
Run the above command to download the blochchain data. Make sure to add the `testnet` flag to sync with the testnet and `daemon` flag to run as a background service. Once this command is run, a data directory will be created at `~/.bitcoin` which contains the downloaded blockchain data. Depending on the blockchain size and the bandwidth of the network connection, it will take several hours to sometimes few days to sync up with the current state of the blockchain.

```
# To check the status run
./bin/bitcoin-cli -testnet getblockchaininfo

# To stop the bitcoin daemon run
./bin/bitcoin-cli -testnet stop
```

#### 1.2 Bitcoin Core client

Bitcoin client comes with the following executables.

- **bitcoind**: This is the Bitcoin deamon server. Includes a wallet and a JSON-RPC API to interact with the node
- **bitcoin-cli**: Command line interface to communicate with the deamon server
- **bitcoin-qt**: GUI for the deamon server and the wallet 
- **bitcoin-tx**: Create, parse and modify transactions 
- **bitcoin-wallet**: Wallet related utilities


#### 1.3 Editing bitcoin.conf

We can add the relevant flags to the configuration file (i.e., bitcoin.conf) instead of passing all the flags with values as command line arguements each time when starting the node. This conf file is located in the data folder (*~/.bitcoin/bitcoin.conf*). At the bottom of this file, there're separate sections for the flags to be inserted (e.g., mainnet, testnet, signet). The purpose of these sections is to provide clarity when different types of nodes are running with different configuations. They can be used if you want to set specific flags as per your requirement. However, since I'm running only a testnet node, I just added to all following flags at the top of file. Now I can simply call `./bin/bitcoin-cli/bitcoind` without passing any flag.

```
# Run as a background service
daemon=1

# Always start the testnet node
testnet=1

# Prune the node to keep the most recent 10000 megabytes of data
prune=10000
```

**NOTE**: When pruning is enabled, it does not mean the node will only download the most recent blockchain data during syncing. The node will still download the entire blockchain to validate the data and then it will progressively delete the older blocks as the syncing process continues.


#### 1.4 Enabling RPC

I'm connecting to the bitcoin node from the host terminal using ssh. Therefore, first we need to make sure ssh server is installed in the linux server (and in the host machine as well). 
```
sudo apt -y install openssh-server
```

The standard way of connecting to the node is via remote procedure calls (RPC). So we need add the following configuration options bitcoin.conf to enable RPC (alternatively, they can be passed as flags to `bitcoind` when starting the node).

```
# Enable RPC server in the Bitcoin-Core
server=1

# Username and password to access RPC server
rpcuser=rp_username
rpcpassword=rp_password


# Following IP addresses can be obtained by simply doing an 'ifconfig' on each machine, and the address is typcally list under 'eth0'

# Local network address of the machine running the bitcoin node, i.e., the VM
rpcbind=192.168.1.5

# Local network address of the host machine. 
rpcallowip=192.168.1.4
```

Once the above options are added to the bicoin.conf we can simply connect to the node from our host machine using ssh (e.g., `ssh rp_username@192.168.1.5`) and execute bitcoin commandline arguements from the host terminal.

**That's it. node setup is done!**