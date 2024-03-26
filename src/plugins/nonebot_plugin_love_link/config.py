from nonebot import get_driver
from pydantic import Extra, BaseModel


class Config(BaseModel, extra=Extra.ignore):
    """
    配置类
    """
    # 签到基础点数
    daily_sign_base: int = 100

    # 连续签到加成比例
    daily_sign_multiplier: float = 0.2

    # 最大幸运值
    daily_sign_max_lucky: int = 10


# 从 NoneBot 配置中解析出的插件配置
plugin_config = Config.parse_obj(get_driver().config)

# 签到基础点数
BASE = plugin_config.daily_sign_base

# 连续签到加成比例
MULTIPLIER = plugin_config.daily_sign_multiplier

# 最大幸运值
MAX_LUCKY = plugin_config.daily_sign_max_lucky
