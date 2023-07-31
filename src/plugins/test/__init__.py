import random
from datetime import date
from nonebot.plugin import on_keyword , on_command
from nonebot.params import ArgPlainText ,CommandArg
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.typing import T_State
try:
    import ujson as json
except ModuleNotFoundError:
    import json

def luck_simple(num):
    if num < 18:
        return '大吉'
    elif num < 53:
        return '吉'
    elif num < 58:
        return '半吉'
    elif num < 62:
        return '小吉'
    elif num < 65:
        return '末小吉'
    elif num < 71:
        return '末吉'
    else:
        return '凶'


qq = on_keyword(['jrrp', '今日人品'], priority=50)


@qq.handle()
async def jrrp_handle(bot: Bot, event: Event):
    rnd = random.Random()
    rnd.seed(int(date.today().strftime("%y%m%d")) + int(event.get_user_id()))
    lucknum = rnd.randint(1, 100)

    #  [CQ:json,data={"app":"com.tencent.multimsg"&#44;"config":{"autosize":1&#44;"forward":1&#44;"round":1&#44;"type":"normal"&#44;"width":300}&#44;"extra":"{\"tsum\":3}"&#44;"meta":{"detail":{"news":&#91;{"text":"蝲笔小蛄子:傻子才会点进来看"}&#44;{"text":"蝲笔小蛄子:你不会是那个傻子吧"}&#44;{"text":"蝲笔小蛄子:哈哈哈 "}&#93;&#44;"resid":"q4GsES4Q4SMGyePjAD4WzjfbfXyq9Q9uSGIeC4xpsDJq68wmsRSZlbl4WzZaiwGm"&#44;"source":"蝲笔小蛄子的聊天记录"&#44;"summary":"查看3条转发消息"&#44;"uniseq":"f5e5b999-4de3-4c26-85ad-4f87de2385cc"}}&#44;"prompt":"&#91;聊天记录&#93;"&#44;"ver":"0.0.0.5"&#44;"view":"contact"}]

    msg = {
        "app": "com.tencent.multimsg",
        "config": {"autosize": 1, "forward": 1, "round": 1, "type": "normal", "width": 300},
        "desc": "[聊天记录]",
        "extra": {"filename": "2dc8bf80-8658-4a23-8bf6-703932a9b461", "tsum": 16},
        "meta": {
            "detail": {
                "news": [
                    {"text": "白羽: [图片]"},
                    {"text": "白羽: 真好看，嘻嘻"},
                    {"text": "白羽: 快看快看，一会没了"},
                    {"text": "白羽: [文件] 这个萌妹真好看.mp4"}
                ],
                "resid": "q4GsES4Q4SMGyePjAD4WzjfbfXyq9Q9uSGIeC4xpsDJq68wmsRSZlbl4WzZaiwGm",
                "source": "取名字真的很难...的聊天记录",
                "summary": "查看5条转发消息",
                "uniseq": "f5e5b999-4de3-4c26-85ad-4f87de2385cc"
            }
        },
        "prompt": "[聊天记录]",
        "ver": "0.0.0.5",
        "view": "contact"
    }
    msg = MessageSegment.json(data=msg)
    await qq.finish(Message(msg))

# fake_group_chat = on_command(['假群聊'], priority=50)
# @fake_group_chat.handle()
# async def fake_group_chat_handle(bot: Bot, event: Event):


fake_group_chat = on_command("伪造群聊",  aliases={"weather", "查天气"}, priority=99, block=True)

@fake_group_chat.got("msg",  prompt="请将需要伪造的群聊消息发送给我")
async def _(state: T_State, msg: Event):
    msgdata = msg.get_message()

    # print(state)
    # 输入转发消息
    if 'relay_message' not in state:
        try_count = state.get("try_count", 1)
        if "json" in msgdata:
            for segment in msgdata["json"]:
                data  = segment.data["data"]
                json_data = json.loads(data)
                if "meta" in json_data:
                    state["relay_message"] = json_data
                    msg = (
                        f'请复制下方内容，按文字提示修改后发送给我\n'
                        f'发送格式：\n'
                        +'{\n'
                        +'\t"名称":"这里填写来自哪里",\n'
                        +'\t"内容":[\n'
                        +'\t\t{"text": "这里是内容1"},\n'
                        +'\t\t{"text": "这里是内容2"},\n'
                        +'\t\t{"text": "这里是内容3"}\n'
                        +'\t],\n'
                        +'\t"尾部提示":"如：查看5条转发消息 ，默认就是这个"\n'
                        +'}'
                    )
                    await fake_group_chat.reject(msg)
                else:
                    state["try_count"] = try_count + 1
                    if try_count > 3:
                        await fake_group_chat.finish("错误次数过多，已取消")

                    await fake_group_chat.reject("请转发正确的消息，转发消息应该为合并转发的消息")
        else:
            state["try_count"] = try_count + 1
            if try_count > 3:
                await fake_group_chat.finish("错误次数过多，已取消")
            await fake_group_chat.reject("请转发正确的消息，转发消息应该为合并转发的消息")
    else: # 输入处理消息
        user_msg = msg.get_plaintext()
        relay_message = state["relay_message"]
        send_count =  state.get("send_count", 1)
        try:
            user_msg = user_msg.replace("\n", "").replace("\t", "")
            print(user_msg)
            user_msg = json.loads(user_msg)
        except Exception as e:
            print(e)
            state["send_count"] = send_count + 1
            if send_count > 3:
                await fake_group_chat.finish("错误次数过多，已取消")

            await fake_group_chat.reject("输入错误，请按照提示输入")

        name = user_msg["名称"]
        news = user_msg["内容"]
        source = user_msg["尾部提示"] 
        if not source:
            source = "查看5条转发消息"
        relay_message["meta"]["detail"]["source"] = name + "的聊天记录"
        relay_message["meta"]["detail"]["news"] = news
        relay_message["meta"]["detail"]["summary"] = source
        
        # print('-=-==--=',user_msg)
        print(relay_message)
        share_text = MessageSegment.json(data=relay_message)

        await fake_group_chat.finish(Message(share_text))

