import base58
import json
import os
from api.metaplex_api import MetaplexAPI
from cryptography.fernet import Fernet
SERVER_DECRYPTION_KEY = Fernet.generate_key().decode("ascii")
TEST_PRIVATE_KEY = "61VhiWDnXAtmKYVWwVxnjHq7xqsH5yESnntzCR1WDYS3rS3K5VUjaP4QQt8j1DNdf2jqSuEx2jjAfSTdXoB1VGej"
TEST_PUBLIC_KEY = "GpjmSMc9mUcwuTcKoHyuiTZ9vjEq8QAqH3Y7mexXQUo"
cfg = {
    "PRIVATE_KEY": TEST_PRIVATE_KEY,
    "PUBLIC_KEY": TEST_PUBLIC_KEY,
    "DECRYPTION_KEY": SERVER_DECRYPTION_KEY
}
api = MetaplexAPI(cfg)
# account = metaplex_api.Account(list(base58.b58decode(cfg["PRIVATE_KEY"]))[:32])
api_endpoint = "https://api.devnet.solana.com/"

contract_name = "Animeta"
contract_symbol = "AM"

# requires a JSON file with metadata. best to publish on Arweave
divinity_json_file = "https://ipfs.io/ipfs/QmWtsYsCt5sWCqC6B5fqWeDVmJTBCShy4fo5GXNFCKvweQ/0"
# deploy a contract. will return a contract key.
result = api.deploy(api_endpoint, contract_name, contract_symbol,fees=0)
# print(result)
contract_key = json.loads(result).get('contract')
print("contract_address:",contract_key)
# conduct a mint, and send to a recipient, e.g. wallet_2
mint_res = api.mint(api_endpoint, contract_key, TEST_PUBLIC_KEY, divinity_json_file,supply=100)
print(mint_res)

#
#
# class SolanaMint(object):
#     def __init__(self,mint_request):
#         self.private_key = config.solana_private_key
#         self.public_key = config.solana_public_key
