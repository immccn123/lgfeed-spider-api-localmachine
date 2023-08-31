import datetime
import re

from fastapi import APIRouter, Response
from peewee import fn

from db import get_connection, models

db = get_connection()

app = APIRouter()


@app.get("/tools/at/{username}")
async def who_at_me(username: str):
    current_time = datetime.datetime.now()
    offset = datetime.timedelta(days=-1)
    response = []
    for feed in (
        models.Feed.select(
            models.Feed.id,
            models.Feed.username,
            models.Feed.user_id,
            models.Feed.user_color,
            models.Feed.content,
            models.Feed.time,
            models.Feed.grub_time,
        )
        .where(
            (models.Feed.content.contains(username))
            & (models.Feed.time >= current_time + offset)
        )
        .order_by(-models.Feed.time)
    ):
        parts = re.findall(r"@\[(\S+)\]\(/user/(\d+)\)", feed.content)
        for tp in parts:
            if tp[0].lower() == username.lower():
                response.append(
                    {
                        "id": feed.id,
                        "uid": feed.user_id,
                        "name": feed.username,
                        "time": feed.time,
                        "grab_time": feed.grub_time,
                        "content": feed.content,
                    }
                )
                break
    return response


@app.get("/tools/heatmap/{uid}")
async def get_heatmap_date(uid: int):
    return [
        # FIXME: PGSQL 兼容性
        {"date": feed.date, "count": feed.count}
        for feed in models.Feed.select(
            fn.DATE(models.Feed.time).alias("date"),
            fn.MAX(fn.COUNT(models.Feed.hash)).alias("count"),
        )
        .where(models.Feed.user_id == uid)
        .group_by(fn.DATE(models.Feed.time))
        .order_by(models.Feed.time)
    ]


@app.get("/tools/getFeed/{feed_id}")
async def get_feed_date(feed_id: int, response: Response):
    try:
        feed = models.Feed.get_by_id(feed_id)
        return {
            "id": feed.id,
            "uid": feed.user_id,
            "name": feed.username,
            "time": feed.time,
            "grab_time": feed.grub_time,
            "content": feed.content,
        }
    except models.Feed.DoesNotExist:
        response.status_code = 202
        return {"detail": "Feed not found"}
