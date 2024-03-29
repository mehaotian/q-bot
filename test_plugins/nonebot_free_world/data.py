from pathlib import Path
from pydantic import BaseModel, ValidationError
from typing import Dict,List
try:
    import ujson as json
except ModuleNotFoundError:
    import json


class TalentData(BaseModel):
    """
    玩家天赋
    """
    pass


class BookData(BaseModel):
    """
    玩家功法秘籍
    """
    pass


class BagData(BaseModel):
    """
    玩家背包
    """
    id: int = 0
    type: str = ''
    name: str = ''
    desc: str = ''
    # 是否装备
    is_equip: bool = False
    count: int = 0


class AttrDict(BaseModel):
    """
    玩家属性
    """
    # strength=10, agility=5, intelligence=5, stamina
    # 力量
    STR: int = 0
    # 敏捷
    AGI: int = 0
    # 智力
    INT: int = 0
    # 体力
    STA: int = 0
    # 攻击力
    ATK: int = 0
    # 防御力
    DEF: int = 0
    # 攻击速度
    AS: float = 0
    # 暴击率
    CRI: float = 0
    # 命中率
    HIT: float = 0
    # 闪避率
    DOD: float = 0
    # 抗性
    RES: int = 0
    # 生命上限
    HP: int = 0
    # 魔法上限
    MP: int = 0
    # 生命恢复速度
    HPR: float = 0
    # 魔法恢复速度
    MPR: float = 0

# class UserDict(BaseModel):
#     attr: AttrDict = {}

class equipData(BaseModel):
    """
    装备
    """
    # 装备id
    id: int = 0
    # 装备类型
    type: str = ''
    # 装备名称
    name: str = ''
    # 装备描述
    desc: str = ''
    # 装备属性
    data: AttrDict = {}

class UserDict(BaseModel):
    """
    用户字典
    """
    # 玩家 qq 号
    user_id: int = None
    # 玩家昵称
    nickname: str = None
    # 玩家状态  1 正常 2 禁闭
    status: str = "正常"
    # 玩家等级
    level: int = 1
    # 下级需要经验
    next_exp: int = 100
    # 玩家经验
    exp: int = 0
    # 装备
    equip: Dict[str, equipData] = {}
    # 玩家金币
    gold: int = 0
    # 最后签到时间
    last_sign_in: str = ""
    # 连续签到初始时间
    sign_in_time: str = ""
    # 玩家天赋
    talent: Dict[int, TalentData] = {}
    # 玩家功法秘籍
    books: Dict[int, BookData] = {}
    # 属性 ,力量 敏捷 智力 ... hp mp 攻击力 防御力
    attr: AttrDict = {}
    # 额外属性加成
    attr_extra: AttrDict = {}
    # 玩家背包
    bag: Dict[int, BagData] = {}
    # 战力
    power: int = 5
    # 是否禁闭
    prison: bool = False
    # 禁闭时间 ，0 为永久禁闭，需要缴纳保释金或管理解禁
    prison_time: int = 0
    # 禁闭原因
    prison_reason: str = ""
    # 保释金
    prison_bail: int = 0
    # 行动步数
    step: int = 5

    def __init__(self, event=None, **obj):
        """
        初始化用户字典
        """
        super().__init__(**obj)
        # if event:
        #     self.user_id = event.user_id
        #     self.nickname = event.sender.nickname


class UserData(Dict[int, UserDict]):
    """
    用户数据
    """


class GroupDict(BaseModel):
    """
    群字典
    """
    group_id: int = None


class GroupData(Dict[int, GroupDict]):
    """
    群数据
    """
    pass


class GameData(BaseModel):
    """ 
    游戏数据
    """
    # 名称
    name: str = '自由世界'
    # 版本
    version: str = '1.0.0'
    # 开始时间
    start_time: float = 8
    # 结束时间
    end_time: float = 22
    # 是否开启
    is_start: bool = False


class PrisonDict (BaseModel):
    """
    监狱字典
    """
    # 玩家 qq 号
    user_id: int = None
    # 禁闭时间 ，0 为永久禁闭，需要缴纳保释金或管理解禁
    prison_time: int = 0
    # 禁闭原因
    prison_reason: str = ""
    # 保释金
    prison_bail: int = 0

# 监狱


class PrisonData(Dict[int, PrisonDict]):
    """
    监狱数据
    """
    pass

# 组队信息
class TeamDict(BaseModel):
    """
    组队字典
    """
    # 组队人数
    team_num: int = 0
    # 组队时间
    team_time: str = ""
    # 组队副本
    team_game: str = ""
    # 组队人员 ,数组
    team_user_id: list = []
    # 组队状态
    team_status: str = "正常"
    # 组队平均战力
    team_power: int = 0
    # 组队队长
    team_leader: int = 0
    

# 组队
class TeamData(Dict[int, TeamDict]):
    """
    组队数据
    """
    pass
    

class DataBase(BaseModel):
    user: UserData = UserData()
    # group:GroupData = GroupData()
    game: GameData = GameData()
    prison: PrisonData = PrisonData()
    team: TeamData = TeamData()
    file: Path

    def save(self):
        """ 
        保存数据
        """
        # print(self.json(indent = 4))
        # print(self.file)
        with open(self.file, "w") as f:
            f.write(self.json(indent=4))

    @classmethod
    def loads(cls, data: str):
        """
        从json字符串中加载数据
        """
        data_dict = json.loads(data)
        Truedata = cls(file=Path(data_dict["file"]))
        for user_id, user in data_dict["user"].items():
            for talent_id, talent in user["talent"].items():
                user["talent"][talent_id] = TalentData.parse_obj(talent)

            for book_id, book in user["books"].items():
                user["books"][book_id] = BookData.parse_obj(book)

            for bag_id, bag in user["bag"].items():
                user["bag"][bag_id] = BagData.parse_obj(bag)
            
            for equip_id, equip in user["equip"].items():
                # for attr_id, attr in equip["data"].items():
                #     if attr:
                #         equip["data"][attr_id] = AttrDict.parse_obj(attr) 
                user["equip"][equip_id] = equipData.parse_obj(equip)
            
            user["attr"] = AttrDict.parse_obj(user["attr"])
            user["attr_extra"] = AttrDict.parse_obj(user["attr_extra"])
            Truedata.user[int(user_id)] = UserDict.parse_obj(user)

        for user_id, prison in data_dict["prison"].items():
            Truedata.prison[int(user_id)] = PrisonDict.parse_obj(prison)

        # 以下代码是重新构建数据结构，否则获取的是默认值
        Truedata.game = GameData.parse_obj(data_dict["game"])
        # print(Truedata)

        return Truedata
