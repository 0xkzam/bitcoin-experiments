
### Transactions 
- 2.1 Intro
- 2.2 UTXO
- 2.3 scriptPubKey
- 2.4 scriptSig
- 2.5 Tx Outout Types
- 2.6 Signatures
- 2.7 SIGHASH flags
- 2.8 Making a basic Tx using bitcoin-cli

#### 2.1 Transactions Intro

- A transaction consists of one or more inputs and one or more outputs.
- Each input references an output from a previous transaction.
- Each output defines a certain amount of bitcoins to be transferred and the conditions under which they can be spent.

#### 2.2 UTXO

- The outputs that are available to be spent (balance = sum of UTXOs).
- When creating a UTXO, a set of conditions must be specified.
- When spending the UTXO, you must prove that you satisfy those conditions.
- The conditions are set using the scripting language.
- When a new output is created, a script is placed in the UTXO called **scriptPubKey** (**locking script**).
- When you want to spend the UTXO, a new transaction must be created referencing this UTXO in the **scriptSig** (**unlocking script**). The scriptSig is prepended to the scriptPubKey and executed.

#### 2.3 **scriptPubKey**

- When a UTXO is created, it includes a **scriptPubKey**, which sets the conditions for spending that output.
- This script is essentially a locking mechanism that specifies what must be provided in a future transaction for these bitcoins to be spent.

#### 2.4 **scriptSig**

- To spend a UTXO, a transaction must include a **scriptSig** that fulfills the conditions specified in the UTXO's **scriptPubKey**.
- This is often a digital signature that proves ownership of the corresponding private key for a Bitcoin address, but it can be more complex depending on the **scriptPubKey**.


#### 2.5 Transaction Output Types

