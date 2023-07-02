import datetime

from fastapi import APIRouter
from db import get_connection, models
from peewee import fn

db = get_connection()

app = APIRouter()


@app.get("/statistics")
async def get_history_feed():
    """获取统计信息"""

    total = models.Feed.select().count()

    date_before = datetime.datetime.now() + datetime.timedelta(days=-1)
    today = models.Feed.select().where(models.Feed.time >= date_before).count()

    total_user = models.Feed.select(models.Feed.user_id).distinct().count()

    today_user = (
        models.Feed.select(models.Feed.id)
        .group_by(models.Feed.user_id)
        .where(models.Feed.time >= date_before)
        .count()
    )

    return {
        "total": total,
        "today": today,
        "total_user": total_user,
        "today_user": today_user,
    }
