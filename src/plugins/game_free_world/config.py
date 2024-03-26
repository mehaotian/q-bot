from pathlib import Path
from pydantic import BaseModel, Extra



class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
current_directory =  Path(__file__).resolve().parent
# 默认数据存数路径
path = Path() / "data" / "russian"

text_bg_path = current_directory / "resource" / "imgs"
path.mkdir(exist_ok = True, parents = True)