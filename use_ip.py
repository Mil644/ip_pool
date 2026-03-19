# -*- coding: utf-8 -*-
"""
使用代理IP的示例模块，演示如何从API获取IP并利用该IP访问百度。
实际应用中可将此类集成到爬虫或需要代理的客户端中。
"""
import requests

class use_ip:
    """代理IP使用示例类"""

    def __init__(self):
        self.ip_url = 'http://127.0.0.1:10086/get_ip'  # API地址

    def get_ip(self):
        """
        调用API获取一个可用代理IP
        :return: IP字符串 "ip:port" 或 None（如果失败）
        """
        try:
            ip = requests.get(self.ip_url).text
            print(f"DNS解析成功，IP地址: {ip}")
            return ip
        except Exception as e:
            print(f"DNS解析失败: {e}")
            return None

    def set_ip(self, ip):
        """
        使用给定的代理IP发起请求访问百度，并打印响应内容
        :param ip: 代理IP字符串
        """
        session = requests.Session()
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://www.ipify.org/",
            "sec-ch-ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Microsoft Edge\";v=\"146\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "script",
            "sec-fetch-mode": "no-cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
        }
        session.headers = headers
        my_proxies = {
            'http': f'http://{ip}',
            'https': f'http://{ip}'
        }
        response = session.get('http://www.baidu.com',
                               proxies=my_proxies,
                               timeout=10).text
        print(response)  # 打印百度首页HTML


def run():
    """执行示例：获取IP并使用"""
    user = use_ip()
    ip = user.get_ip()
    user.set_ip(ip)

if __name__ == '__main__':
    run()