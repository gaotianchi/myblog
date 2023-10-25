from markdown import Markdown

from myblog.model.mdexten.customtable import CustomTableExtension

string: str = """
| 名称     | 数据类型     | 备注                                                     |
| -------- | ------------ | -------------------------------------------------------- |
| id       | VARCHAR(30)  | 使用一个功能函数为每个标题生成唯一的ID，这是这个表的主键 |
| title    | VARCHAR(60)  | 文章的标题                                               |
| author   | VARCHAR(30)  | 文章的作者                                               |
| body     | TEXT         | 文章正文                                             |
| table    | TEXT         | 文章的目录                                           |
| path     | VARCHAR(255) | 文章的路径                                           |
| date     | DATE         | 文章的创建日期，储存年月日的值                           |
| update   | DATE         | 文章的更新时间，储存年月日的值                           |
| summary  | TINYTEXT     | 文章的摘要                                           |
| category | VARCHAR(30)  | 文章的分类                                           | 
"""

md = Markdown(extensions=[CustomTableExtension()])
result = md.convert(string)
print(result)
