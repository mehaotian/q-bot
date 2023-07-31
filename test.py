import random
import os
from pathlib import Path
try:
    import ujson as json
except ModuleNotFoundError:
    import json

from Player_test import BattleStats, Character, PlayerPK

resourcefile = Path(os.path.join(os.path.dirname(__file__),
                    "src", "plugins", "nonebot_free_world", "./resource"))

with open(resourcefile / "scenes.json", "r", encoding="utf8") as f:
    scenes_library = json.load(f)
with open(resourcefile / "equipments.json", "r", encoding="utf8") as f:
    equipments_library = json.load(f)


class Game_Scene():
    scene = {}

    def __init__(self, scene_name):
        self.scene = scenes_library[scene_name]
        self.round = self.scene["round"]
        # print(self.round)

    def start(self, player1):
        print(f'你进入了{self.scene["name"]}，准备探探究竟！')
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
        self._fight(player1, dungeon_rounds)

    def _fight(self, player, data):
        for row in data:
            # 是遇怪还，是事件
            if "type" in row:
                player2 = self.getPlayerStatus(player=row)
                msg = ''
                if row["type"] == "boss":
                    print(f'BOSS 来袭 ，你遭遇了{row["name"]}，他看起来格外强大，准备战斗！')
                    msg = PlayerPK(player, player2)
                else:
                    print(f'你遭遇了{row["name"]}，准备战斗！')
                    msg = PlayerPK(player, player2)
                    # print(msg)

            else:
                """记算奖励"""
                msg = '，你'
                # 经验
                if "exp" in row['give']:
                    ranges = row['give']['exp']
                    reduce_exp = random.randint(ranges[0], ranges[1])

                    if self._is_negative(reduce_exp):
                        msg += f'失去{abs(reduce_exp)}点经验！'
                    else:
                        msg += f'获得{reduce_exp}点经验！'

                elif 'gold' in row['give']:
                    ranges = row['give']['gold']
                    reduce_gold = random.randint(ranges[0], ranges[1])
                    # msg += f'{reduce_gold}金币！'
                    if self._is_negative(reduce_gold):
                        msg += f'失去{abs(reduce_gold)}金币！'
                    else:
                        msg += f'获得{reduce_gold}金币！'
                elif 'equip' in row['give']:
                    result = []
                    for item_id, item_data in equipments_library.items():
                        if item_data["type"] == "身":
                            item_data["id"] = item_id
                            result.append(item_data)
                    equip = random.choice(result)
                    msg += f'获得 《{equip["name"]}》！'

                elif 'books' in row['give']:
                    msg += f'获得 《牛子变大术》！'
                else:
                    msg = ''

                print(row["message"]+msg)

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

    # 判断是否负数

    def _is_negative(self, num):
        return num < 0


player1_attr = {'STR': 17, 'AGI': 26, 'INT': 22, 'STA': 12, 'ATK': 49, 'DEF': 40, 'AS': 0.5,
                'CRI': 0.1, 'HIT': 0.8, 'DOD': 0.1, 'RES': 4, 'HP': 150, 'MP': 170, 'HPR': 1.5, 'MPR': 1.7}
# player2_attr = {'STR': 56, 'AGI': 30, 'INT': 29, 'STA': 41, 'ATK': 47, 'DEF': 41, 'AS': 0.5, 'CRI': 0.1, 'HIT': 0.8, 'DOD': 0.1, 'RES': 4, 'HP': 150, 'MP': 180, 'HPR': 1.5, 'MPR': 1.8}

player1_attr = Character(strength=player1_attr['STR'], agility=player1_attr['AGI'],
                         intelligence=player1_attr['INT'], stamina=player1_attr['STA'], level=3)
# player1_attr.display_stats()

# 定义 dict 数据
player1 = BattleStats(player=dict(nickname="牛爷爷"), attribute=player1_attr)


scene_handle = Game_Scene("1001")
scene_handle.start(player1)
