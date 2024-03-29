import os
import datetime
import random
import re
from pathlib import Path
try:
    import ujson as json
except ModuleNotFoundError:
    import json

from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    MessageEvent,
    GroupMessageEvent,
    Message,
    MessageSegment
)
from .data import AttrDict, DataBase, PrisonDict, BagData, equipData
from .config import path
from .utils import calculate_experience_required
from .Player import Player, Character, BattleStats, PlayerPK
# 加载数据
datafile = path / "russian_data.json"

if datafile.exists():
    print('存在')
    with open(datafile, "r") as f:
        data = DataBase.loads(f.read())
else:
    print('不存在')
    data = DataBase(file=datafile)

resourcefile = Path(os.path.join(os.path.dirname(__file__), "./resource"))

# 加载探索事件
with open(resourcefile / "game_events.json", "r", encoding="utf8") as f:
    game_event_library = json.load(f)

# 加载探索事件
with open(resourcefile / "events.json", "r", encoding="utf8") as f:
    events_library = json.load(f)


# 加载装备
with open(resourcefile / "equipments.json", "r", encoding="utf8") as f:
    equipments_library = json.load(f)

# 加载副本
with open(resourcefile / "scenes.json", "r", encoding="utf8") as f:
    scenes_library = json.load(f)

# 加载副本奖励
with open(resourcefile / "scene_rewards.json", "r", encoding="utf8") as f:
    scene_rewards_library = json.load(f)

# 加载副本
with open(resourcefile / "scenes.json", "r", encoding="utf8") as f:
    scenes_library = json.load(f)

player = Player(data)


