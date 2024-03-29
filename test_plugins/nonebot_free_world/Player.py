
import copy
import random
from .data import AttrDict, UserDict
from .utils import calculate_experience_required

base_attr = {
    "STR": 0,
    "AGI": 0,
    "INT": 0,
    "STA": 0,
    "ATK": 0,
    "DEF": 0,
    "AS": 0,
    "CRI": 0,
    "HIT": 0,
    "DOD": 0,
    "RES": 0,
    "HP": 0,
    "MP": 0,
    "HPR": 0,
    "MPR": 0
}


class Player():
    def __init__(self, data):
        self.data = data
        self.user = data.user
        self.game = data.game
        self.prison = data.prison

    # 初始化用户
    def init_user(self, user_id, nickname):
        playerCharacrer = Character()
        user_attr = self.calculate_stats(playerCharacrer)
        attr = AttrDict.parse_obj(user_attr)

        userData = {
            "user_id": user_id,
            "nickname": nickname,
            "status": "正常",
            "level": 1,
            "exp": 0,
            "gold": 0,
            "equip": {},
            "talent": {},
            "attr": attr,
            "attr_extra": AttrDict.parse_obj(base_attr),
            "books": {},
            "bag": {},
            "prison": False,
            "prison_time": 0,
            "prison_reason": "",
            "prison_bail": 0
        }

        self.user[user_id] = UserDict.parse_obj(userData)
        self.data.save()
        return self.user[user_id]

    # 玩家增加金币
    def add_gold(self, user_id, gold):
        self.user[user_id].gold += gold
        self.data.save()
        return self.user[user_id].gold

    # 玩家减少金币
    def reduce_gold(self, user_id, gold):
        self.user[user_id].gold -= gold
        self.data.save()
        return self.user[user_id].gold

    # 清空玩家金币
    def clear_gold(self, user_id):
        self.user[user_id].gold = 0
        self.data.save()
        return 0

    # 玩家等级增加
    def add_level(self, user_id, value):
        # 当前等级
        lv = self.user[user_id].level

        # 生级到下一级需要的经验
        exp_required = calculate_experience_required(lv+value)
        self.level_up(user_id, lv+value, exp_required+1, exp_required)
        return lv+value
    # 玩家等级减少

    def reduce_level(self, user_id, value):
        # self.user[user_id].level -= lv
        # self.data.save()
        # return self.user[user_id].level
        # 当前等级
        lv = self.user[user_id].level
        # 生级到下一级需要的经验
        exp_required = calculate_experience_required(lv - value)
        self.level_down(user_id, lv-value, exp_required+1, exp_required)
        return lv-value

    # 清空玩家等级
    def clear_level(self, user_id):
        self.user[user_id].level = 0
        self.data.save()
        return 0

    # 玩家升级
    def level_up(self, user_id, lv, exp, exp_required):
        user = self.user[user_id]
        attr = user.attr
        user_lv = user.level

        diff = lv - user_lv

        STR = attr.STR
        AGI = attr.AGI
        INT = attr.INT
        STA = attr.STA
        playerCharacrer = Character()
        for i in range(diff):
            # i_lv = user_lv + i + 1
            # 升级属性
            playerCharacrer.level_up(
                strength=STR, agility=AGI, intelligence=INT, stamina=STA)
            STR = playerCharacrer.strength
            AGI = playerCharacrer.agility
            INT = playerCharacrer.intelligence
            STA = playerCharacrer.stamina

        user_attr = self.calculate_stats(playerCharacrer)
        attr = AttrDict.parse_obj(user_attr)
        user.attr = attr

        exp = exp - exp_required
        self.user[user_id].level = lv
        user.next_exp = calculate_experience_required(lv + 1)
        user.exp = exp
        if exp >= user.next_exp:
            lv, exp = self.level_up(user_id, lv+1, exp, user.next_exp)
        # 保存数据
        self.data.save()
        return lv, exp

    # 等级降级
    def level_down(self, user_id, lv, exp, exp_required):
        user = self.user[user_id]
        attr = user.attr
        user_lv = 0

        playerCharacrer = Character()

        STR = playerCharacrer.strength
        AGI = playerCharacrer.agility
        INT = playerCharacrer.intelligence
        STA = playerCharacrer.stamina

        for i in range(lv):
            # i_lv = user_lv + i + 1
            # 升级属性
            playerCharacrer.level_up(
                strength=STR, agility=AGI, intelligence=INT, stamina=STA)
            STR = playerCharacrer.strength
            AGI = playerCharacrer.agility
            INT = playerCharacrer.intelligence
            STA = playerCharacrer.stamina

        user_attr = self.calculate_stats(playerCharacrer)
        attr = AttrDict.parse_obj(user_attr)
        user.attr = attr

        exp = exp - exp_required
        self.user[user_id].level = lv
        user.exp = exp
        user.next_exp = calculate_experience_required(lv + 1)
        # 保存数据
        self.data.save()
        return lv, exp

    # 玩家额外属性
    def update_attr_extra(self, user_id):
        user = self.user[user_id]
        # 获取当前背包属性
        bag = user.equip

        # 装备属性列表
        equip_list = []
        equip_data = copy.copy(base_attr)

        for _, value in bag.items():
            equip_list.append(value)

        for row in equip_list:
            # 获取装备属性
            for key, value in dict(row.data).items():
                equip_data[key] += value
        user.attr_extra = AttrDict.parse_obj(equip_data)
        self.data.save()

    # pk 玩家
    def pk(self, user_id):
        pass

    # 计算 玩家 攻击力 MP HP
    def calculate_stats(self, playerAttr):
        return {
            "STR": playerAttr.strength,
            "AGI": playerAttr.agility,
            "INT": playerAttr.intelligence,
            "STA": playerAttr.stamina,
            "ATK": playerAttr.attack,
            "DEF": playerAttr.defense,
            "AS": playerAttr.attack_speed,
            "CRI": playerAttr.critical_chance,
            "HIT": playerAttr.hit_chance,
            "DOD": playerAttr.dodge_chance,
            "RES": playerAttr.resistance,
            "HP": playerAttr.max_health,
            "MP": playerAttr.max_mana,
            "HPR": playerAttr.health_regeneration,
            "MPR": playerAttr.mana_regeneration,
        }


