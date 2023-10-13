---
date: 2023-10-12
summary: 这是一篇示例文章，你好世界！
tags:
  - hello
  - world
---

## 这是一个普通的段落

麻匝麻跳旅…路腔种鲢陡[^1]忌膏学摧右露款十他键驴杀后停兵牧临勤煮杉罕意觉溶望脆暴蔓，晒爷革料妄蓟泪症韵懈篡阿嚼崭派晰栖恰涛每沈正盘折卸嘴谁酵曹哗珩强耳示验墓孕定泊幻旁蝼眠彼耀伞念瓦弓。材拖像挂届帽仿阀铭泰寻批盆方哺，腋稠厩今扁畔待慨转糠捉宿失鳄。育团诞蓟灰河识罢避捷融打兴尺败她皆丹糙被连调蓄牵右秒处媳胆为挥伏扬，湾外陨钼苔图十腹人佣恳[^2]卧士饼菜鲜翟察钮形意伙换汹俭？涡偶膀央桥棋锁况镍载挽果昂脸暗熊帅灵执趋锈利派陨哄紧寮


### 这是一个三级标题

腋稠厩今扁畔待慨转糠捉宿失鳄。育团诞蓟灰河识罢避捷融打兴尺败她皆丹糙被连调蓄牵右秒处媳胆为挥伏扬，湾外陨钼苔图十腹人佣恳卧士饼菜鲜翟察钮形意伙换汹俭？涡偶膀央桥棋锁况镍载挽果昂脸暗熊帅灵执趋锈利派陨哄紧寮

### 这是另一个三级标题

腋稠厩今扁畔待慨转糠捉宿失鳄。育团诞蓟灰河识罢避捷融打兴尺败她皆丹糙被连调蓄牵右秒处媳胆为挥伏扬，湾外陨钼苔图十腹人佣恳卧士饼菜鲜翟察钮形意伙换汹俭？涡偶膀央桥棋锁况镍载挽果昂脸暗熊帅灵执趋锈利派陨哄紧寮

## 下面是一个代码块

```python
import os
import shutil

from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    USERDATA_DIR = os.getenv("USERDATA_DIR")
    PROFILE_REQUIRE_ELEMENTS = os.getenv("PROFILE_REQUIRE_ELEMENTS")
    USER_DEFAULT_DIR = os.path.join(basedir, "default")
    LOG_DIR = os.path.join(basedir, "log")
    POSTSPACE = os.path.join(USERDATA_DIR, "文章")

    for path in [LOG_DIR, USERDATA_DIR]:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    for i in os.listdir(USER_DEFAULT_DIR):
        src = os.path.join(USER_DEFAULT_DIR, i)
        shutil.move(src, USERDATA_DIR)


class DevelopmentConfig(BaseConfig):
    SERVER_NAME = os.getenv("DEV_SERVER_NAME", "127.0.0.1:5000")


class ProductionConfig(BaseConfig):
    SERVER_NAME = os.getenv("PROD_SERVER_NAME")


config = {"dev": DevelopmentConfig, "prod": ProductionConfig}

```

## 下面包含一些引言之类的

> 育团诞蓟灰河识罢避捷融打兴尺败她皆丹糙被连调蓄牵右秒处媳胆为挥伏扬，湾外陨钼苔图十腹人佣恳卧士饼菜鲜翟察钮

1. 避捷融打兴尺败她皆丹糙被连调
2. 避捷融打兴尺败她皆丹糙被连调
3. 避捷融打兴尺败她皆丹糙被连调
    - 避捷融打兴尺败她皆丹糙被连调
    - 避捷融打兴尺败她皆丹糙被连调


[^1]: 避捷融打兴尺败她皆丹糙被连调
[^2]: 避捷融打兴尺败她皆丹糙被连调