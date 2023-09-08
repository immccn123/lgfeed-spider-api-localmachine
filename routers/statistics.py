import datetime

from fastapi import APIRouter, Query
from db import get_connection, models
from peewee import fn

from typing_extensions import Annotated

db = get_connection()

app = APIRouter()


@app.get("/statistics")
async def get_statistics():
    """获取统计信息"""

    total = models.Feed.select().count()

    date_before = datetime.datetime.now() + datetime.timedelta(days=-1)
    today = models.Feed.select().where(models.Feed.time >= date_before).count()

    total_user = models.Feed.select(models.Feed.user_id).distinct().count()
    today_user = (
        models.Feed.select(models.Feed.user_id)
            .where(models.Feed.time >= date_before)
            .distinct()
            .count()
    )

    return {
        "total": total,
        "today": today,
        "total_user": total_user,
        "today_user": today_user,
    }


@app.get("/statistics/24h")
async def get_statistics_24h(date: Annotated[datetime.datetime, Query()]):
    """获取统计信息"""

    end_date = date
    start_date = end_date - datetime.timedelta(days=1)

    query = (models.Feed
            .select(fn.date_trunc('hour', models.Feed.time).alias('hour'), fn.COUNT(models.Feed.id).alias('feed_count'))
            .where((models.Feed.time >= start_date) & (models.Feed.time <= end_date))
            .group_by(fn.date_trunc('hour', models.Feed.time))
            .order_by(fn.date_trunc('hour', models.Feed.time)))

    data = [
        {
            'time': entry.hour,
            'count': entry.feed_count,
        }
        for entry in query
    ]

    return data


@app.get("/statistics/60d")
async def get_statistics_60d(date: Annotated[datetime.datetime, Query()]):
    """获取统计信息"""

    end_date = date
    start_date = end_date - datetime.timedelta(days=60)

    query = (models.Feed
            .select(models.Feed.time.cast('date').alias('date'), fn.COUNT(models.Feed.id).alias('feed_count'))
            .where((models.Feed.time >= start_date) & (models.Feed.time <= end_date))
            .group_by(models.Feed.time.cast('date'))
            .order_by(models.Feed.time.cast('date')))

    data = [
        {
            'time': entry.date,
            'count': entry.feed_count,
        }
        for entry in query
    ]

    return data