class Game():
    async def run(self, mode, bot: Bot, event: Event):
        """
        开启/关闭世界
        """
        gamedata = data.game

        if mode == "开启":
            if gamedata.is_start:
                await bot.send(event, f"{gamedata.name}正在运行中，无需重复开启！")
                return
            else:
                gamedata.is_start = True

        if mode == "关闭":
            if not gamedata.is_start:
                await bot.send(event, f"{gamedata.name}尚未开启，无需关闭！")
                return
            else:
                gamedata.is_start = False

        data.save()
        await bot.send(event, f"已成功{mode}游戏:{gamedata.name}")
        if gamedata.is_start:
            await bot.send(event, f"世界生成中，请稍后！")
            msg = (
                f'世界已生成，当前世界信息如下：\n'
                f'◆ 世界人数：1 人\n'
                f'◆ 监狱人数：0 人\n'
                f'◆ 发现灵境：35 个\n'
                f'◆ 发现功法秘籍：35 个\n'
                f'◆ 发现神通：20 个'
            )
            await bot.send(event, msg)

    # 判断用户是否可进行游戏
    async def user_check(self, event: Event):
        """
        判断用户是否可进行游戏
        """
        game = data.game  # 获取游戏信息
        users = data.user  # 获取用户信息

        is_start = game.is_start
        user_id = event.user_id

        # is_start = True 并且 user_id 在 users 中返回True
        if is_start and user_id in users:
            prison = users[user_id].prison
            if prison:
                return False
            return True
        else:
            return False
    # 给予或减少用户金币

    async def give_player_gold(self, bot, event: Event, mode):
        """
        给予或减少用户金币
        """
        pattern = r"([+-]?)(\d+)"
        match = re.match(pattern, mode)
        # 提取正负号和数值
        sign = match.group(1)
        value = int(match.group(2))

        at = None
        msg = ''

        message = event.message
        to_user = [msg.data["qq"] for msg in message if msg.type == "at"]
        # 长度大于 0 说明有 at
        if len(to_user) > 0:
            is_send = False
            for qq_no in to_user:
                if qq_no != 'all' and int(qq_no) in data.user:
                    qq_no = int(qq_no)
                    is_send = True
                    # user = data.user[qq_no]
                    at += MessageSegment.at(qq_no)
                    if sign == "+":
                        player.add_gold(qq_no, value)
                    elif sign == "-":
                        gold = player.reduce_gold(qq_no, value)
                        if gold < 0:
                            player.clear_gold(qq_no)
            if is_send:
                if sign == "+":
                    msg = f'{at}\n成功给予以上玩家 {value} 金！'
                elif sign == "-":
                    msg = f'{at}\n成功减少以上玩家 {value} 金！'
                await bot.send(event, message=Message(msg))
            else:
                await bot.send(event, message=Message('请检查是否有误操作，或者用户未加入游戏！'))
        else:
            await bot.send(event, message=Message('请在命令后面加上要操作的用户，如：金币 +100 @xxx'))

    # 给予或减少用户等级
    async def give_player_level(self, bot, event: Event, mode):
        """
        给予或减少用户等级
        """
        pattern = r"([+-]?)(\d+)"
        match = re.match(pattern, mode)
        # 提取正负号和数值
        sign = match.group(1)
        value = int(match.group(2))

        at = None
        msg = ''

        message = event.message
        to_user = [msg.data["qq"] for msg in message if msg.type == "at"]
        # 长度大于 0 说明有 at
        if len(to_user) > 0:
            is_send = False
            for qq_no in to_user:
                if qq_no != 'all' and int(qq_no) in data.user:
                    qq_no = int(qq_no)
                    is_send = True
                    # user = data.user[qq_no]
                    at += MessageSegment.at(qq_no)
                    if sign == "+":
                        player.add_level(qq_no, value)
                    elif sign == "-":
                        lv = player.reduce_level(qq_no, value)
                        if lv < 0:
                            player.clear_level(qq_no)
            if is_send:
                if sign == "+":
                    msg = f'{at}\n成功给予以上玩家 {value} 级！'
                elif sign == "-":
                    msg = f'{at}\n成功减少以上玩家 {value} 级！'
                await bot.send(event, message=Message(msg))
            else:
                await bot.send(event, message=Message('请检查是否有误操作，或者用户未加入游戏！'))
        else:
            await bot.send(event, message=Message('请在命令后面加上要操作的用户，如：等级 +100 @xxx'))

    # 进入监狱

    async def ban_player(self, bot, event: Event, reg):

        message = event.message
        text = message.extract_plain_text()
        parts = re.split(reg, text)
        # 取消空格元素
        parts = [item.strip() for item in parts if item.strip()]
        time = parts[1]
        if len(parts) == 3:
            reason = parts[2]
        else:
            reason = ''

        at = None

        hava_at = None

        # 判断是否为有效用户
        to_user = [msg.data["qq"] for msg in message if msg.type == "at"]
        if len(to_user) > 0:
            is_send = False
            for qq_no in to_user:
                if qq_no != 'all' and int(qq_no) in data.user:
                    qq_no = int(qq_no)
                    is_send = True
                    user = data.user[qq_no]
                    prisons = data.prison
                    if qq_no in prisons:
                        hava_at += MessageSegment.at(qq_no)
                        continue
                    else:
                        at += MessageSegment.at(qq_no)

                    prisonData = {
                        "user_id": qq_no,
                        "prison_time": int(time),
                        "prison_reason": reason or '抓你要什么理由？',
                        "prison_bail": 10 * int(time)
                    }

                    prisons[qq_no] = PrisonDict.parse_obj(prisonData)
                    user.prison = True

            if is_send:
                msg = ''
                if at:
                    msg += f'{at}\n成功将以上用户逮捕，并关进监狱，请大家引以为戒！！'
                if hava_at:
                    msg += f'\n{hava_at}\n以上用户已经在监狱中了，不要重复抓捕！！'

                data.save()
                await bot.send(event, message=Message(msg))
            else:
                await bot.send(event, message=Message('请检查是抓错人拉？看看他加入游戏没呢？'))
        else:
            await bot.send(event, message=Message('请在命令后面加上要操作的用户，如：ban {时间} ?{理由} @xxx'))

    # 玩家物品查询
    async def query_item(self, bot, event: Event, args):
        """
        玩家物品查询
        """
        at = MessageSegment.at(event.user_id)
        text = args.extract_plain_text()
        parts = text.split(' ')
        # 取消空格元素
        parts = [item.strip() for item in parts if item.strip()]
        # 取出第一部分
        try:
            mode = parts[0]
        except:
            mode = ''
        # 取出第二部分
        try:
            item = parts[1]
        except:
            item = ''

        if mode and item:
            if mode == '装备':
                for _, row in equipments_library.items():
                    if item in row["name"]:
                        msg = (
                            f'\n\n查询到如下装备：\n\n'
                            f'◆ 名称：{row["name"]}\n'
                            f'◆ 装备部位：{row["type"]}\n'
                            f'◆ 力量：{row["data"]["STR"]} \n'
                            f'◆ 敏捷：{row["data"]["AGI"]}\n'
                            f'◆ 智力：{row["data"]["INT"]}\n'
                            f'◆ 体力：{row["data"]["STA"] }\n'
                            f'◆ 描述：{row["desc"]}\n'
                        )
                        break
                    else:
                        msg = '没有找到该装备！'
            elif mode == '副本':
                for _, row in scenes_library.items():
                    if item in row["name"]:
                        msg = (
                            f'\n\n查询到如下秘境：\n\n'
                            f'◆ 名称：{row["name"]}\n'
                            f'◆ 描述：{row["desc"]}\n'
                            f'◆ 等级：{row["level"]}\n'
                            f'◆ 难度：{row["difficulty"]}\n'
                            f'◆ 可探索次数：{row["count"]}'
                        )
                        break
                    else:
                        msg = '没有找到该副本！'

        else:
            msg = '请在命令后面加上要操作的用户，如：查询 {物品类型} {物品名称}'

        await bot.send(event, message=Message(at + msg))

    # 用户加入游戏

    async def add(self, event: Event, mode):
        """
        用户加入游戏
        """
        return player.init_user(event.user_id,  mode)

    # 签到

    async def sign_in(self, event: Event):
        users = data.user
        user = users[event.user_id]
        # 上次签到时间
        last_sign_in = user.last_sign_in
        # 连续签到开始时间
        nowtime = datetime.datetime.fromtimestamp(event.time).date()

        if type(last_sign_in) == str:
            if last_sign_in:
                last_sign_in = datetime.datetime.strptime(
                    last_sign_in, "%Y-%m-%d").date()

        # 昨天签到日期
        yesterday = nowtime - datetime.timedelta(days=1)

        if last_sign_in != yesterday:  # 不是连续签到
            # 如果不是昨天的日期 ，并且 最后签到时间小于昨天的日期 ，但肯定是断签了
            if not last_sign_in or last_sign_in < yesterday:
                user.sign_in_time = nowtime
        sign_in_time = user.sign_in_time

        if type(sign_in_time) == str:
            sign_in_time = datetime.datetime.strptime(
                sign_in_time, "%Y-%m-%d").date()

        # 计算日期之间的差值
        delta = nowtime - sign_in_time

        # 获取相差的天数
        diff_days = delta.days
        diff_days += 1

        # 判断 last_sign_in 是否 为今天内的日期
        if last_sign_in == nowtime:
            return f'『{user.nickname}』今天已经签到过了！'
        # 设置签到日期
        user.last_sign_in = nowtime

        gold = user.gold
        # 随机获取 金币 10-100
        add_gold = random.randint(10, 100)
        gold += add_gold
        user.gold = gold
        # 保存用户信息
        data.save()
        if diff_days < 2:
            msg = (
                f'『{user.nickname}』签到成功，获得 {add_gold} 金，当前拥有 {gold} 金！'
            )
        else:
            # 连续签到获取额外金币
            lx_gold = diff_days * 5
            gold += lx_gold
            user.gold = gold
            msg = (
                f'『{user.nickname}』签到成功,获得 {add_gold} 金，连续签到 {diff_days} 天，额外获取 {lx_gold} 金,，当前拥有 {gold} 金！'
            )
        return msg

    # 增加经验

    async def add_exp(self, event: Event):

        users = data.user
        user = users[event.user_id]
        lv = user.level
        exp = user.exp

        # 生级到下一级需要的经验
        exp_required = calculate_experience_required(lv + 1)

        # 随机增加经验 10-100
        add_exp = random.randint(1, 15)
        exp += add_exp

        msg = ''
        # 判断是否升级
        if exp >= exp_required:
            lv += 1
            # 升级
            lv, exp = player.level_up(event.user_id, lv, exp, exp_required)

            msg = (
                f'恭喜『{user.nickname}』升级了，当前等级：{lv}级'
            )
            # 保存用户信息
        # 不需要显示一值提醒经验
        else:
            user.exp = exp
            user.next_exp = calculate_experience_required(lv + 1)
            print(f'恭喜『{user.nickname}』获得经验：{add_exp}，当前经验：{exp}/{exp_required}')
            # msg = (
            #     f'恭喜『{user.nickname}』获得经验：{add_exp}，当前经验：{exp}/{exp_required}'
            # )

        return msg

    # 装备
    async def player_equip(self, event: Event, text):
        user = data.user[event.user_id]
        bags = user.bag
        equips = {}

        # 装备数据
        equi_data = {
            "key": '',
            "data": {}
        }

        # 从装备库找到这件装备
        for index, value in equipments_library.items():
            if value['name'] == text:
                equi_data['key'] = int(index)
                equi_data['data'] = value
        # 背包中是否存在该装备
        if equi_data['key'] in bags:
            key = equi_data['key']
            lib_data = equi_data['data']
            my_equip = user.equip
            try:
                my_equips = my_equip[lib_data['type']]
            except:
                my_equips = {}

            if my_equips and my_equips.name == text:
                return f'已经装备过『{text}』了'
            else:
                equips = {
                    "id": key,
                    'name': lib_data['name'],
                    'type': lib_data['type'],
                    'desc': lib_data['desc'],
                    'data': AttrDict.parse_obj({
                        "STR": lib_data['data']['STR'],
                        "AGI": lib_data['data']['AGI'],
                        "INT": lib_data['data']['INT'],
                        "STA": lib_data['data']['STA'],
                    })
                }

                # 卸下装备
                if my_equips:
                    user.bag[my_equips.id].is_equip = False

                # 装备
                user.bag[key].is_equip = True

                user.equip[lib_data['type']] = equipData.parse_obj(equips)
                # data.save()
                player.update_attr_extra(event.user_id)
                return f'『{equips["name"]}』装备成功！装备部位：{equips["type"]}'

        else:
            return '背包中没有该装备'

    # pk

    async def pk_player(self, event: Event):
        message = event.message

        # 判断是否为有效用户
        to_user = [msg.data["qq"] for msg in message if msg.type == "at"]
        msg = ''
        user_id = None
        is_pk = False
        # 判断是否为有效用户
        if len(to_user) > 0:
            if len(to_user) == 1:
                user_id = int(to_user[0])

                if user_id in data.user:

                    # 开始pk
                    player1_data = data.user[event.user_id]
                    player1_attr = dict(player1_data.attr)
                    player1_attr_extra = dict(player1_data.attr_extra)
                    for key, value in player1_attr_extra.items():
                        player1_attr[key] += value

                    # 处理真实属性
                    player1_attr = Character(strength=player1_attr['STR'], agility=player1_attr['AGI'],
                                             intelligence=player1_attr['INT'], stamina=player1_attr['STA'], level=player1_data.level)
                    player1_attr.display_stats()
                    player1 = BattleStats(
                        player=player1_data, attribute=player1_attr)

                    player2_data = data.user[user_id]
                    player2_attr = dict(player2_data.attr)
                    player2_attr_extra = dict(player2_data.attr_extra)
                    for key, value in dict(player2_attr_extra).items():
                        player2_attr[key] += value

                    # 处理真实属性
                    player2_attr = Character(strength=player2_attr['STR'], agility=player2_attr['AGI'],
                                             intelligence=player2_attr['INT'], stamina=player2_attr['STA'], level=player2_data.level)
                    player2_attr.display_stats()
                    player2 = BattleStats(
                        player=player2_data, attribute=player2_attr)
                    res, status = PlayerPK(player1, player2)

                    for i in res:
                        msg += "\n" + i + "\n"

                    is_pk = True

                else:
                    msg = '用户可能还没加入游戏呢！快让他加入游戏吧！'

            else:
                msg = '一次只能和一个人决斗哦~'
        else:
            msg = 'pk用户不存在，请在命令后面加上要操作的用户，如：pk @xxx'

        return msg, user_id, is_pk

    async def next_scene(self, event: Event, text):
        user = data.user[event.user_id]
        bag = user.bag
        key = None
        scene = None
        for key, value in bag.items():
            if value.type == '副本' and value.name == text:
                key = str(key)
                scene = value

        if scene:
            # 获取副本数据
            attr = user.attr
            # 获取真实伤害
            player_attr = dict(attr)
            player1_attr_extra = dict(user.attr_extra)
            for key, value in player1_attr_extra.items():
                player_attr[key] += value

            player_attr = Character(strength=player_attr['STR'], agility=player_attr['AGI'],
                                    intelligence=player_attr['INT'], stamina=player_attr['STA'], level=user.level)

            # 定义 dict 数据
            player1 = BattleStats(player=user, attribute=player_attr)

            scene_handle = Game_Scene(str(scene.id))
            return scene_handle.start(player1)
        else:
            return '您要探索的秘境不存在，你或许还没有获取它哦~'

