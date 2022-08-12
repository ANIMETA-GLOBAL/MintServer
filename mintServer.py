from aiohttp import web
import json
import new_mint_mod
import time
routes = web.RouteTableDef()
import logging
import os.path
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))[:-4]
log_path = os.path.dirname(os.getcwd()) + '/MintServer/logs/'
log_name = log_path + rq + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='a')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


import threading

def minting(data):
    res = new_mint_mod.NFTFactory((data["mint_request"])).mint()
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
        logger.info("receipt mint request:" + str(data))
        return web.json_response({"receipt": True, })
    except Exception as E:
        return web.json_response({"receipt": False, "data": str(E)})





app = web.Application()
app.add_routes(routes)
web.run_app(app,port=6666)
