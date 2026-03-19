# -*- coding: utf-8 -*-
"""
代理IP API服务模块，使用Sanic提供RESTful接口，返回一个可用的代理IP。
支持跨域请求（CORS），便于前端或其他服务调用。
"""
from sanic import Sanic
from sanic.response import text
from sanic_cors import CORS
from proxy_red import ProxyRedis
import time

app = Sanic('ip')   # 创建Sanic应用实例
CORS(app)            # 启用跨域资源共享

@app.route('/get_ip')
def get_ip(request):
    """
    处理GET请求，从代理池随机返回一个分数为100的可用IP。
    返回格式为纯文本 "ip:port"
    """
    pr = ProxyRedis()
    ip = pr.get_usdeful_ip()
    return text(ip)

def run():
    """
    启动API服务，监听0.0.0.0:10086。
    启动前等待30秒，确保验证模块至少完成一轮验证，有可用IP。
    """
    time.sleep(30)
    app.run(host='0.0.0.0', port=10086, single_process=True)

if __name__ == '__main__':
    run()