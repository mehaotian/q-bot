
from typing import Optional, Tuple
from nonebot import on_fullmatch, on_regex ,on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.params import RegexGroup
from .config import *
from .take_my_money import pic_creater, list_pic_creater
from .box import get_article_list
from .utils import hey_box, mes_creater

# 菜单指令
menu_handle = on_command('群主文章', rule = to_me(), priority=5, block=True)
# 小黑盒特惠
game = on_fullmatch("特惠", rule=to_me(),  priority=10, block=True)

# 群主文章
qunlist = on_regex(r"文章列表(?: (?<!\d)(\d+))?$", priority=98, block=True)
qundetail = on_regex(r"^文章详情 (?<!\d)(\d+)$", priority=99, block=True)
newts = on_fullmatch("最新推送",  priority=97, block=True)

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
            try:
                if send_pic_mes:
                    await bot.send(event, mes_creater(data, gamename))
                    return
                await game.finish(Message(f"[CQ:image,file={pic_creater(data, is_steam=False)}]"))
            except Exception as err:
                if "retcode=100" in str(err):
                    await bot.send(event, "消息可能依旧被风控,无法完成发送!")
        else:
            await bot.send(event, f"发生了其他错误,报错内容为{err},请检查运行日志!")

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

# 详情查询
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
# 最新推送
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

