from thirdweb import ThirdwebSDK
from thirdweb.types.nft import NFTMetadataInput, EditionMetadataInput
import json
import config
import redis
import pymysql
import time
# Note that you can customize this metadata however you like
import logging
import os.path

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))[:-4]
log_path = os.path.dirname(os.getcwd()) + '/MintServer/logs/'
log_name = log_path + "mint_" +rq + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='a')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

EDITION_ADDRESS = "0x0B892512FC5Ae908f0f4B9A411AaED5Cd0aDab91"

RPC_URL = "https://rinkeby.infura.io/v3/10b156a4ad4449669733898b548f63f9"
HOST_PRIVATE_KEY = config.private_key

# And now you can instantiate the SDK with it


sdk = ThirdwebSDK.from_private_key(HOST_PRIVATE_KEY, "rinkeby")

contract = sdk.get_edition(EDITION_ADDRESS)
pool = redis.Redis(host=config.redis_host, port=config.redis_port, decode_responses=True,password=config.redis_pwd, db=0,ssl=True)


def update_mint_history(history):
    db = pymysql.connect(host=config.history_mysql_host, user=config.mysql_user, password=config.mysql_pwd,
                         db=config.mysql_db)

    cursor = db.cursor()
    sql = "INSERT INTO animeta_mint_history(receipt_time, \
           mint_id,redis_response_time,mint_success,mint_chain_id,mint_contract_address,data) \
           VALUES (%s,%s,%s,%s,%s,%s,%s)"

    val = ((history["receipt_time"], history["mint_id"], history["redis_response_time"], history["mint_success"],
            history["mint_chain_id"], history["mint_contract_address"], history["data"]),)
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



def mint_nft(mint_request):
    start_time = time.time()
    metadata_with_supply = EditionMetadataInput(
        NFTMetadataInput.from_json({
            "name": mint_request["meta_data"]["name"],
            "description": mint_request["meta_data"]["description"],
            "image": mint_request["meta_data"]["image"],
        }),
        mint_request["mint_amount"]
    )

    print(mint_request)

    # You can pass in any address here to mint the NFT to

    try:
        tx = contract.mint_to("0xe403E8011CdB251c12ccF6911F44D160699CCC3c", metadata_with_supply)
        receipt = tx.receipt
        token_id = tx.id
        nft = tx.data()

        res = {
            "tx":tx,
            "receipt":receipt,
            "token_id": token_id,
            "nft_data": nft.metadata,
            "contract_address": EDITION_ADDRESS
        }


        result = {
            "token_id": token_id,
            "nft_data": {
                "name": mint_request["meta_data"]["name"],
                "description": mint_request["meta_data"]["description"],
                "image": mint_request["meta_data"]["image"],
            },
            "contract_address": EDITION_ADDRESS,
            "chain_id": "0x4",
            "mint_amount":mint_request["mint_amount"]

        }




        log = {
            "receipt_time":int(start_time),
            "mint_id":mint_request["id"],
            "redis_response_time":int(time.time()),
            "mint_success":True,
            "mint_chain_id":"0x4",
            "mint_contract_address":EDITION_ADDRESS,
            "data":str(result)
        }

        update_mint_history(log)
        send = False
        max_try = 0
        while not send and max_try < 5:
            pool = redis.Redis(host=config.redis_host, port=config.redis_port, decode_responses=True,
                               password=config.redis_pwd, db=0, ssl=True)
            try :
                print("sendding redis",mint_request["id"],max_try)
                pool.rpush("mintRes", json.dumps({
                    "id": mint_request["id"],
                    "success": True,
                    "data": result
                }))
                send = True
                logger.info(f"uploadRedis success -{mint_request['id']}")
            except Exception as E:
                logger.debug(f"uploadRedis-error-{E}-count:{max_try}")
            max_try += 1
            logger.info(f"mint-success-{mint_request}-{True}-{result}")

    except Exception as E:

        logger.debug(f"mint-error-{mint_request}-{False}-{E}")
        log = {
            "receipt_time": int(start_time),
            "mint_id": mint_request["id"],
            "redis_response_time": int(time.time()),
            "mint_success": False,
            "mint_chain_id": "0x4",
            "mint_contract_address": EDITION_ADDRESS,
            "data": str(E)
        }

        update_mint_history(log)
        pool.rpush("mintRes", json.dumps({
            "id": mint_request["id"],
            "success": False,
            "data": str(E)
        }))