# 探索类


class Explore():
    def __init__(self, event):
        self.event = event
        self.user_id = event.user_id

    # 开始探索
    def run(self, text):
        user_id = self.user_id
        user = data.user[user_id]
        msg = ''

        # 收获内容数据
        get_data = {}

        for i in range(text):
            # 计算事件的权重列表
            weights = [evt["chance"] for evt in game_event_library]

            # 随机选择一个事件
            selected_event = random.choices(
                game_event_library, weights=weights, k=1)[0]
            type_name = selected_event["type"]

            event_rows = events_library[type_name]
            res_msg = ''
            # 随机一个内容出来
            event_row = random.choice(event_rows)
            if type_name == 'money_add':  # 金币增加
                get_data.setdefault("金币", 0)
                ranges = event_row["range"]
                add_gold = random.randint(ranges[0], ranges[1])
                get_data["金币"] += add_gold
                res_msg = f'获得金币：{add_gold}'

            elif type_name == 'money_reduce':  # 金币减少
                get_data.setdefault("金币", 0)
                ranges = event_row["range"]
                reduce_gold = random.randint(ranges[0], ranges[1])
                get_data["金币"] -= reduce_gold
                res_msg = f'失去金币：{reduce_gold}'

            elif type_name == 'exp_add':  # 经验增加
                get_data.setdefault("经验", 0)
                ranges = event_row["range"]
                add_exp = random.randint(ranges[0], ranges[1])

                # 当前 总经验
                next_exp = user.next_exp
                # 随机 0.5% - 2% 的经验
                add_exp += int(next_exp * random.uniform(0.005, 0.02))

                get_data["经验"] += add_exp
                res_msg = f'获得经验：{add_exp}'

            elif type_name == 'exp_reduce':  # 经验减少
                get_data.setdefault("经验", 0)
                ranges = event_row["range"]
                reduce_exp = random.randint(ranges[0], ranges[1])
                get_data["经验"] -= reduce_exp
                res_msg = f'失去经验：{reduce_exp}'

            elif type_name == 'prop_add':  # 装备增加
                get_data.setdefault("装备", [])
                # 随机一个装备
                random_equipment_id = random.choice(
                    list(equipments_library.keys()))
                random_equipment = equipments_library[random_equipment_id]

                get_data["装备"].append({
                    "id": random_equipment_id,
                    "name": random_equipment['name']
                })
                res_msg = f'获得装备：{random_equipment["name"]}'

            elif type_name == 'cheat_add':  # 秘籍增加
                get_data.setdefault("秘籍", [])
                get_data["秘籍"].append({
                    "id": i,
                    "name": '一本新秘籍'
                })
                res_msg = f'获得秘籍：一本新秘籍'

            elif type_name == 'encounter':  # 遭遇副本
                get_data.setdefault("副本", [])

                random_scenes_id = random.choice(list(scenes_library.keys()))
                random_scenes = scenes_library[random_scenes_id]

                get_data["副本"].append({
                    "id": random_scenes["id"],
                    "name": random_scenes["name"],

                })
                res_msg = f'获得秘境路引：{random_scenes["name"]}'

            elif type_name == 'nothing':  # 无事发生
                pass
            else:
                pass

            msg += f'{event_row["message"]}'
            if res_msg:
                msg += f'{res_msg}\n\n'
            else:
                msg += f'\n\n'
        msg = msg.rstrip("\n\n")
        # msg += '\n探索结束！结算中...'
        is_up = False

        if "金币" in get_data:
            gold = get_data["金币"]
            if gold > 0:
                player.add_gold(user_id, gold)
            else:
                player.reduce_gold(user_id, abs(gold))

        if "经验" in get_data:
            get_exp = get_data["经验"]
            exp = user.exp
            lv = user.level

            if get_exp > 0:
                # 生级到下一级需要的经验
                exp_required = user.next_exp

                exp += get_exp
                if exp >= exp_required:
                    is_up = True
                    lv += 1
                    # 升级
                    player.level_up(user_id, lv, exp, exp_required)
                else:
                    user.exp = exp

            else:
                get_exp = abs(get_exp)
                # 如果经验不够，则恢复到0
                if get_exp > exp:
                    exp = 0
                    user.exp = exp
                else:
                    # 没有降级
                    exp -= get_exp
                    user.exp = exp
        elif "装备" in get_data:
            get_equipment = get_data["装备"]
            for row in get_equipment:
                key = int(row['id'])

                if key in user.bag:
                    user.bag[key].count += 1
                else:
                    user.bag[key] = BagData.parse_obj({
                        "id": key,
                        "type": "装备",
                        "name": row['name'],
                        "is_equip": False,
                        "count": 1
                    })
        elif "副本" in get_data:
            get_equipment = get_data["副本"]
            for row in get_equipment:
                key = int(row['id'])
                if key in user.bag:
                    user.bag[key].count += 1
                else:
                    user.bag[key] = BagData.parse_obj({
                        "id": key,
                        "type": "副本",
                        "name": row['name'],
                        "count": 1
                    })

        data.save()

        return msg, get_data, is_up


