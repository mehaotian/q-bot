import nonebot
from nonebot import Driver

from .service.game_handler import load_world_data

from .psql_db import db_context


# # 加载数据库
# driver: Driver = nonebot.get_driver()

# # 开启 nonebot 时开启数据库
# driver.on_startup(db_context.init)
# # 关闭 nonebot 时关闭数据库
# driver.on_shutdown(db_context.disconnect)

# """加载世界资源"""
# @driver.on_startup
# async def events_read():
#     await load_world_data()


