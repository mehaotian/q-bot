import hashlib
import time
import random
import json
from .config import *


m = ['a', 'b', 'e', 'g', 'h', 'i', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'w']

def g(e):
    return 255 & (e << 1 ^ 27) if 128 & e else e << 1

def x(e):
    return g(e) ^ e

def w(e):
    return x(g(e))

def v(e):
    return w(x(g(e)))

def C(e):
    return v(e) ^ w(e) ^ x(e)


def conversion(i):
    e = [ord(c) for c in i[-4:]]
    t = [0, 0, 0, 0]
    t[0] = C(e[0]) ^ v(e[1]) ^ w(e[2]) ^ x(e[3])
    t[1] = x(e[0]) ^ C(e[1]) ^ v(e[2]) ^ w(e[3])
    t[2] = w(e[0]) ^ x(e[1]) ^ C(e[2]) ^ v(e[3])
    t[3] = v(e[0]) ^ w(e[1]) ^ x(e[2]) ^ C(e[3])
    e[0] = t[0]
    e[1] = t[1]
    e[2] = t[2]
    e[3] = t[3]
    return sum(e)


def E(e, t, n):
    e = "/" + "/".join(filter(lambda x: x, e.split("/"))) + "/"
    # o = "JKMNPQRTX1234OABCDFG56789H"
    # r = Y(n + o)
    # a = Y(str(t) + e + r)[:9].ljust(9, "0")
    # s = int.from_bytes(a.encode(), byteorder='big')

    i = ""
    o = "JKMNPQRTX1234OABCDFG56789H"

    r = Y("".join(filter(lambda e: e.isdigit(), n + o)))
    a = Y(str(t) + e + r)
    a = "".join(filter(lambda e: e.isdigit(), a))[:9]
    aWithZero = a + "0" * (9 - len(a))

    s = int(aWithZero)
    for _ in range(5):
        p = s % len(o)
        s = s // len(o)
        i += o[p]
    
    d = str(conversion(i) % 100)
    if len(d) < 2:
        d = "0" + d
    return i + d

def Y(t):
    md5 = hashlib.md5()
    md5.update(t.encode())
    return md5.hexdigest()

def D(e):
    t = {}
    n = int(time.time())
    p = str(n) + str(random.random())[:18]
    i = Y(p).upper()
    t['hkey'] = F_g(e, n, i)
    t["_time"] = n
    t["nonce"] = i
    return t

def F_g(e, t, n):
    return E(e, t + 1, n)

text = "/bbs/web/profile/post/links"

def r_url(page: int):
    obj = D(text)
    return f'https://api.xiaoheihe.cn/bbs/web/profile/post/links?os_type=web&version=999.0.3&x_app=heybox_website&x_client_type=web&heybox_id=43580550&x_os_type=Mac&hkey={obj["hkey"]}&_time={obj["_time"]}&nonce={obj["nonce"]}&userid=1985029&limit=20&offset={str((page - 1) * 20)}&post_type=2&list_type=article'

header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.xiaoheihe.cn/",
}

def get_article_list(page: int = 1):
    url = r_url(page)
    print(url)
    json_page = json.loads(other_request(url, headers=header).text)
    result_list = json_page["post_links"]
    result = []
    for item in result_list:
        gameinfo = {
            "链接": item["share_url"],
            "图片": item["thumbs"][0],
            "标题": item["title"],
        }
        result.append(gameinfo)

    return result