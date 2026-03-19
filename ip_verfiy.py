# -*- coding: utf-8 -*-
"""
代理IP验证模块，异步检查代理池中所有IP的可用性。
使用aiohttp并发请求百度首页，根据响应状态调整IP分数。
"""
import time
from proxy_red import ProxyRedis
import aiohttp
import asyncio

class IpVerify:
    """代理IP验证器，负责周期性验证所有IP"""

    def __init__(self):
        self.pr = ProxyRedis()

    async def check(self, ip):
        """
        验证单个IP：通过代理访问百度首页
        :param ip: 代理IP字符串 "ip:port"
        """
        sem = asyncio.Semaphore(30)  # 限制并发数，避免资源耗尽
        url = 'http://www.baidu.com/'
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
            "sec-ch-ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Microsoft Edge\";v=\"146\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        async with sem:
            try:
                async with aiohttp.ClientSession() as session:
                    # 使用代理发起请求，超时10秒
                    async with session.get(url, timeout=10, headers=headers,
                                           proxy=f'http://{ip}') as response:
                        if response.status == 200 or response.status == 307:
                            self.pr.set_max_score(ip)   # 可用，分数设为100
                            print(f'{ip}可用')
                        else:
                            self.pr.set_reduce_score(ip) # 不可用，减分
                            print(f'{ip}不可用')
            except Exception as e:
                # 请求异常（连接失败、超时等）也视为不可用
                self.pr.set_reduce_score(ip)
                print(f'{ip}不可用')

    async def check_all(self, ips):
        """
        并发验证所有IP
        :param ips: IP列表
        """
        tasks = []
        for ip in ips:
            task = asyncio.create_task(self.check(ip))
            tasks.append(task)
        await asyncio.gather(*tasks)


def run():
    """
    验证循环：每隔5分钟验证一次代理池中所有IP
    启动时先等待15秒，给采集器留出初始填充时间
    """
    time.sleep(15)
    ver = IpVerify()
    while True:
        ips = ver.pr.get_all_ip()           # 获取所有待验证IP
        asyncio.run(ver.check_all(ips))     # 运行异步验证
        time.sleep(300)                      # 间隔5分钟

if __name__ == '__main__':
    run()