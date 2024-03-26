import tarfile

from nonebot import logger
import os



class Map:
    name = '未定义地图'  # 地图名称
    enemy_list = []  # 地图拥有的敌人和概率
    item_list = []  # 地图拥有的道具
    owned_map = []  # 子地图
    require_level = 1  # 地图需要的探索等级
    require_honor = {}  # 地图需要的特别称号
    require_buff = {}  # 地图需要的特别buff
    require_item = {}  # 地图需要的特别物品
    cost = {}  # 地图的消耗
    public = True  # 是否直接可达
    description = "无"

    def get_max_enemy_level(self):
        return max(self.enemy_list, key=lambda l: l["lv"])["lv"]



class Help:
    type: str  # 种类 目前有图片型 消息型2种
    question: str  # 问题
    ans = ""  # 回答 str or list[str]
    name: str  # 消息名称
    pos: int  # 帮助在栏目中的位置


class WorldInfo:
    mapList: dict[str, Map]
    helpList: dict[int, Help]

    def get_help_question(self) -> list[str]:
        return [f"{q.pos}. {q.question}" for q in self.helpList.values()]

    def get_help_answer(self, pos):
        return self.helpList.get(pos)


world_data: WorldInfo


def get_world_data() -> WorldInfo:
    return world_data


# 将src_dir中的所有文件提取到des_dir
def extract_tar_files(src_dir, des_dir):
    files = os.listdir(src_dir)
    for file in files:
        dir_tmp = os.path.join(src_dir, file)
        if not os.path.isdir(dir_tmp):  ##是文件，非文件夹
            # 解压特定文件
            if dir_tmp.endswith("gamedata"):
                # f = zipfile.ZipFile(dir_tmp, mode="r")
                f = tarfile.open(dir_tmp)
                names = f.getnames()
                for name in names:
                    f.extract(name, path=des_dir)
                return
        else:
            extract_tar_files(dir_tmp, des_dir)
    return 0


async def load_world_data() -> None:
    global world_data
    world_data = WorldInfo()
    logger.info(f'【只因进化录】资源载入中')
    path = os.path.dirname(__file__) + '/../gamedata/json/'
    path2 = os.path.dirname(__file__) + '/../gamedata/'
    files = os.listdir(path)
    extract_tar_files(path2, path)
    

    