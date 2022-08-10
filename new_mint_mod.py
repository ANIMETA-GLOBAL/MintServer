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

    def mintNft(self, mint_request):
        GAS_AMOUNT = 65000
        GAS_PRICE = 12  # gwei
        MAXFeeperGas = 20
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = self.contract.functions.mint(mint_request["account"], mint_request["amount"], bytes([]),
                                          mint_request["uri"]).buildTransaction(
            {
                'chainId': self.chainId,
                # 'gas': GAS_AMOUNT,
                'gasPrice': Web3.toWei(GAS_PRICE, 'gwei'),
                'maxFeePerGas':Web3.toWei(MAXFeeperGas, 'gwei'),
                'maxPriorityFeePerGas': Web3.toWei('10', 'gwei'),
                'from': self.account.address,
                'nonce': nonce
            }
        )

        signed_txn = self.w3.eth.account.signTransaction(tx, private_key=self.account.privateKey)
        tx_hash = self.w3.toHex(self.w3.keccak(signed_txn.rawTransaction))

        # signed_tx = self.w3.eth.sign_transaction(tx,private_key=self.account.privateKey)
        print(tx_hash)
        res = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(res)


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
    A = Minter(config.network_config["bsc"])
    A.mintNft(mint_request=mint_request)
