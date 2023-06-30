import random
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.message import Message
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent, \
    MessageSegment, Message

from .path import *
from .welcome_utils.config import config
from .welcome_utils.message_util import MessageBuild


notice_handle = on_notice(priority=5, block=True)

greetings = [
    "来啦!来了你可就不能走了哦~",
    "欢迎新朋友的加入~",
    "欢迎新人~",
    "这可让你来着了，群里都是妹妹哦~",
    "欢迎欢迎，你是GG和是MM呀？", 
    "欢迎新人，群里的妹妹们都在等你哦~",
    "欢迎新人，群里的哥哥们都在等你哦~",
]


# 匹配词库
def get_wel_word(text) -> str:
    return random.choice(text)

@notice_handle.handle()
async def GroupNewMember(bot: Bot, event: GroupIncreaseNoticeEvent):
    greet_emoticon = MessageBuild.Image(bg_file,size=(300,300), mode='RGBA')
    if event.user_id == event.self_id:
        await bot.send_group_msg(group_id=event.group_id, message=Message(
            MessageSegment.text('这是哪里？哦？让我康康！\n') + greet_emoticon))
    elif event.group_id not in config.paimon_greet_ban:
        await bot.send_group_msg(group_id=event.group_id, message=Message(
            MessageSegment.at(event.user_id) + MessageSegment.text(f'{get_wel_word(greetings)}\n') + greet_emoticon))