class Character():
    def __init__(self, strength=10, agility=5, intelligence=5, stamina=3, level=1):
        self.strength = strength  # 力量
        self.agility = agility  # 敏捷
        self.intelligence = intelligence  # 智力
        self.stamina = stamina  # 体力
        self.level = level  # 默认等级
        self.init()

    def init(self):
        self.attack = self.calculate_attack()  # 攻击力
        self.defense = self.calculate_defense()  # 防御力
        self.attack_speed = self.calculate_attack_speed()  # 攻击速度
        self.critical_chance = self.calculate_critical_chance()  # 暴击率
        self.hit_chance = self.calculate_hit_chance()  # 命中率
        self.dodge_chance = self.calculate_dodge_chance()  # 闪避率
        self.resistance = self.calculate_resistance()  # 抗性
        self.max_health = self.calculate_max_health()  # 生命上限
        self.max_mana = self.calculate_max_mana()  # 魔法上限
        self.health_regeneration = self.calculate_health_regeneration()  # 生命恢复速度
        self.mana_regeneration = self.calculate_mana_regeneration()  # 魔法恢复速度

    def level_up(self, strength=10, agility=5, intelligence=5, stamina=3, points=10):
        """
        角色升级，增加属性
        """
        self.level += 1
        self.strength = strength
        self.agility = agility
        self.intelligence = intelligence
        self.stamina = stamina

        attributes = ['strength', 'agility', 'intelligence', 'stamina']
        for _ in range(points):
            attribute = random.choice(attributes)
            setattr(self, attribute, getattr(self, attribute) + 1)

        # 重新计算其他隐藏属性
        self.init()

    def calculate_growth(self, attribute):
        """
        计算属性的增长值
        """
        base_growth = 3  # 基础属性增长值
        scaling_factor = 0.2  # 每级属性增长的系数
        return int(base_growth + attribute * scaling_factor)

    def calculate_attack(self):
        """
        计算攻击力
        """
        base_attack = self.strength * 2 + self.agility + self.intelligence // 2
        attack_per_level = 5
        return base_attack + self.level * attack_per_level

    def calculate_defense(self):
        """
        计算防御力
        """
        base_defense = self.strength + self.agility * 2 + self.intelligence
        defense_per_level = 3
        return base_defense + self.level * defense_per_level

    def calculate_attack_speed(self):
        """
        计算攻击速度
        """
        # 0.5+ 100*0.01 = 1.5
        base_attack_speed = 0.5  # 基础攻击速度（例如每秒0.5次攻击）
        agility_scaling = 0.001  # 每点敏捷增加的攻击速度
        return round(base_attack_speed + self.agility * agility_scaling, 1)

    def calculate_critical_chance(self):
        """
        计算暴击率
        """
        base_critical_chance = 0.05  # 基础暴击率（例如5%）
        agility_scaling = 0.001  # 每点敏捷增加的暴击率
        return round(base_critical_chance + self.agility * agility_scaling, 1)

    def calculate_hit_chance(self):
        """
        计算命中率
        """
        base_hit_chance = 0.8  # 基础命中率（例如80%）
        agility_scaling = 0.001  # 每点敏捷增加的命中率
        return round(base_hit_chance + self.agility * agility_scaling, 1)

    def calculate_dodge_chance(self):
        """
        计算闪避率
        """
        base_dodge_chance = 0.1  # 基础闪避率（例如10%）
        agility_scaling = 0.001  # 每点敏捷增加的闪避率
        return round(base_dodge_chance + self.agility * agility_scaling, 1)

    def calculate_resistance(self):
        """
        计算抗性
        """
        base_resistance = self.stamina // 2
        resistance_per_level = 1
        return base_resistance + self.level * resistance_per_level

    def calculate_max_health(self):
        """
        计算生命上限
        """
        base_health = 100  # 基础生命值
        health_per_stamina = 10  # 每点体力增加的生命值
        return base_health + self.stamina * health_per_stamina

    def calculate_max_mana(self):
        """
        计算魔法上限
        """
        base_mana = 100  # 基础魔法值
        mana_per_intelligence = 10  # 每点智力增加的魔法值
        return base_mana + self.intelligence * mana_per_intelligence

    def calculate_health_regeneration(self):
        """
        计算生命恢复速度
        """
        base_regeneration = 1  # 基础每秒生命恢复值
        stamina_scaling = 0.1  # 每点体力增加的生命恢复速度
        return round(base_regeneration + self.stamina * stamina_scaling, 1)

    def calculate_mana_regeneration(self):
        """
        计算魔法恢复速度
        """
        base_regeneration = 1  # 基础每秒魔法恢复值
        intelligence_scaling = 0.1  # 每点智力增加的魔法恢复速度
        return round(base_regeneration + self.intelligence * intelligence_scaling, 1)

    def display_stats(self):
        """
        显示角色属性
        """
        print("===== 角色属性 =====")
        print("力量:", self.strength)
        print("敏捷:", self.agility)
        print("智力:", self.intelligence)
        print("体力:", self.stamina)
        print("等级:", self.level)
        print("攻击力:", self.attack)
        print("防御力:", self.defense)
        print("攻击速度:", self.attack_speed)
        print("暴击率:", self.critical_chance)
        print("命中率:", self.hit_chance)
        print("闪避率:", self.dodge_chance)
        print("抗性:", self.resistance)
        print("生命上限:", self.max_health)
        print("魔法上限:", self.max_mana)
        print("生命恢复速度:", self.health_regeneration)
        print("魔法恢复速度:", self.mana_regeneration)
        print("==================")


