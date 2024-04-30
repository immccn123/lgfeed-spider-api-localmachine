"""
数据库配置，敏感文件。
"""

import sys
from peewee import SqliteDatabase, OperationalError
from tools.logger import HandleLog

logger = HandleLog()
logger.info("connecting database......")


def get_connection():
    """获取一个数据库连接。"""
    try:
        # db = SqliteDatabase("feed.db")
        # db = MySQLDatabase(
        #     "u933163999_lgfeed",
        #     host="82.180.152.175",
        #     user="u933163999_imken2",
        #     password="imkenhaomeng!_QwQ0",
        #     charset="utf8mb4",
        #     port=3306,
        # )
        db = PostgresqlDatabase(
            'lgfeed',
            thread_safe=True,
            autorollback=False,
        )
        # db = MySQLDatabase(
        #     "luogu_feed",
        #     host="sh-cynosdbmysql-grp-5hkhuwxc.sql.tencentcdb.com",
        #     user="luogu_feed",
        #     password="Nrnq8fHZx7kWZc",
        #     charset="utf8mb4",
        #     port=28315,
        # )
        db.connect()
    except OperationalError as e:
        db.close()
        logger.critical("Cannot connect to database with these exceptions:")
        print(e)
        logger.critical("Aborted.")
        sys.exit(1)
    logger.info("Connected to database.")
    return db
