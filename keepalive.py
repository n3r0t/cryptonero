import urllib3
import threading
import asyncio

async def keepalive():
    http = urllib3.PoolManager()
    http.request('get','1.1.1.1')
    t = threading.Thread(target=asyncio.run,args=(keepalive(), ))
    t.start()
    await asyncio.sleep(600)
