import datetime
import re

from fastapi import APIRouter, Response, Query
from peewee import fn

from db import get_connection, models

from typing import Union
from typing_extensions import Annotated

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
        response.status_code = 404
        return {"detail": "Feed not found"}


@app.get("/tools/search")
async def search(
    keyword: Annotated[Union[str, None], Query()] = None,
    senders: Union[list[int], None] = Query(default=None),
    date_after: Annotated[
        Union[datetime.datetime, None], Query()
    ] = None,  # UTC Time Stamp (sec) or ISO 8601 || 2008-09-15T15:53:00+05:00
    date_before: Annotated[Union[datetime.datetime, None], Query()] = None,
    id_after: Annotated[int, Query()] = 0,  # Result not includes id_after
    per_page: Annotated[int, Query(gt=0)] = 50,
):
    query = models.Feed.select(
        models.Feed.id,
        models.Feed.username,
        models.Feed.user_id,
        models.Feed.user_color,
        models.Feed.content,
        models.Feed.time,
        models.Feed.grub_time,
    )

    if keyword:
        query = query.where(models.Feed.content.contains(keyword))

    if senders:
        query = query.where(models.Feed.user_id.in_(senders))

    if date_after:
        query = query.where(models.Feed.time >= date_after)

    if date_before:
        query = query.where(models.Feed.time <= date_before)

    query = query.where(models.Feed.id > id_after)
    results = query.limit(per_page)

    return [
        {
            "id": result.id,
            "username": result.username,
            "user_id": result.user_id,
            "user_color": result.user_color,
            "content": result.content,
            "time": result.time,
            "grub_time": result.grub_time,
        }
        for result in results
    ]
