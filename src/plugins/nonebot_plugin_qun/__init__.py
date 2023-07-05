
from nonebot import on_command, on_notice
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import Message
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent, \
    MessageSegment, Message

from .path import *
from .welcome_utils.config import config
from .welcome_utils.message_util import MessageBuild
from .config import *

# 进去通知指令
notice_handle = on_notice(priority=5, block=True)
# 菜单指令
menu_handle = on_command('菜单', aliases={"help", "帮助"} ,priority=5, block=True)

@menu_handle.handle()
async def menu(bot: Bot, event: Event):
    message = f"\
    哈喽哈喽，我是群内小助手，你可以随意使用我哦~ 下面是我的功能：\n\
    1. 群主文章查询  ，@喵喵Bot并回复 /群主文章 \n\
    2. 喵喵GPT，@喵喵Bot并回复 喵喵 \n\
    3. 小黑盒特惠  @喵喵Bot并回复 特惠\
    "
    print(message)
    await bot.send(event=event, message=message) 

# 进群通知
@notice_handle.handle()
async def GroupNewMember(bot: Bot, event: GroupIncreaseNoticeEvent):
    greet_emoticon = MessageBuild.Image(bg_file,size=(300,300), mode='RGBA')
    if event.user_id == event.self_id:
        await bot.send_group_msg(group_id=event.group_id, message=Message(
            MessageSegment.text('这是哪里？哦？让我康康！\n') + greet_emoticon))
    elif event.group_id not in config.paimon_greet_ban:
        await bot.send_group_msg(group_id=event.group_id, message=Message(
            MessageSegment.at(event.user_id) + MessageSegment.text(f'{get_wel_word(greetings)}\n') + greet_emoticon))