# 副本


class Game_Scene():
    scene = {}

    def __init__(self, scene_name):
        self.scene = scenes_library[scene_name]
        self.round = self.scene["round"]

    def start(self, player1):
        msg = f'你进入了{self.scene["name"]}，准备探探究竟！\n'
        events = self.scene["random_event"]
        round_data = self.scene["round"]

        num_events = random.randint(5, len(events))  # 随机选择5-8个事件

        event_indices = random.sample(
            range(len(events)), num_events)  # 随机选择事件索引
        dungeon_rounds = []
        for i, round_info in enumerate(event_indices):
            dungeon_rounds.append(events[event_indices[i]])

        for i, round_info in enumerate(round_data):
            if i < len(round_data) - 1:
                dungeon_rounds.append(round_info)

        random.shuffle(dungeon_rounds)

        boss_index = len(round_data) - 1
        # 在最后插入剩余的随机事件和Boss
        event = round_data[boss_index]
        dungeon_rounds.append(event)
        mssage, get_data = self._fight(player1, dungeon_rounds)
        msg += mssage
        return msg

    def _fight(self, player, data):

        out_msg = '\n'

        # 奖励
        get_data = {}

        for row in data:
            # 是遇怪还，是事件
            if "type" in row:
                player2 = self.getPlayerStatus(player=row)
                res, status = PlayerPK(player, player2)
                msg = ''
                if row["type"] == "boss":
                    msg += f'BOSS 来袭 ，你遭遇了{row["name"]}，他看起来格外强大，准备战斗！\n'
                    for i in res:
                        msg += "\n" + i + "\n"
                else:
                    msg += f'你遭遇了{row["name"]}，准备战斗！\n'

                    for i in res:
                        msg += "\n" + i + "\n"

                out_msg += msg + '\n'

                # 在战斗中失败，直接结束
                if status == 2:
                    out_msg += f'你被{row["name"]}打败了，探索结束！\n'
                    # 清空 get_data
                    get_data = {}
                    return out_msg, get_data
                elif status == 1:
                    msg = ''
                    reward = self.getReward(row=row)
                    print(reward)
                    # 循环 奖励
                    for key, value in reward.items():
                        if key == "经验":
                            get_data.setdefault("经验", 0)
                            get_data["经验"] += value
                            msg += f'获得{value}点经验！'
                        elif key == "金币":
                            get_data.setdefault("金币", 0)
                            get_data["金币"] += value
                            msg += f'获得{value}金币！'
                        elif key == "装备":
                            get_data.setdefault("装备", [])
                            get_data["装备"].append({
                                "id": value[0]["id"],
                                "name": value[0]["name"]
                            })
                            msg += f'获得 《{value[0]["name"]}》！'

                    out_msg += f'你打败了{row["name"]}，{msg}\n\n'

                    # if "经验" in reward:
                    #     exp = reward["经验"]
                    #     if exp > 0:
                    #         msg += f'获得{exp}点经验！'
                    #     else:
                    #         msg += f'失去{abs(exp)}点经验！'
                    #     get_data.setdefault("经验", 0)
                    #     get_data["经验"] += exp

                    # elif "金币" in reward:
                    #     gold = reward["金币"]
                    #     if gold > 0:
                    #         msg += f'获得{gold}金币！'
                    #     else:
                    #         msg += f'失去{abs(gold)}金币！'

                    #     get_data.setdefault("金币", 0)
                    #     get_data["金币"] += gold

                    # elif "装备" in reward:
                    #     msg += f'获得 《{reward["装备"][0]["name"]}》！'

                    #     get_data.setdefault("装备", [])
                    #     get_data["装备"].append({
                    #         "id": reward["装备"][0]["id"],
                    #         "name": reward["装备"][0]["name"]
                    #     })
                    # else:
                    #     msg = ''

            else:
                """记算奖励"""
                msg = '，你'
                reward = self.getReward(row=row)
                if "经验" in reward:
                    exp = reward["经验"]
                    if exp > 0:
                        msg += f'获得{exp}点经验！'
                    else:
                        msg += f'失去{abs(exp)}点经验！'
                    get_data.setdefault("经验", 0)
                    get_data["经验"] += exp

                elif "金币" in reward:
                    gold = reward["金币"]
                    if gold > 0:
                        msg += f'获得{gold}金币！'
                    else:
                        msg += f'失去{abs(gold)}金币！'

                    get_data.setdefault("金币", 0)
                    get_data["金币"] += gold

                elif "装备" in reward:
                    msg += f'获得 《{reward["装备"][0]["name"]}》！'

                    get_data.setdefault("装备", [])
                    get_data["装备"].append({
                        "id": reward["装备"][0]["id"],
                        "name": reward["装备"][0]["name"]
                    })
                else:
                    msg = ''

                out_msg += row["message"]+msg + '\n\n'
        return out_msg, get_data

    def getPlayerStatus(self, player):
        ranges = player['level']
        level = random.randint(ranges[0], ranges[1])
        attr = player["attr"]
        STR = attr['STR']
        AGI = attr["AGI"]
        INT = attr["INT"]
        STA = attr["STA"]
        char = Character()
        for i in range(level):
            # i_lv = user_lv + i + 1
            # 升级属性
            char.level_up(
                strength=STR, agility=AGI, intelligence=INT, stamina=STA, points=5)
            STR = char.strength
            AGI = char.agility
            INT = char.intelligence
            STA = char.stamina

        return BattleStats(player={"nickname": player["name"]}, attribute=char)

    # 获取奖励
    def getReward(self, row):
        get_data = {}
        # 循环奖励
        for key, value in row["give"].items():
            if key == "exp":
                ranges = value
                reduce_exp = random.randint(ranges[0], ranges[1])

                get_data.setdefault("经验", 0)
                get_data["经验"] += reduce_exp

            elif key == 'gold':
                ranges = value
                reduce_gold = random.randint(ranges[0], ranges[1])

                get_data.setdefault("金币", 0)
                get_data["金币"] += reduce_gold

            elif key == 'equip':
                result = []
                for item_id, item_data in equipments_library.items():
                    if item_data["type"] == "身":
                        item_data["id"] = item_id
                        result.append(item_data)
                equip = random.choice(result)

                get_data.setdefault("装备", [])
                get_data["装备"].append({
                    "id": equip["id"],
                    "name": equip["name"]
                })

            # boss 奖励装备
            elif key == 'boss_equip':
                print('boss奖励装备',value)
                # result = []
                # for item_id, item_data in scene_rewards_library.items():
                #     if item_data["type"] == "身":
                #         item_data["id"] = item_id
                #         result.append(item_data)
                # equip = random.choice(result)

                # get_data.setdefault("装备", [])
                # get_data["装备"].append({
                #     "id": equip["id"],
                #     "name": equip["name"]
                # })

            elif key == 'books':
                # msg += f'获得 《牛子变大术》！'
                pass
                # TODO 缺少秘籍内容，后续补充
            else:
                pass

        return get_data

    # 判断是否负数

    def _is_negative(self, num):
        return num < 0
