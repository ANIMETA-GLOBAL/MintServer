from thirdweb import ThirdwebSDK
from thirdweb.types.nft import NFTMetadataInput, EditionMetadataInput
import json
import config
import redis

# Note that you can customize this metadata however you like

EDITION_ADDRESS = "0x0B892512FC5Ae908f0f4B9A411AaED5Cd0aDab91"

RPC_URL = "https://rinkeby.infura.io/v3/10b156a4ad4449669733898b548f63f9"
HOST_PRIVATE_KEY = config.private_key

# And now you can instantiate the SDK with it


sdk = ThirdwebSDK.from_private_key(HOST_PRIVATE_KEY, "rinkeby")

contract = sdk.get_edition(EDITION_ADDRESS)
pool = redis.Redis(host=config.redis_host, port=config.redis_port, decode_responses=True, db=0)


def mint_nft(mint_request):
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

        print({
            # "tx":tx,
            # "receipt":receipt,
            "token_id": token_id,
            "nft_data": nft.metadata,
            "contract_address": EDITION_ADDRESS
        }
        )

        result = {
            "token_id": token_id,
            "nft_data": {
                "name": mint_request["meta_data"]["name"],
                "description": mint_request["meta_data"]["description"],
                "image": mint_request["meta_data"]["image"],
            },
            "contract_address": EDITION_ADDRESS
        }

        pool.rpush("mintRes", json.dumps({
            "id":mint_request["id"],
            "success": True,
            "data": result
        }))
    except Exception as E:
        pool.rpush("mintRes", json.dumps({
            "id": mint_request["id"],
            "success": False,
            "data": str(E)
        }))
