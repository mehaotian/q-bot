import re
import time
from nonebot import (
    on_command,
    on_regex,
    on_message
)
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    GROUP,
    GROUP_ADMIN,
    GROUP_OWNER,
    Bot,
    Event,
    MessageSegment,
    GroupMessageEvent,
    Message,
)
from nonebot.params import RegexGroup, CommandArg
from nonebot.typing import T_State
from .Game import Explore, data, Game
from .utils import find_duplicate_names
from .txt2img import txt2img

# 获取游戏操作
game = Game()


# 开启/关闭世界
adminOpenGame = on_regex(
    r"^(开启|关闭)世界",
    rule=to_me(),
    permission=SUPERUSER | GROUP_ADMIN,
    priority=20, block=True
)

# 开始结束游戏操作


@adminOpenGame.handle()
async def open_close_game(bot: Bot, event: Event, args=RegexGroup()):
    mode = args[0]
    await game.run(mode, bot, event)


async def user_add_check(event: Event, state: T_State):
    """
    游戏是否开始
    """
    is_start = data.game.is_start
    if is_start:
        return True
    else:
        return False

# 给予或减少用户金币
give_player_gold = on_regex(
    '^金币 ([+-]?\d+)',
    rule=to_me(),
    permission=SUPERUSER | GROUP_ADMIN,
    priority=22,
    block=True
)


@give_player_gold.handle()
async def give_gold_handle(bot: Bot, event: GroupMessageEvent, args=RegexGroup()):
    mode = args[0]
    await game.give_player_gold(bot, event, mode)

# 给玩家升级或降级
give_player_level = on_regex(
    '^等级 ([+-]?\d+)',
    rule=to_me(),
    permission=SUPERUSER | GROUP_ADMIN,
    priority=22,
    block=True
)


@give_player_level.handle()
async def give_level_handle(bot: Bot, event: GroupMessageEvent, args=RegexGroup()):
    mode = args[0]
    await game.give_player_level(bot, event, mode)

# ban 玩家
reg = r"(ban)\s+(\d+)(?:\s+(.*))?(?:\s+\[CQ:at,qq=\w+\])?"
ban_player = on_regex(
    reg,
    rule=to_me(),
    permission=SUPERUSER | GROUP_ADMIN,
    priority=22,
    block=True
)


@ban_player.handle()
async def ban_player_handle(bot: Bot, event: GroupMessageEvent, args=RegexGroup()):
    await game.ban_player(bot, event, reg)

# 用户加入游戏
userAddGame = on_command("踏入江湖", rule=user_add_check, priority=20, block=True)


@userAddGame.handle()
async def add_game_handle(bot: Bot, event: Event, args: Message = CommandArg()):
    users = data.user
    user_id = event.user_id
    at = MessageSegment.at(event.user_id)
    if user_id in users:
        await bot.send(event, Message(f'{at} 您已身在江湖，请去尽情施展你的才华吧！！'))
        return
    # 获取用户昵称
    text = args.extract_plain_text()
    mode = text if text else event.sender.nickname
    user = await game.add(event, mode)
    await bot.send(event, Message(f'欢迎『{user.nickname}』踏入江湖，江湖路漫漫，且行且珍惜！'))
    msg = (
        f'◆ 等级：{user.level} 级（1/100）\n'
        f'◆ 称号：初入江湖\n'
        f'◆ 金钱：{user.gold} 金\n'
        f'◆ 装备：无\n'
        f'◆ 天赋：无\n'
        f'◆ 状态：自由自在\n'
        f'◆ 力量：{user.attr.STR} \n'
        f'◆ 敏捷：{user.attr.AGI}\n'
        f'◆ 智力：{user.attr.INT}\n'
        f'◆ 体力：{user.attr.STA }'
    )

    # await bot.send(event, Message(at + msg))
    img = txt2img(msg=msg)
    img_data = MessageSegment.image(file=img)
    await bot.send(event, Message(at + img_data))


"""
游戏指令 --
"""


async def game_rule(event: Event):  # 判断用户是否在游戏中
    return await game.user_check(event)

# 查询玩家等级
query_exp = on_command("等级", rule=game_rule, priority=80, block=True)


@query_exp.handle()
async def query_exp_handle(bot: Bot, event: Event):
    users = data.user
    user = users[event.user_id]
    at = MessageSegment.at(event.user_id)
    msg = (
        f'『{user.nickname}』 您当前等级：{user.level} 级，经验值：{user.exp}/{user.next_exp}'
    )
    await bot.send(event, Message(at + msg))


