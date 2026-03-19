# -*- coding: utf-8 -*-
"""
主入口模块，使用多进程分别启动采集、验证和API服务。
由于三个服务需要长期运行且互不干扰，使用进程隔离。
"""
import ip_api
import ip_colllection
import ip_verfiy
from multiprocessing import Process, set_start_method

if __name__ == '__main__':
    # 创建三个子进程，分别执行对应模块的run函数
    collect = Process(target=ip_colllection.run)   # 采集进程
    verify = Process(target=ip_verfiy.run)         # 验证进程
    api = Process(target=ip_api.run)                # API服务进程

    # 启动所有进程
    collect.start()
    verify.start()
    api.start()