|  |  |
|-------------------------|--------------|
| **P2PK**                | - Pay to Public Key<br>- Not used anymore |
| **P2PKH**               | - Pay to Public Key Hash<br>- Standard transaction output to transfer bitcoin<br> - scriptPubKey: `OP_DUP OP_HASH160  <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG`<br> - scriptSig: `<signature> <pubKey>`| 
| **P2SH**                | - Pay to Script Hash ([BIP-16](https://github.com/bitcoin/bips/blob/master/bip-0016.mediawiki))<br>- Use to create complex scripts with multiple conditions (e.g. Multisig, Timelocks)<br>- Moves the responsibility for supplying the conditions to redeem a transaction from the sender to the receiver <br> - E.g. 2-of-2 Multisig: <br>-- redeem script: `2 <pubKeyA> <pubKeyB> 2 OP_CHECKMULTISIG`<br> -- scriptPubKey: `OP_HASH160 [20-byte-redeem-script-hash] OP_EQUAL`<br> -- scriptSig: `0 <signatureA> <signatureB> <redeem-script>`<br>-- NOTE: The 0 (or OP_0) at the beginning of the scriptSig is used as a dummy value to work around a bug in OP_CHECKMULTISIG where it pops an extra element from the stack|
| **P2WPKH**              | - Pay to Witness Public Key Hash ([BIP-141](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki))<br>- Segwit version of P2PKH <br> - The 0 at the beginning of scriptPubKey is the version byte indicating the segwit version<br> - scriptPubKey: `0 <20-byte-public-key-hash>` <br> - scriptSig: "" <br> - witness: `<signature> <pubKey>` |
| **P2WSH**               | - Pay to Witness Script Hash ([BIP-141](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki))<br>- Segwit version of P2SH <br> - The 0 at the beginning of scriptPubKey is the version byte indicating the segwit version<br> - E.g. 1-of-2 Multisig: <br> -- witness script: `1 <pubKeyA> <pubKeyB> 2 OP_CHECKMULTISIG `<br> -- scriptPubKey: `0 <32-byte-witness-script-hash>` <br> -- scriptSig: "" <br> -- witness: ` 0 <signatureA> <witness-script>` <br>-- NOTE: The 0 (or OP_0) at the beginning of the witness is used as a dummy value to work around a bug in OP_CHECKMULTISIG where it pops an extra element from the stack|
| **P2TR**                | - Pay to Witness Taproot ([BIP-341](https://github.com/bitcoin/bips/blob/e918b50731397872ad2922a1b08a5a4cd1d6d546/bip-0341.mediawiki#cite_ref-22-0))|
| **OP_RETURN**           | - Direct storage of data, storing up to 80 bytes in an output<br>-  No sathoshis required except the transaction fee <br>- Typically used to store a hash of some data rather than immutable existence of the data itself<br>- Can be used to encode meta-protocol information (e.g. [Counterparty](https://counterparty.io/), [OMNI protocol](https://www.omnilayer.org/), [BDip](https://github.com/karask/blockchain-certificates))|
| **P2MS**      | - Legacy multisig transactions<br>- P2SH/P2WSH are used instead <br>- Limited 3 public keys, while P2SH/P2WSH allows up to 15|
| **Non-standard**        | - Any other type of tx <br> - These are typically rejected (but not invalid) and not relayed by nodes <br> - Can be mined if arranged with a miner|
|||



#### 2.6 Signatures

- When creating a new transaction, a signature must be provided for each Unspent Transaction Output (UTXO) that is going to be spent.
- Each transaction input must be signed separately.
- The signature proves that:
  - The signer owns the private key.
  - The proof of authorization is undeniable.
  - The parts of the transaction that are signed cannot be modified.
- At the end of the signature, the hash type (SIGHASH) of the signature is defined using a one-byte suffix. This type determines the parts of the transaction that are signed.
- Serialized using [DER encoding](https://en.wikipedia.org/wiki/X.690#DER_encoding).

#### 2.7 SIGHASH flags

- The SIGHASH type determines which parts of a transaction are signed.
- This is important when it comes to multiple inputs or complex spending conditions.
- E.g. scriptSig: `<signature1[SIGHASH_SINGLE]> <pubKey1>`
- E.g. scriptSig: `<signature2[SIGHASH_ALL]> <pubKey2>`

<br>


| Flag                 | Value | Description                                                                                                                                         |
| -------------------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| ALL                  | 0x01  | - Signs all inputs and all outputs<br>- Most common type of SIGHASH used<br>- Protects everything except the signature scripts against modification |
| NONE                 | 0x02  | - Signs all of the inputs but none of the outputs<br>- Allows anyone to change where the funds are going                                            |
| SINGLE               | 0x03  | - Signs all the inputs and only one output.<br>- The signed output’s output index (i.e. vout) should be the same as the index of the input          |
| ALL\|ANYONECANPAY    | 0x81  | - Signs one input and all outputs, but allows additional inputs to be added.                                                                        |
| NONE\|ANYONECANPAY   | 0x82  | - Signs one input and allows changes to all outputs and additional inputs to be added.                                                              |
| SINGLE\|ANYONECANPAY | 0x83  | - Signs one input and its corresponding output, allowing changes to other outputs and additional inputs.                                            |
||

#### 2.8 Making a basic Tx using `bitcoin-cli`

- Select a wallet and run `listunspent` to list all available UTXOs
    ```
    bitcoin-cli -testnet -rpcwallet="test-w-1" listunspent
    ```
- Select `txid` and `vout` from a UTXO that has enough funds
- Run `createrawtransaction` using the selected `txid` and `vout`
- Always calculate the amount of fees for the tx, otherwise the rest of the BTC minus the sending amount will be used as the tx fee. The `change_address` can be used to return the balance after substracting the sending amount + tx fee.
    ```
    bitcoin-cli -testnet createrawtransaction '[
        {
            "txid":"<txn_id>",
            "vout":<vout>
        }
    ]' '{
        "<recipient_address>": <btc_amount>, 
        "data":"<data_in_hex>",
        "change_address": <change-amount>
    }'
    ```

- The hex data output that is returned from running `createrawtransaction` is passed to `signrawtransactionwithwallet`
    ```
    bitcoin-cli -testnet -rpcwallet="test-w-1" signrawtransactionwithwallet "<hex_data_createrawtransaction>"
    ```
- Finally, the hex data output that is returned from `signrawtransactionwithwallet` is passed to `sendrawtransaction` to broadcast the tx.
    ```
    bitcoin-cli -testnet sendrawtransaction “<hex_data_signrawtransactionwithwallet>”
    ```