# 判断用户是否可进行游戏
async def user_check_rule(event: Event):
    """
    判断用户是否可进行游戏
    """
    game = data.game  # 获取游戏信息
    users = data.user  # 获取用户信息

    is_start = game.is_start
    user_id = event.user_id

    # is_start = True 并且 user_id 在 users 中返回True
    if is_start and user_id in users:
        return True
    else:
        return False
# 查询玩家属性信息
query_user = on_command("看看我", rule=user_check_rule, priority=80, block=True)


@query_user.handle()
async def query_user_handle(bot: Bot, event: Event):
    users = data.user
    user_id = event.user_id
    user = users[user_id]
    prison = user.prison
    at = MessageSegment.at(user_id)
    if prison:
        user_prison = data.prison[user_id]
        await bot.send(event, Message(f'『{user.nickname}』已经锒铛入狱，啧啧！做点人事儿吧'))
        msg = (
            f'◆ 等级：{user.level} 级（{user.exp}/{user.next_exp}）\n'
            f'◆ 称号：初入江湖\n'
            f'◆ 状态：锒铛入狱\n'
            f'◆ 需要服刑：{user_prison.prison_time}分钟\n'
            f'◆ 被捕理由：{user_prison.prison_reason}\n'
            f'◆ 保释金：{user_prison.prison_bail}'
        )
        img = txt2img(msg=msg)
        img_data = MessageSegment.image(file=img)
        await bot.send(event, Message(at + img_data))
        return True

    eqiu = user.equip
    attr_extra = user.attr_extra
    eqiu_msg = ''
    try:
        eqiu_data = eqiu['头']
        eqiu_msg += f'◆ 头：{eqiu_data.name} \n'
    except:
        eqiu_msg += f'◆ 头：空\n'
    try:
        eqiu_data = eqiu['身']
        eqiu_msg += f'◆ 身：{eqiu_data.name} \n'
    except:
        eqiu_msg += f'◆ 身：空\n'
    try:
        eqiu_data = eqiu['臂']
        eqiu_msg += f'◆ 臂：{eqiu_data.name} \n'
    except:
        eqiu_msg += f'◆ 臂：空\n'
    try:
        eqiu_data = eqiu['腿']
        eqiu_msg += f'◆ 腿：{eqiu_data.name} \n'
    except:
        eqiu_msg += f'◆ 腿：空\n'

    # 计算力量
    if attr_extra.STR:
        STR = f'{user.attr.STR}（+{attr_extra.STR}）'
    else:
        STR = user.attr.STR

    # 计算敏捷
    if attr_extra.AGI:
        AGI = f'{user.attr.AGI}（+{attr_extra.AGI}）'
    else:
        AGI = user.attr.AGI

    # 计算智力
    if attr_extra.INT:
        INT = f'{user.attr.INT}（+{attr_extra.INT}）'
    else:
        INT = user.attr.INT
    # 计算体力
    if attr_extra.STA:
        STA = f'{user.attr.STA}（+{attr_extra.STA}）'
    else:
        STA = user.attr.STA
    await bot.send(event, Message(f'『{user.nickname}』使用了内视，仔细观察了自己一下'))
    msg = (
        f'◆ 等级：{user.level} 级（{user.exp}/{user.next_exp}）\n'
        f'◆ 称号：初入江湖\n'
        f'◆ 金钱：{user.gold} 金\n'
        f'◆ 天赋：牛子变大术\n'
        f'◆ 状态：自由自在\n'
        + eqiu_msg +
        f'◆ 力量：{STR} \n'
        f'◆ 敏捷：{AGI}\n'
        f'◆ 智力：{INT}\n'
        f'◆ 体力：{STA }'
    )
    img = txt2img(msg=msg)
    img_data = MessageSegment.image(file=img)
    await bot.send(event, Message(at + img_data))

# 查询隐藏属性
query_hidden = on_command("隐藏属性", rule=game_rule, priority=80, block=True)


