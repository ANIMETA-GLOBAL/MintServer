import web3
from web3 import Web3
from eth_account.signers.local import LocalAccount
from eth_account import Account
import config
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware
from pprint import pprint as pp
import json
import pymysql
import logging
import time
import os
import redis
from AnimetaIPFS.animeta_ipfs import AnimetaIPFS
from metaplex_pj.metaplexJ2P import MetaPlexClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))[:-4]
log_path = os.path.dirname(os.getcwd()) + '/MintServer/logs/'
log_name = log_path + "mint_" + rq + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='a')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

with open('contract/ABI.json', 'r') as abi:
    ABI = abi.read()


def DataStruct(token_id="", metadata="", contract_address="", network="", mint_amount=""):
    data_struct = {
        "token_id": token_id,
        "nft_data": metadata,
        "contract_address": contract_address,
        "network": network,
        "mint_amount": mint_amount

    }

    return data_struct


def update_mint_history(history):
    db = pymysql.connect(host=config.history_mysql_host, user=config.mysql_user, password=config.mysql_pwd,
                         db=config.mysql_db)

    cursor = db.cursor()
    sql = "INSERT INTO animeta_mint_history(receipt_time, \
           mint_id,redis_response_time,mint_success,mint_network,mint_contract_address,data) \
           VALUES (%s,%s,%s,%s,%s,%s,%s)"

    val = ((history["receipt_time"], history["mint_id"], history["redis_response_time"], history["mint_success"],
            history["mint_network"], history["mint_contract_address"], history["data"]),)
    try:
        # 执行sql语句
        cursor.executemany(sql, set(val))
        # 提交到数据库执行
        db.commit()
    except Exception as E:
        # 如果发生错误则回滚
        print(E)
        logger.debug("update-error" + str(E))
        db.rollback()


class Minter(object):

    def __init__(self, network):
        print(network)
        self.network_name = network["name"]
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
        try:
            res = self.legacy_mint_nft(mint_request) if self.chainId == config.network_config["bsc"][
                "chainId"] else self.london_mint_nft(mint_request)
            mint_result = json.loads(Web3.toJSON(res))

            if mint_result["status"] == 1:
                token_id_hex = mint_result["logs"][1]["topics"][1]
                token_id = int(token_id_hex, 16)
                # print(token_id, self.network_name)
                # print(mint_request)

                result = {
                    "success": True,
                    "network": self.network_name,
                    "contract": self.contract.address,
                    "token_id": token_id
                }
            else:
                result = {
                    "success": False,
                    "network": "",
                    "contract": "",
                    "token_id": ""
                }

            return result
        except Exception as E:
            print(time.time(), mint_request, E)
            result = {
                "success": False,
                "network": "",
                "contract": "",
                "token_id": "",
                "error": str(E)
            }
            return result


#
class NFTFactory(object):
    #
    def __init__(self, mint_request):
        self.start = time.time()

        self.network = mint_request["network"]
        self.amount = mint_request["mint_amount"]
        self.meta_data = mint_request["meta_data"]
        self.id = mint_request["id"]
        self.pool = redis.Redis(host=config.redis_host, port=config.redis_port, decode_responses=True,
                                password=config.redis_pwd, db=0)
        self.ipfs = AnimetaIPFS()

        self.cid = self.ipfs.upload(self.meta_data)["Hash"]
        self.uri = f"https://ipfs.io/ipfs/{self.cid}"

    def mint(self):
        wrapped_mint_request = {
            "account": config.address,
            "amount": self.amount,
            "uri": self.uri,
            "network": self.network
        }

        if self.network in ["ethereum", "polygon", "bsc"]:
            res = Minter(config.network_config[self.network]).mint_nft(wrapped_mint_request)
            if res["success"]:
                print(self.id, "mint_success")
                redis_final = self.pool.rpush("mintRes", json.dumps({
                    "id": self.id,
                    "success": True,
                    "data": DataStruct(res["token_id"], self.meta_data, res["contract"], res["network"],
                                       wrapped_mint_request["amount"])
                }))
                print("redis push:", redis_final)
                log = {
                    "receipt_time": self.start,
                    "mint_id": self.id,
                    "redis_response_time": time.time(),
                    "mint_success": True,
                    "mint_network": self.network,
                    "mint_contract_address": res["contract"],
                    "data": json.dumps(DataStruct(res["token_id"], self.meta_data, res["contract"], res["network"],
                                                  wrapped_mint_request["amount"]))
                }
                update_mint_history(log)

            else:
                redis_final = self.pool.rpush("mintRes", json.dumps({
                    "id": self.id,
                    "success": False,
                    "data": DataStruct(res["token_id"], self.meta_data, res["contract"], self.network,
                                       wrapped_mint_request["amount"])
                }))
                log = {
                    "receipt_time": self.start,
                    "mint_id": self.id,
                    "redis_response_time": time.time(),
                    "mint_success": False,
                    "mint_network": self.network,
                    "mint_contract_address": res["contract"],
                    "data": json.dumps(DataStruct(res["token_id"], self.meta_data, res["contract"], res["network"],
                                                  wrapped_mint_request["amount"]))
                }
                update_mint_history(log)
                print("redis push:", redis_final)

        if self.network == "solana":
            self.client = MetaPlexClient()
            res = self.client.create_nft(uri=wrapped_mint_request["uri"], name=self.meta_data["name"], fee=500)
            if res:

                result = json.loads(res)
                redis_final = self.pool.rpush("mintRes", json.dumps({
                    "id": self.id,
                    "success": True,
                    "data": DataStruct(result["address"], self.meta_data, result["address"], self.network,
                                       1)
                }))
                log = {
                    "receipt_time": self.start,
                    "mint_id": self.id,
                    "redis_response_time": time.time(),
                    "mint_success": True,
                    "mint_network": self.network,
                    "mint_contract_address": result["address"],
                    "data": json.dumps(DataStruct(result["address"], self.meta_data, result["address"], self.network,
                                                  1))
                }
                update_mint_history(log)
            else:
                redis_final = self.pool.rpush("mintRes", json.dumps({
                    "id": self.id,
                    "success": False,
                    "data": DataStruct(network=self.network, metadata=self.meta_data)
                }))
                log = {
                    "receipt_time": self.start,
                    "mint_id": self.id,
                    "redis_response_time": time.time(),
                    "mint_success": False,
                    "mint_network": self.network,
                    "mint_contract_address": "",
                    "data": ""
                }
                update_mint_history(log)


if __name__ == '__main__':
    data = {'mint_request': {
        "meta_data":
            {
                "name": "hyx nb",
                "description": " nb a hyx",
                "image": "https://ipfs.io/ipfs/QmSWgjuqnKh4tApbHE8wfRoUSG9RWj6DX4NxPUJ2Q225M6?filename=5494c0fa4c8d21450ef7357d0929a5d8.jpegg"
            },
        "mint_amount": 1,
        "id": 78789749,
        "network": "solana"
    }}

    A = NFTFactory(data).mint()
