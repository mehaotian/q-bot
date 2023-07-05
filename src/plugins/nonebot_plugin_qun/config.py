import random
# 进群随机问候语
greetings = [
    "来啦!来了你可就不能走了哦~",
    "欢迎新朋友的加入~",
    "欢迎新人~",
    "这可让你来着了，群里都是妹妹哦~",
    "欢迎欢迎，你是GG和是MM呀？", 
    "欢迎新人，群里的妹妹们都在等你哦~",
    "欢迎新人，群里的哥哥们都在等你哦~",
]

# 匹配词库
def get_wel_word() -> str:
    return random.choice(greetings)