@query_hidden.handle()
async def query_hidden_handle(bot: Bot, event: Event):
    users = data.user
    user = users[event.user_id]
    at = MessageSegment.at(event.user_id)

    eqiu = user.equip
    attr_extra = user.attr_extra
    eqiu_msg = ''
    try:
        eqiu_data = eqiu['头']
        eqiu_msg += f'◆ 头：{eqiu_data.name} \n'
    except:
        eqiu_msg += f'◆ 头：空\n'
    try:
        eqiu_data = eqiu['身']
        eqiu_msg += f'◆ 身：{eqiu_data.name} \n'
    except:
        eqiu_msg += f'◆ 身：空\n'
    try:
        eqiu_data = eqiu['臂']
        eqiu_msg += f'◆ 臂：{eqiu_data.name} \n'
    except:
        eqiu_msg += f'◆ 臂：空\n'
    try:
        eqiu_data = eqiu['腿']
        eqiu_msg += f'◆ 腿：{eqiu_data.name} \n'
    except:
        eqiu_msg += f'◆ 腿：空\n'

    # 计算力量
    if attr_extra.STR:
        STR = f'{user.attr.STR}（+{attr_extra.STR}）'
    else:
        STR = user.attr.STR

    # 计算敏捷
    if attr_extra.AGI:
        AGI = f'{user.attr.AGI}（+{attr_extra.AGI}）'
    else:
        AGI = user.attr.AGI

    # 计算智力
    if attr_extra.INT:
        INT = f'{user.attr.INT}（+{attr_extra.INT}）'
    else:
        INT = user.attr.INT
    # 计算体力
    if attr_extra.STA:
        STA = f'{user.attr.STA}（+{attr_extra.STA}）'
    else:
        STA = user.attr.STA

    await bot.send(event, Message(f'『{user.nickname}』使用了内视，更仔细的观察了自己一下'))

    prison = user.prison
    prison_msg = '自由自在'
    if prison:
        prison_msg = '锒铛入狱'

    msg = (
        f'◆ 等级：{user.level} 级（{user.exp}/{user.next_exp}）\n'
        f'◆ 金钱：{user.gold} 金\n'
        f'◆ 状态：{prison_msg}\n'
        + eqiu_msg +
        f'◆ 力量：{STR} \n'
        f'◆ 敏捷：{AGI}\n'
        f'◆ 智力：{INT}\n'
        f'◆ 体力：{STA }\n'
        f'◆ 防御力：{user.attr.DEF}\n'
        f'◆ 攻击力：{user.attr.ATK}\n'
        f'◆ 抗性：{user.attr.RES}\n'
        f'◆ 攻击速度：{int(user.attr.AS*100)}\n'
        f'◆ 暴击率：{int(user.attr.CRI*100)}\n'
        f'◆ 命中率：{int(user.attr.HIT*100)}\n'
        f'◆ 闪避率：{int(user.attr.DOD*100)}\n'
        f'◆ HP：{user.attr.HP}\n'
        f'◆ MP：{user.attr.MP}'
    )
    img = txt2img(msg=msg)
    img_data = MessageSegment.image(file=img)
    await bot.send(event, Message(at + img_data))


# 玩家签到
sign_in = on_command("签到", rule=game_rule, priority=80, block=True)


@sign_in.handle()
async def sign_in_handle(bot: Bot, event: Event):
    at = MessageSegment.at(event.user_id)
    msg = await game.sign_in(event)
    await bot.send(event, Message(at + msg))

# 查看玩家背包
player_bag = on_command("背包", rule=game_rule, priority=80, block=True)


@player_bag.handle()
async def player_bag_handle(bot: Bot, event: Event):
    users = data.user
    user = users[event.user_id]
    at = MessageSegment.at(event.user_id)

    user_bag = user.bag
    # 装备
    equips_msg = ''
    # 副本
    scenes_msg = ''

    for _, item in user_bag.items():
        type = item.type
        if type == '装备':
            is_equip = item.is_equip
            if is_equip:
                equip_msg = f' ◦ 装备中〕'
            else:
                equip_msg = f'〕'

            if item.count > 1:
                equips_msg += f'〔{item.name}*{item.count}{equip_msg}'
            else:
                equips_msg += f'〔{item.name}{equip_msg}'
        if type == '副本':
            if item.count > 1:
                scenes_msg += f'〔{item.name}*{item.count}〕'
            else:
                scenes_msg += f'〔{item.name}〕'

    await bot.send(event, Message(f'『{user.nickname}』拿起背包，准备看看都有啥'))

    msg = ''
    print(scenes_msg)
    if equips_msg:
        msg += f'◆ 装备：{equips_msg}\n\n'
    if scenes_msg:
        msg += f'◆ 秘境路引：{scenes_msg}\n'
    if len(user_bag) == 0:
        msg = '嘶~,背包里什么都没有！'
        await bot.send(event, Message(at + msg))
        return True

    img = txt2img(msg=msg, bg_path="player.png", size=40)
    img_data = MessageSegment.image(file=img)
    await bot.send(event, Message(at + img_data))

# 装备玩家装备
player_equip = on_command("装备", rule=game_rule, priority=80, block=True)


@player_equip.handle()
async def player_equip_handle(bot: Bot, event: Event, args: Message = CommandArg()):
    user_id = event.user_id
    user = data.user[user_id]
    at = MessageSegment.at(user_id)
    # 获取用户昵称
    text = args.extract_plain_text()
    # 有参数才进行下面的判断
    if text:
        msg = await game.player_equip(event, text)
        await bot.send(event, Message(at + msg))
    else:
        await bot.send(event, Message(at + '你要装备什么？'))