class BattleStats:
    def __init__(self, player={}, attribute={
        "attack": 100,
        "defense": 100,
        "attack_speed": 1.0,
        "critical_chance": 0.1,
        "hit_chance": 0.8,
        "dodge_chance": 0.1,
        "resistance": 0,
        "max_health": 1000,
        "max_mana": 500,
        "health_regeneration": 10,
        "mana_regeneration": 5
    }):
        self.player = player
        self.attack = attribute.attack  # 攻击力
        self.defense = attribute.defense  # 防御力
        self.attack_speed = attribute.attack_speed  # 攻击速度
        self.critical_chance = attribute.critical_chance  # 暴击率
        self.hit_chance = attribute.hit_chance  # 命中率
        self.dodge_chance = attribute.dodge_chance  # 闪避率
        self.resistance = attribute.resistance  # 抗性
        self.max_health = attribute.max_health  # 生命上限
        self.max_mana = attribute.max_mana  # 魔法上限

        self.health = attribute.max_health  # 当前生命值
        self.mana = attribute.max_mana  # 当前魔法值

        self.health_regeneration = attribute.health_regeneration  # 生命恢复速度
        self.mana_regeneration = attribute.mana_regeneration  # 魔法恢复速度

    def attack_damage(self):
        """
        计算角色的攻击伤害值
        """
        base_damage = self.attack * self.attack_speed
        # 是否暴击
        is_critical = False
        if random.random() < self.critical_chance:
            base_damage *= 2  # 暴击时伤害加倍
            is_critical = True
        return int(base_damage), is_critical

    def defend(self, damage):
        """
        根据防御力和抗性减少受到的伤害值
        """
        # 伤害 / 防御力 = 防御因子
        defense_factor = damage / self.defense  # 防御因子,即减少的伤害百分比
        reduced_damage = int(damage * defense_factor)
        return max(reduced_damage, 0)  # 确保伤害值不会为负数

    def is_hit(self):
        """
        判断角色是否被命中
        """
        return random.random() < self.hit_chance

    def is_dodge(self):
        """
        判断角色是否闪避攻击
        """
        return random.random() < self.dodge_chance

    def is_hit_or_dodge(self, dogge):
        effective_chance = self.hit_chance - dogge
        return random.random() < effective_chance

    def take_damage(self, damage):
        """
        承受伤害并减少生命值
        """
        self.max_health -= damage
        if self.max_health < 0:
            self.max_health = 0

    def regenerate_health(self):
        """
        恢复生命值
        """
        if self.max_health <= 0:
            return  # 死亡时无法恢复生命值
        self.max_health += self.health_regeneration
        self.max_health = int(self.max_health)
        if self.max_health > self.health:
            self.max_health = self.health
        return self.health_regeneration

    def regenerate_mana(self):
        """
        恢复魔法值
        """
        if self.max_mana <= 0:
            return  # 死亡时无法恢复魔法值
        self.max_mana += self.mana_regeneration
        self.max_mana = int(self.max_mana)
        if self.max_mana > self.mana:
            self.max_mana = self.mana

    def is_alive(self):
        """
        判断角色是否存活
        """
        return self.max_health > 0


