from pydantic import BaseModel

from random import randint
from datetime import date, timedelta

from tortoise import fields
from tortoise.models import Model

from ..config import BASE, MAX_LUCKY, MULTIPLIER

# 导入插件方法
from nonebot_plugin_tortoise_orm import add_model

#  添加模型
add_model("src.plugins.nonebot_plugin_love_link.models.user_model")


class SignData(BaseModel):
    """
    签到数据
    """

    # 累计金币
    all_gold: int
    # 今日金币
    today_gold: int
    # 累计签到次数
    sign_times: int
    # 连续签到次数
    streak: int


class UserTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 用户 ID
    user_id = fields.IntField()
    # 群组 ID
    group_id = fields.IntField()
    # 金币
    gold = fields.IntField(default=0)
    # 登录时间
    sign_times = fields.IntField(default=0)
    # 最后登录时间
    last_sign = fields.DateField(default=date(2000, 1, 1))
    # 连续登录天数
    streak = fields.IntField(default=0)

    class Meta:
        table = "user_table"
        table_description = " 用户表"  # 可选

    @classmethod
    async def sign_in(
        cls,
        user_id: int,
        group_id: int,
    ) -> SignData:
        """
        :说明: `sign_in`
        > 添加签到记录

        :参数:
          * `user_id: int`: 用户ID
          * `group_id: int`: 群ID

        :返回:
          - `SignData`: 签到数据
        """
        record, _ = await UserTable.get_or_create(
            user_id=user_id,
            group_id=group_id,
        )

        today = date.today()
        if record.last_sign == (today - timedelta(days=1)):
            record.streak += 1

        record.last_sign = today

        gold_base = BASE + randint(-MAX_LUCKY, MAX_LUCKY)
        """基础金币"""

        today_gold = round(gold_base * (1 + record.streak * MULTIPLIER))
        """计算连续签到加成"""

        record.gold += today_gold

        record.sign_times += 1

        await record.save(update_fields=["last_sign", "gold", "sign_times", "streak"])
        return SignData(
            all_gold=record.gold,
            today_gold=today_gold,
            sign_times=record.sign_times,
            streak=record.streak,
        )

    @classmethod
    async def get_last_sign(cls, user_id: int, group_id: int) -> date:
        """
        :说明: `get_last_sign`
        > 获取最近的签到日期

        :参数:
          * `user_id: int`: 用户ID
          * `group_id: int`: 群ID

        :返回:
          - `date`: 签到日期
        """
        record, _ = await UserTable.get_or_create(
            group_id=group_id,
            user_id=user_id,
        )
        return record.last_sign

    @classmethod
    async def get_gold(cls, user_id: int, group_id: int) -> int:
        """
        :说明: `get_gold`
        > 获取金币

        :参数:
          * `user_id: int`: 用户ID
          * `group_id: int`: 群ID

        :返回:
          - `int`: 当前金币数量
        """
        record, _ = await UserTable.get_or_create(
            group_id=group_id,
            user_id=user_id,
        )
        return record.gold

    @classmethod
    async def adjust_gold(cls, adjust: int, user_id: int, group_id: int) -> int:
        """
        :说明: `adjust_gold`
        > 调整金币

        :参数:
          * `adjust: int`: 调整金币数量 为正 则添加 为负 则减少
          * `user_id: int`: 用户ID
          * `group_id: int`: 群ID

        :返回:
          - `int`: 当前金币数量
        """
        record, _ = await UserTable.get_or_create(
            group_id=group_id,
            user_id=user_id,
        )
        record.gold += adjust
        await record.save(update_fields=["gold"])
        return record.gold
