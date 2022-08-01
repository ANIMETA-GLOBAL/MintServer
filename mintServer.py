from aiohttp import web
import json
import mint_mod
routes = web.RouteTableDef()


import threading

def minting(data):
    res = mint_mod.mint_nft(data["mint_request"])
    print(res)


@routes.post('/mint')
async def hello(request):
    print("get mint request")
    data = await request.json()
    print(data)

    try:
        t = threading.Thread(target=minting, args=(data,))
        t.start()
        # res = mint_mod.mint_nft(data["mint_request"])
        # print(res)
        return web.json_response({"receipt": True, })
    except Exception as E:
        return web.json_response({"receipt": False, "data": str(E)})





app = web.Application()
app.add_routes(routes)
web.run_app(app,port=6666)
