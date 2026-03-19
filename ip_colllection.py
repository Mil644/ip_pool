# -*- coding: utf-8 -*-
"""
代理IP采集模块，从快代理（kuaidaili.com）和89代理（89ip.cn）抓取免费代理IP。
使用多线程提高采集效率，继承自Thread，每个采集器为一个线程。
"""
import requests
import json
import re
import time
from lxml import etree
from proxy_red import ProxyRedis
from threading import Thread

class IPAbstract(Thread):
    """采集线程的抽象基类，提供公共的Redis存储方法"""

    def __init__(self):
        super().__init__()
        self.proxy_red = ProxyRedis()  # 每个采集器持有一个Redis操作对象

    def save_ip(self, ips):
        """
        将解析出的IP列表存入Redis
        :param ips: 包含 "ip:port" 字符串的列表
        """
        for ip in ips:
            self.proxy_red.add_proxy(ip)


class KuaiIp(IPAbstract):
    """快代理（www.kuaidaili.com）采集器，抓取免费国内普通代理"""

    def __init__(self):
        super().__init__()
        self.session = requests.session()
        # 请求头模拟浏览器，避免被反爬
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "https://www.kuaidaili.com/free/",
            "sec-ch-ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Microsoft Edge\";v=\"146\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
        }
        self.session.headers = self.headers

    def get_ip(self):
        """
        抓取快代理第1页（可修改范围）的IP，通过正则解析JSON数据
        :return: IP列表 ["ip:port", ...]
        """
        response_list = []
        ip_list = []
        # 目前只抓取第1页，可调整range(1, 2)为更多页，但需注意请求间隔
        for i in range(1, 2):
            url = f"https://www.kuaidaili.com/free/intr/{i}/"
            response = self.session.get(url)
            response_list.append(response.text)
            time.sleep(5)  # 爬取间隔，避免IP被封

        for response in response_list:
            # 页面中包含 const fpsList = [...] 的JSON数据
            compile = re.compile(r'const fpsList =(.*?);')
            info_list = re.search(compile, response).group(1)
            info_list = json.loads(info_list)
            for info in info_list:
                ip = info['ip']
                port = info['port']
                ip_list.append(f"{ip}:{port}")
        return ip_list

    def run(self):
        """线程入口，获取IP并保存"""
        ips = self.get_ip()
        self.save_ip(ips)


class Ip89(IPAbstract):
    """89代理（www.89ip.cn）采集器，抓取免费代理"""

    def __init__(self):
        super().__init__()
        self.session = requests.session()
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "https://cn.bing.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
            "sec-ch-ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Microsoft Edge\";v=\"146\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        self.session.headers = self.headers

    def get_ip(self):
        """
        抓取89代理第1页的IP，通过XPath解析表格
        :return: IP列表
        """
        response_list = []
        ip_list = []
        for i in range(1, 2):  # 只抓取第1页
            url = f"https://www.89ip.cn/index_{i}.html"
            response = self.session.get(url)
            response_list.append(response.text)
            time.sleep(5)

        for response in response_list:
            tree = etree.HTML(response)
            # 定位表格中的所有行
            ip_tags = tree.xpath('//table[@class="layui-table"]/tbody/tr')
            for ip_tag in ip_tags:
                ip = ip_tag.xpath('./td[1]/text()')[0].strip()
                port = ip_tag.xpath('./td[2]/text()')[0].strip()
                ip_list.append(f"{ip}:{port}")
        return ip_list

    def run(self):
        ips = self.get_ip()
        self.save_ip(ips)


def run():
    """
    采集入口：循环每隔一小时启动两个采集线程
    """
    while True:
        kuai_thread = KuaiIp()
        Ip89_thread = Ip89()
        kuai_thread.start()
        Ip89_thread.start()
        time.sleep(3600)  # 间隔1小时采集一次

if __name__ == "__main__":
    run()