# 查询物品详细信息
query_item = on_command(
    "查看", aliases={'查询', 'q', 'query'}, rule=game_rule, priority=80, block=True)


@query_item.handle()
async def query_item_handle(bot: Bot, event: Event, args: Message = CommandArg()):

    await game.query_item(bot, event, args)


# 玩家探索
explore = on_command("探索", rule=game_rule, priority=80, block=True)


@explore.handle()
async def explore_handle(bot: Bot, event: Event, args: Message = CommandArg()):
    user_id = event.user_id
    user = data.user[user_id]
    at = MessageSegment.at(user_id)
    # 获取用户昵称
    text = args.extract_plain_text()
    # 有参数才进行下面的判断
    if text:
        pattern = r"^[1-9][0-9]*$"
        if re.match(pattern, text):
            text = int(text)
            step = user.step
            if text > step:
                text = step

    else:
        # 如果没有参数，就只探索一次
        text = 1

    
    exp = Explore(event)
    msg, get_data, is_up = exp.run(text)
    # await bot.send(event, Message(at + msg))

    img = txt2img(msg=msg, size= 60)
    img_data = MessageSegment.image(file=img)
    await bot.send(event, Message(at + img_data))

    res_msg = ''
    for name in get_data:
        row = get_data[name]
        if name == '金币':
            res_msg += f'\n✤ 获取 {name}：{row} 金'
        elif name == '经验':
            res_msg += f'\n✤ 获取 {name}：{row} 经验'
        elif name == '装备':
            res_msg += f'\n✤ 获取装备：'
            res_msg += find_duplicate_names(row)

        elif name == '秘籍':
            res_msg += f'\n✤ 获取秘籍：'
            res_msg += find_duplicate_names(row)
        elif name == '副本':
            res_msg += f'\n✤ 获得秘境路引：'
            # for i in row:
            #     res_msg += f'《{i["name"]}》'
            res_msg += find_duplicate_names(row)
        else:
            pass
    if res_msg:

        await bot.send(event, Message(at + res_msg))
    else:
        await bot.send(event, Message(at + '屁玩意儿没获得'))

    # 升级
    if is_up:
        msg = (f'恭喜『{user.nickname}』升级了，当前等级：{user.level} 级')
        await bot.send(event, Message(at + msg))


# 玩家 pk
pk_player = on_command("pk", rule=game_rule, priority=80, block=True)


@pk_player.handle()
async def pk_player_handle(bot: Bot, event: Event):
    at = MessageSegment.at(event.user_id)
    player1 = data.user[event.user_id]

    msg , user_id ,is_pk = await game.pk_player(event)

    if user_id and is_pk:
        player2 = data.user[user_id]
        await bot.send(event, Message(f"『{player1.nickname}』与『{player2.nickname}』的战斗正式拉开了序幕。"))

    if is_pk:
    # await bot.send(event, Message(at + msg))
        img = txt2img(msg=msg)
        img_data = MessageSegment.image(file=img)
        await bot.send(event, Message(at + img_data))
    else:
        await bot.send(event, Message(at + msg))


# 下副本 
next_scene = on_command("进入秘境", rule=game_rule, priority=80, block=True)
@next_scene.handle()
async def next_scene_handle(bot: Bot, event: Event, args: Message = CommandArg()):
    user_id = event.user_id
    user = data.user[user_id]
    at = MessageSegment.at(user_id)
    text = args.extract_plain_text()
    if not text:
        return '请输入秘境名称名称！'

    await bot.send(event, Message(f"『{user.nickname}』正在做战前准备，马上进入秘境！"))

    msg = await game.next_scene(event, text)

    img = txt2img(msg=msg)
    img_data = MessageSegment.image(file=img)
    await bot.send(event, Message(at + img_data))


# 监听用户消息
run_game = on_message(rule=game_rule, priority=20, block=False)

# 获取当前时间戳
lv_time = time.time()


@run_game.handle()
async def run_game_handle(bot: Bot, event: Event, state: T_State):
    # 获取经验
    msg = await game.add_exp(event)
    if msg:
        await bot.send(event, msg)
    # 获取当前时间戳，如果超过 1分钟，更新用户数据
    global lv_time
    if time.time() - lv_time > 60:
        lv_time = time.time()
        data.save()
        print('保存用户数据')


# 删除用户信息
clearUser = on_command("clear", priority=20, block=True)


@clearUser.handle()
def is_superuser(bot: Bot, event: Event, state: T_State):
    users = data.user
    del users[490272692]
    data.save()
