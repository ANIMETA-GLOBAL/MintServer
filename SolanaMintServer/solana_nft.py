import base58
import json
import os
from api.metaplex_api import MetaplexAPI
from cryptography.fernet import Fernet
import config

# SERVER_DECRYPTION_KEY = Fernet.generate_key().decode("ascii")
# TEST_PRIVATE_KEY = "61VhiWDnXAtmKYVWwVxnjHq7xqsH5yESnntzCR1WDYS3rS3K5VUjaP4QQt8j1DNdf2jqSuEx2jjAfSTdXoB1VGej"
# TEST_PUBLIC_KEY = "GpjmSMc9mUcwuTcKoHyuiTZ9vjEq8QAqH3Y7mexXQUo"
# cfg = {
#     "PRIVATE_KEY": TEST_PRIVATE_KEY,
#     "PUBLIC_KEY": TEST_PUBLIC_KEY,
#     "DECRYPTION_KEY": SERVER_DECRYPTION_KEY
# }
# api = MetaplexAPI(cfg)
# # account = metaplex_api.Account(list(base58.b58decode(cfg["PRIVATE_KEY"]))[:32])
# api_endpoint = "https://api.devnet.solana.com/"
#
# contract_name = "Animeta"
# contract_symbol = "AM"
#
# # requires a JSON file with metadata. best to publish on Arweave
# divinity_json_file = "https://ipfs.io/ipfs/QmWtsYsCt5sWCqC6B5fqWeDVmJTBCShy4fo5GXNFCKvweQ/0"
# # deploy a contract. will return a contract key.
# result = api.deploy(api_endpoint, contract_name, contract_symbol, fees=0)
# # print(result)
# contract_key = json.loads(result).get('contract')
# print("contract_address:", contract_key)
# # conduct a mint, and send to a recipient, e.g. wallet_2
# mint_res = api.mint(api_endpoint, contract_key, TEST_PUBLIC_KEY, divinity_json_file, supply=100)
# print(mint_res)


class SolanaMint(object):
    def __init__(self):
        self.private_key = config.solana_private_key
        self.public_key = config.solana_public_key
        self.network = config.network_config["solana"]
        self.cfg = {
            "PRIVATE_KEY": self.private_key,
            "PUBLIC_KEY": self.public_key,
            "DECRYPTION_KEY": Fernet.generate_key().decode("ascii")
        }

        self.api = MetaplexAPI(self.cfg)
        self.api_endpoint = self.network["rpcUrl"]
        self.contract_key = self.network["address"]

    def mint_nft(self, mint_request):
        meta_data_url = mint_request["meta_data_url"]
        amount = mint_request["mint_amount"]
        mint_res = self.api.mint(self.api_endpoint, self.contract_key,self.public_key, meta_data_url,
                                 amount)
        return mint_res




if __name__ == '__main__':

    mint_request = {
        "account": config.address,
        "mint_amount": 100,
        "meta_data_url": "https://ipfs.moralis.io:2053/ipfs/QmZJxFn8kTwb8HcpHyoNPq1jsDSE2pEqG848FGhtFGU5ES"
    }
    A = SolanaMint()
    print(A.mint_nft(mint_request))
