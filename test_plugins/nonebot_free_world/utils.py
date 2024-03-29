
# 计算经验值
import random


def calculate_experience_required(level):
    # 每升1级所需的初始经验值
    base_experience = 100

    # 每升1级所需的经验值增长量
    experience_increment = 80

    # 计算总经验值
    experience_required = 0
    for i in range(level):
        experience_required += base_experience + (i * experience_increment)

    return experience_required

# 计算战力


def calculate_power(lv=1, exp=0, equip=0, skill=0, book=0):
    # 基础战力
    base_power = 5

    # 等级加成
    level_bonus = lv * 10

    # 经验加成
    exp_bonus = calculate_total_experience(lv, exp) // 100

    # 装备加成
    equip_bonus = equip * 5

    # 技能加成
    skill_bonus = skill * 3

    # 武功残卷加成
    book_bonus = book * 2

    # 计算总战力
    total_power = base_power + level_bonus + \
        exp_bonus + equip_bonus + skill_bonus + book_bonus

    return total_power

# 获取当前等级的总经验值


def calculate_total_experience(level, current_exp):
    base_experience = 100
    experience_growth_rate = 1.5
    total_experience = 0

    for lv in range(1, level):
        experience_required = int(
            base_experience * (experience_growth_rate ** (lv - 1)))
        total_experience += experience_required

    total_experience += current_exp
    return total_experience


# 获取天赋 

def get_random_talent():
    talents = ['雷', '电', '风', '冰', '金', '木', '水', '火', '土']
    rare_weight = 0.001  # 稀有天赋的权重
    common_weight = (1 - (rare_weight * 4)) / 5  # 常用天赋的权重

    weights = [rare_weight] * 4 + [common_weight] * 5

    random_talent = random.choices(talents, weights, k=1)[0]
    return random_talent


# 获取重复内容
def find_duplicate_names(lst):
    """
    查找列表中相同名称出现的次数，并输出格式化的字符串
    """
    name_counts = {}
    for item in lst:
        name = item["name"]
        if name in name_counts:
            name_counts[name] += 1
        else:
            name_counts[name] = 1
    
    res_msg = ""
    for name, count in name_counts.items():
        res_msg += f'《{name}*{count}》'
    
    return res_msg