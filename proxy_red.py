# -*- coding: utf-8 -*-
"""
代理IP存储模块，使用Redis有序集合维护代理池。
- 分数（score）表示IP的可用性，100为最高分（可用），每次验证失败减少10分，直至0分被移除。
- 使用Redis的zset结构，可以方便地按分数排序和随机获取高分IP。
"""
from redis import Redis
import random

class ProxyRedis:
    """封装Redis操作，管理代理IP的有序集合"""

    def __init__(self):
        """初始化Redis连接，配置主机、端口、密码和响应解码"""
        self.red = Redis(host='127.0.0.1', port=6379, db=0,
                         password='password', decode_responses=True)

    def add_proxy(self, ip):
        """
        添加代理IP到集合中，初始分数为50。
        如果IP已存在则不再重复添加。
        :param ip: 字符串格式的 "IP:端口"
        """
        if self.red.zrank('proxy_ip', ip) is None:  # 检查IP是否已存在
            self.red.zadd('proxy_ip', {ip: 50})
            print(f"添加代理成功: {ip}")
        else:
            print(f"代理已存在: {ip}")

    def get_all_ip(self):
        """
        获取代理池中的所有IP（按分数升序排列）
        :return: IP列表
        """
        return self.red.zrange('proxy_ip', 0, -1)

    def set_max_score(self, ip):
        """
        将IP的分数设为100，表示验证通过可用
        :param ip: 代理IP字符串
        """
        self.red.zadd('proxy_ip', {ip: 100})
        print(f"代理可用: {ip}")

    def set_reduce_score(self, ip):
        """
        降低IP的分数（减10），若分数<=0则从池中移除
        :param ip: 代理IP字符串
        """
        self.red.zincrby('proxy_ip', -10, ip)
        if self.red.zscore('proxy_ip', ip) <= 0:
            self.red.zrem('proxy_ip', ip)

    def get_usdeful_ip(self):
        """
        随机返回一个分数为100的可用IP（用于API接口）
        :return: 代理IP字符串，如果无可用IP则可能抛出异常（应自行处理）
        """
        ip_list = self.red.zrangebyscore('proxy_ip', 100, 100)
        ip = random.choice(ip_list)
        return ip

if __name__ == '__main__':
    # 简单测试
    proxy_redis = ProxyRedis()
    proxy_redis.get_usdeful_ip()