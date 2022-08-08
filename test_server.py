import requests

url = 'http://localhost:6666/mint'
data = {'mint_request': {
    "meta_data":
        {
            "name":"test nft",
            "description":" test nft",
            "image":"https://ipfs.io/ipfs/QmSWgjuqnKh4tApbHE8wfRoUSG9RWj6DX4NxPUJ2Q225M6?filename=5494c0fa4c8d21450ef7357d0929a5d8.jpegg"
        },
    "mint_amount":100,
    "id":7948749
}}

x = requests.post(url, json=data)

print(x.text)
