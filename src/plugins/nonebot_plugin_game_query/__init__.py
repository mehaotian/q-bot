import json
from datetime import datetime
from typing import Optional, Tuple
from nonebot import on_fullmatch, on_regex ,on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.params import RegexGroup
from .config import *
from .take_my_money import pic_creater, list_pic_creater
from .box import get_article_list


# 菜单指令
menu_handle = on_command('群主文章', rule = to_me(), priority=5, block=True)
@menu_handle.handle()
async def menu(bot: Bot, event: Event):
    message = f"\
    执行以下命令可以查询群主的文章哦~\n\
    1. 文章列表 + 页码（默认为1），例：文章列表 1 \n\
    2. 文章详情 + 文章序号，例：文章详情 12 \n\
    3. 最新推送\
    "
    print(message)
    await bot.send(event=event, message=message) 

# 小黑盒爬虫
def hey_box(page: int):
    url = f"https://api.xiaoheihe.cn/game/web/all_recommend/games/?os_type=web&version=999.0.0&show_type=discount&limit=30&offset={str((page - 1) * 30)}"
    json_page = json.loads(other_request(url, headers=header).text)
    result_list = json_page["result"]["list"]
    result = []
    for i in result_list:
        lowest_stat = "无当前是否史低信息"
        is_lowest = i["price"].get("is_lowest", "")
        if not is_lowest:
            is_lowest = i["heybox_price"].get("is_lowest", "")
        if is_lowest == 0:
            lowest_stat = "不是史低哦"
        elif is_lowest == 1:
            lowest_stat = "是史低哦"
        discount = str(i["price"].get("discount", ""))
        if not discount:
            discount = str(i["heybox_price"].get("discount", ""))
        new_lowest = i["price"].get("new_lowest", " ")
        gameinfo = {
            "appid": str(i["appid"]),
            "链接": f"https://store.steampowered.com/app/{str(i['appid'])}",
            "图片": i["game_img"],
            "标题": i["game_name"],
            "原价": str(i["price"]["initial"]),
            "当前价": str(i["price"]["current"]),
            "平史低价": str(i["price"].get("lowest_price", "无平史低价格信息")),
            "折扣比": discount,
            "是否史低": lowest_stat,
            "是否新史低": "好耶!是新史低!" if new_lowest == 1 else " ",
            "截止日期": i["price"].get("deadline_date", "无截止日期信息"),
        }
        result.append(gameinfo)

    return result

# 消息主体拼接
def mes_creater(result, gamename):
    mes_list = []
    print(result[0].get("平台", ""))
    if result[0].get("平台", "") == "":
        content = f"    ***数据来源于小黑盒官网***\n***默认展示小黑盒steam促销页面***"
        for i in range(len(result)):
            mes = (
                f"[CQ:image,file={result[i]['图片']}]\n{result[i]['标题']}\n原价:¥{result[i]['原价']} \
                当前价:¥{result[i]['当前价']}(-{result[i]['折扣比']}%)\n平史低价:¥{result[i]['平史低价']} {result[i]['是否史低']}\n链接:{result[i]['链接']}\
                \n{result[i]['截止日期']}(不一定准确,请以steam为准)\n{result[i]['是否新史低']}\nappid:{result[i]['appid']}".strip()
                .replace("\n ", "")
                .replace("    ", "")
            )
            data = {"type": "node", "data": {
                "name": "sbeam机器人", "uin": "2854196310", "content": mes}}
            mes_list.append(data)
    else:
        content = f"***数据来源于小黑盒官网***\n游戏{gamename}搜索结果如下"
        for i in range(len(result)):
            if "非steam平台" in result[i]["平台"]:
                mes = f"[CQ:image,file={result[i]['其他平台图片']}]\n{result[i]['标题']}\n{result[i]['平台']}\n{result[i]['链接']} (请在pc打开,在手机打开会下载小黑盒app)".strip().replace(
                    "\n ", ""
                )
            elif "免费" in result[i]["原价"]:
                mes = mes = (
                    f"[CQ:image,file={result[i]['图片']}]\n{result[i]['标题']}\n原价:{result[i]['原价']}\n链接:{result[i]['链接']}\nappid:{result[i]['appid']}".strip(
                    )
                    .replace("\n ", "")
                    .replace("    ", "")
                )
            elif result[i]["折扣比"] == "当前无打折信息":
                mes = (
                    f"[CQ:image,file={result[i]['图片']}]\n{result[i]['标题']}\n{result[i]['折扣比']}\n当前价:¥{result[i]['当前价']} \
                        平史低价:¥{result[i]['平史低价']}\n链接:{result[i]['链接']}\nappid:{result[i]['appid']}".strip()
                    .replace("\n ", "")
                    .replace("    ", "")
                )
            else:
                mes = (
                    f"[CQ:image,file={result[i]['图片']}]\n{result[i]['标题']}\n原价:¥{result[i]['原价']} 当前价:¥{result[i]['当前价']}\
                        (-{result[i]['折扣比']}%)\n平史低价:¥{result[i]['平史低价']} {result[i]['是否史低']}\n链接:{result[i]['链接']}\n\
                            {result[i]['截止日期']}\n{result[i]['是否新史低']}\nappid:{result[i]['appid']}".strip()
                    .replace("\n ", "")
                    .replace("    ", "")
                )
            data = {"type": "node", "data": {
                "name": "sbeam机器人", "uin": "2854196310", "content": mes}}
            mes_list.append(data)
    announce = {"type": "node", "data": {
        "name": "sbeam机器人", "uin": "2854196310", "content": content}}
    mes_list.insert(0, announce)
    return mes_list


