import click
from flask import Flask

from myblog.model.database import db


def register_command(app: Flask) -> None:
    @app.cli.command(help="初始化数据库")
    @click.option("--drop", is_flag=True, help="删除旧的数据库表后再创建新表。")
    def initdb(drop):
        if drop:
            click.confirm("确定要删除所有的表吗？", abort=True)
            db.drop_all()
            click.echo("成功删除所有的数据库表。")
        db.create_all()
        click.echo("完成数据库初始化。")
