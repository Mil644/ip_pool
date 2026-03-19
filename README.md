# 代理IP池管理系统

## 简介

这是一个自动维护的代理IP池系统，能够定时从多个免费代理网站采集代理IP，异步验证其可用性，并通过HTTP API提供高质量的可用代理IP。系统采用多进程架构，采集、验证和API服务独立运行，互不干扰。

## 功能特性

- **多源采集**：支持从快代理（kuaidaili.com）和89代理（89ip.cn）抓取免费代理IP。
- **智能验证**：使用异步IO（aiohttp）并发验证代理IP的可用性，通过请求百度首页并根据响应状态调整IP的信用分数。
- **动态存储**：基于Redis有序集合存储代理IP，分数动态变化（可用+100，不可用-10，分数≤0移除），保证IP池的质量。
- **HTTP API**：提供RESTful接口，随机返回一个当前可用的代理IP，方便集成到爬虫或其他应用中。
- **高并发支持**：API服务基于Sanic框架，支持高并发请求，并配置了跨域（CORS）。
- **模块化设计**：采集、验证、API服务分离，通过多进程并行运行，便于扩展和维护。

## 技术栈

- **Python 3.7+**
- **Redis**：用于存储代理IP及分数
- **aiohttp**：异步HTTP客户端，用于验证代理
- **Sanic**：异步Web框架，提供API服务
- **requests**：用于采集模块的同步请求
- **lxml**：解析HTML页面
- **multiprocessing**：多进程管理

## 安装与运行

### 环境要求

- Python 3.7 或更高版本
- Redis 服务（本地或远程）

### 安装依赖

克隆项目后，使用pip安装所需依赖：

```bash
pip install redis aiohttp sanic sanic-cors requests lxml
```

### 配置Redis

确保Redis服务已启动，并在`proxy_red.py`中修改连接参数（默认配置如下）：

```python
self.red = Redis(host='127.0.0.1', port=6379, db=0, password='', decode_responses=True)
```

- `host`：Redis主机地址
- `port`：Redis端口
- `password`：Redis密码（若无则删除该参数）
- `db`：使用的数据库编号

### 启动项目

直接运行主入口文件`main.py`：

```bash
python main.py
```

程序将启动三个子进程：

- **采集进程**：每隔1小时从代理网站抓取新IP
- **验证进程**：每隔5分钟验证代理池中所有IP的可用性
- **API进程**：启动HTTP服务，监听`0.0.0.0:10086`

## 使用说明

### 获取代理IP的API

**接口地址**：`http://127.0.0.1:10086/get_ip`

**请求方式**：GET

**返回格式**：纯文本，内容为 `ip:port`，例如 `123.45.67.89:8080`

### 示例代码

在您的爬虫或应用中，可以通过HTTP请求获取代理IP并使用：

```python
import requests

def get_proxy():
    try:
        ip = requests.get('http://127.0.0.1:10086/get_ip', timeout=5).text
        return ip
    except Exception as e:
        print(f"获取代理失败: {e}")
        return None

# 使用代理访问目标网站
proxy_ip = get_proxy()
if proxy_ip:
    proxies = {
        'http': f'http://{proxy_ip}',
        'https': f'http://{proxy_ip}'
    }
    response = requests.get('http://example.com', proxies=proxies, timeout=10)
    print(response.text)
```

## 项目结构

```
.
├── main.py              # 主入口，启动多进程
├── proxy_red.py         # Redis操作封装，管理代理池
├── ip_colllection.py    # 代理采集模块（快代理、89代理）
├── ip_verfiy.py         # 代理验证模块（异步并发验证）
├── ip_api.py            # API服务模块（Sanic）
├── use_ip.py            # 使用示例
└── README.md            # 项目说明
```

## 配置说明

### 采集间隔与页数

在`ip_colllection.py`中，可以调整每个采集器抓取的页数和间隔：

- `for i in range(1, 2)`：目前只抓取第1页，可修改为更多页
- `time.sleep(5)`：每页请求后的等待时间，避免IP被封

### 验证并发数

在`ip_verfiy.py`的`check`方法中，`Semaphore(30)`限制了最大并发数，可根据网络环境和系统资源调整。

### API服务端口

在`ip_api.py`的`app.run(host='0.0.0.0', port=10086, ...)`中修改端口号。

### Redis分数策略

- 初始分数：50
- 验证成功：设为100
- 验证失败：减10分，分数≤0时移除

可在`proxy_red.py`中调整这些值。

## 注意事项

1. **免费代理的稳定性**：免费代理IP通常时效短、不稳定，建议结合业务需求调整验证频率。
2. **反爬机制**：部分代理网站可能对频繁请求有限制，适当增加采集间隔或使用代理池自身IP进行采集。
3. **Redis密码**：如果Redis设置了密码，务必在`proxy_red.py`中配置正确，否则连接失败。
4. **多进程启动**：在Windows上使用`multiprocessing`时，必须将启动方式设置为`'spawn'`，已在`main.py`中处理。
5. **首次启动**：API服务会延迟30秒启动，以便验证模块完成至少一轮验证，确保有可用IP返回。

## 贡献

欢迎提交Issue或Pull Request，共同完善此项目。

## 许可证

MIT License

---

如有任何问题，请联系作者。