def PlayerPK(character1, character2):
    player1 = character1.player
    player2 = character2.player
    try:
        nickname1 = player1.nickname
    except:
        nickname1 = player1['nickname']

    try:
        nickname2 = player2.nickname
    except:
        nickname2 = player2['nickname']

    msg_list = []
    # msg_list = [f"『{player1.nickname}』与『{player2.nickname}』战斗正式拉开了序幕。"]
    # print("===== 战斗开始 =====")
    # msg_list += [f"============================== 战斗开始 =============================="]
    # msg_list.append(f"『{nickname1}』: 生命值 {character1.max_health}, 魔法值 {character1.max_mana}")
    # msg_list.append(f"『{nickname2}』: 生命值 {character2.max_health}, 魔法值 {character2.max_mana}")
    # msg_list += [f"====================================================================="]

    round_num = 1
    while character1.is_alive() and character2.is_alive() and round_num <= 50:
        # print(f"===== 第 {round_num} 回合 =====")
        # msg_list += [f"======================== 第 {round_num} 回合 ====================="]
        # 如果角色1 存活才能攻击
        if character1.is_alive():
            player1_msg = f'『{nickname1}』发动了攻击'
            if character1.is_hit() and not character2.is_dodge():
                damage, is_critical = character1.attack_damage()
                damage = character2.defend(damage)
                character2.take_damage(damage)
                if is_critical:
                    player1_msg += f"，对『{nickname2}』造成了{damage}点暴击伤害，『{nickname2}』剩余生命值 {character2.max_health}"
                    print(player1_msg)
                    msg_list.append(player1_msg)
                else:
                    player1_msg += f"，对『{nickname2}』造成了{damage}点伤害，『{nickname2}』剩余生命值 {character2.max_health}"
                    print(player1_msg)
                    msg_list.append(player1_msg)

            elif character2.is_dodge():
                player1_msg + f"，但是『{nickname2}』闪避了攻击"
                print(player1_msg)
                msg_list.append(player1_msg)
            else:
                player1_msg += f"，但是很可惜未命中『{nickname2}』"
                print(player1_msg)
                msg_list.append(player1_msg)

        # 如果玩家2 存活，才能继续攻击
        if character2.is_alive():
            player2_msg = f'『{nickname2}』发动了攻击'
            # character2攻击character1
            if character2.is_hit() and not character1.is_dodge():
                damage, is_critical = character2.attack_damage()
                damage = character1.defend(damage)
                character1.take_damage(damage)
                if is_critical:
                    player2_msg += f"，对『{nickname1}』造成了{damage}点暴击伤害，『{nickname1}』剩余生命值{character1.max_health}"
                    print(player2_msg)
                    msg_list.append(player2_msg)
                else:
                    player2_msg += f"，对『{nickname1}』造成了{damage}点伤害，『{nickname1}』剩余生命值{character1.max_health}"
                    print(player2_msg)
                    msg_list.append(player2_msg)
            elif character1.is_dodge():
                player2_msg += f"，但是『{nickname1}』闪避了攻击"
                print(player2_msg)
                msg_list.append(player2_msg)
            else:
                player2_msg += f"，但是很可惜未命中『{nickname1}』"
                print(player2_msg)
                msg_list.append(player2_msg)

        # 角色恢复生命和魔法
        character1.regenerate_health()
        character1.regenerate_mana()
        character2.regenerate_health()
        character2.regenerate_mana()

        # msg_list += [f"=============== 回合结束 ==============="]

        round_num += 1
    if round_num > 50:
        msg_list.append(f"=============== 战斗结束 ===============")
        print("双方实力相当，战斗超过50回合，平局")
        msg_list.append("双方实力相当，战斗超过50回合，平局")
        return msg_list ,0

    print("===== 战斗结束 =====")
    if character1.is_alive():
        # msg_list.append(f"=============== 战斗结束 ===============")
        
        print(f"『{nickname1}』获得了最终的胜利")
        msg_list.append(f"『{nickname1}』获得了最终的胜利")
        return msg_list, 1
    else:
        # msg_list.append(f"=============== 战斗结束 ===============")
        print(f"『{nickname2}』获得了最终的胜利")
        msg_list.append(f"『{nickname2}』获得了最终的胜利")
        return msg_list, 2
