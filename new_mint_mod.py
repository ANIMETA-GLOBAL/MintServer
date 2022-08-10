import web3
from web3 import Web3
from eth_account.signers.local import LocalAccount
from eth_account import Account
import config
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware

with open('contract/ABI.json', 'r') as abi:
    ABI = abi.read()


class Minter(object):

    def __init__(self, network):
        print(network)
        self.provider = Web3.HTTPProvider(network["rpcUrl"], )
        self.w3 = Web3(self.provider)
        self.chainId = network["chainId"]
        print(self.w3.isConnected())
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.address = network["address"]
        self.contract = self.w3.eth.contract(address=self.address, abi=ABI)
        self.account: LocalAccount = Account.from_key(config.private_key)
        self.w3.middleware_onion.add(construct_sign_and_send_raw_middleware(self.account))
        print(self.account.address)

    def legacy_mint_nft(self, mint_request):
        print("work on legacy mint")
        current_gas = self.w3.eth.gas_price
        print("gas price:", current_gas)
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = self.contract.functions.mint(mint_request["account"], mint_request["amount"], bytes([]),
                                          mint_request["uri"]).buildTransaction(
            {
                'chainId': self.chainId,
                'gasPrice': current_gas,

                'from': self.account.address,
                'nonce': nonce
            }
        )

        signed_txn = self.w3.eth.account.signTransaction(tx, private_key=self.account.privateKey)
        tx_hash = self.w3.toHex(self.w3.keccak(signed_txn.rawTransaction))
        print("tx_hash:", tx_hash)
        self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        res = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        # print(res)
        return res

    def london_mint_nft(self, mint_request):
        print("work on london mint")
        current_gas = self.w3.eth.gas_price
        print("gas price:", current_gas)
        MFPG = 60
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = self.contract.functions.mint(mint_request["account"], mint_request["amount"], bytes([]),
                                          mint_request["uri"]).buildTransaction(
            {
                'chainId': self.chainId,
                'maxFeePerGas': Web3.toWei(MFPG, 'gwei'),
                'maxPriorityFeePerGas': current_gas,
                'from': self.account.address,
                'nonce': nonce
            }
        )
        signed_txn = self.w3.eth.account.signTransaction(tx, private_key=self.account.privateKey)
        tx_hash = self.w3.toHex(self.w3.keccak(signed_txn.rawTransaction))
        print("tx_hash:", tx_hash)
        self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        res = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        return res

    def mint_nft(self, mint_request):
        return self.legacy_mint_nft(mint_request) if self.chainId == config.network_config["bsc"][
            "chainId"] else self.london_mint_nft(mint_request)


class NFTFactory(object):

    def __init__(self, ):
        self.mint_address = config.address
        self.private_key = config.private_key

        self.ethereum = config.network_config["ethereum"]
        self.polygon = config.network_config["polygon"]
        self.bsc = config.network_config["bsc"]


if __name__ == '__main__':
    mint_request = {
        "account": config.address,
        "amount": 100,
        "uri": "https://ipfs.moralis.io:2053/ipfs/QmZJxFn8kTwb8HcpHyoNPq1jsDSE2pEqG848FGhtFGU5ES"
    }

    network = "ethereum"

    A = Minter(config.network_config[network])

    res = A.mint_nft(mint_request)

    print(res)
