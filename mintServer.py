from aiohttp import web
import json
import mint_mod
routes = web.RouteTableDef()

@routes.post('/mint')
async def hello(request):
    print("get mint request")
    data = await request.json()
    print(data)

    try:
        res = mint_mod.mint_nft(data["mint_request"])
        print(res)
        return web.json_response({"success": True, "data": res})
    except Exception as E:
        return web.json_response({"success": False, "data": str(E)})





app = web.Application()
app.add_routes(routes)
web.run_app(app,port=6666)