game = on_fullmatch("特惠", rule=to_me(),  priority=10, block=True)

# 获取小黑盒特惠消息
@game.handle()
async def _(bot: Bot, event: Event):
    gamename = ""
    try:
        data = hey_box(1)
        await bot.send(event=event, message='正在搜索并生成消息中,请稍等片刻!')
    except Exception as e:
        await bot.send(Message(event=event, message=f"哦吼,获取信息出错了,报错内容为{e},请检查运行日志!"))

    try:
        await game.finish(Message(f'[CQ:at,qq={event.get_user_id()}] {mes_creater(data, gamename)}'))

    except Exception as err:
        if "retcode=100" in str(err):
            # await bot.send(event, "消息可能被风控,正在转为其他形式发送!")
            try:
                if send_pic_mes:
                    await bot.send(event, mes_creater(data, gamename))
                    return
                # print(pic_creater(data, is_steam=False))
                # await bot.send(event, f"[CQ:image,file={pic_creater(data, is_steam=False)}]")
                await game.finish(Message(f"[CQ:image,file={pic_creater(data, is_steam=False)}]"))
            except Exception as err:
                if "retcode=100" in str(err):
                    await bot.send(event, "消息可能依旧被风控,无法完成发送!")
        else:
            await bot.send(event, f"发生了其他错误,报错内容为{err},请检查运行日志!")


# qunlist = on_fullmatch("文章列表",  priority=10, block=True)
qunlist = on_regex(r"文章列表(?: (?<!\d)(\d+))?$", priority=98, block=True)
qundetail = on_regex(r"^文章详情 (?<!\d)(\d+)$", priority=99, block=True)
newts = on_fullmatch("最新推送",  priority=97, block=True)

# 获取群文章列表
@qunlist.handle()
async def get_list(bot: Bot, event: Event, args: Tuple[Optional[str], ...] = RegexGroup(),):
    if  len(args) == 0 or args[0] == None:
        page = 1
    else:
        page = int(args[0])
        if page == 0:
            page = 1

    try:
        await bot.send(event=event, message=f'正在搜索群主的小黑盒投稿第{page}页,请稍等片刻吼~')
        data = get_article_list(page)
    except Exception as e:
        await bot.send(Message(event=event, message=f"哦吼,没找到呢！可能是获取出错！"))

    # 如果 data 长度为 0 说明没有数据
    if len(data) == 0:
        await bot.send(event, "没有找到群主的小黑盒投稿呢！看看是不是页数输错了呢！")
        return

    try:
        await bot.send(event, message=Message(f"[CQ:image,file={list_pic_creater(data,page = page)}]"))
        await bot.send(event, message=Message(f"共为你找到 {len(data)} 篇文章 ，回复 文章详情 + 文章序号，可查看文章详情，如：文章详情 1"))
    except Exception as err:
        print(err)
        if "retcode=100" in str(err):
            await bot.send(event, "消息可能依旧被风控,无法完成发送!")


@qundetail.handle()
async def get_detail(bot: Bot, event: Event, args: Tuple[Optional[str], ...] = RegexGroup(),):
    index = int(args[0])
    if index == 0:
        await bot.send(event=event, message=f'序号不能为0哦~')
        return

    page_size = 20

    if index <= 0:
        page = 1
    else:
        page = (index - 1) // page_size + 1

    # 获取当前数字下标
    if index < 20:
        idx = index
    else:
        idx = index % page_size

    idx = idx - 1

    try:
        await bot.send(event=event, message=f'正在搜索文章详情,请稍等片刻吼~')

        data = get_article_list(page)
         # 如果 data 长度为 0 说明没有数据
        if len(data) == 0:
            await bot.send(event, "没有找到群主的小黑盒投稿呢！看看是不是输错了呢！")
            return

        res = data[idx]
       
        at = MessageSegment.at(event.user_id)
        image = MessageSegment(type="image", data={"file": res['图片']})
        content = f'\n\n为您找到如下文章 \n标题：{res["标题"]} \n链接：{res["链接"]}'

        await bot.send(event=event, message=Message(at + content + "\n" +image ))
    except Exception as err:
        if "retcode=100" in str(err):
            await bot.send(event, "消息可能被风控,无法完成发送!")
        else:
            await bot.send(Message(event=event, message=f"哦吼,没找到呢！可能是获取出错！"))

@newts.handle()
async def get_newts(bot: Bot, event: Event):
    index = 0 
    page = 1
    try:
        await bot.send(event=event, message=f'正在拉取最新推送文章,请稍等片刻吼~')

        data = get_article_list(page)
         # 如果 data 长度为 0 说明没有数据
        if len(data) == 0:
            await bot.send(event, "没有找到群主的小黑盒投稿呢！看看是不是输错了呢！")
            return

        res = data[index]
       
        at = MessageSegment.at(event.user_id)
        image = MessageSegment(type="image", data={"file": res['图片']})
        content = f'\n\n群主最新文章，赶快送上你的5电哦~ \n标题：{res["标题"]} \n链接：{res["链接"]}'

        await bot.send(event=event, message=Message(at + content + "\n" +image ))
    except Exception as err:
        if "retcode=100" in str(err):
            await bot.send(event, "消息可能被风控,无法完成发送!")
        else:
            await bot.send(Message(event=event, message=f"哦吼,没找到呢！可能是获取出错！"))

