import datetime
import re

from fastapi import APIRouter
from peewee import fn

from db import get_connection, models

db = get_connection()

app = APIRouter()


@app.get("/rank/dragon")
async def dragon_king():
    current_time = datetime.datetime.now()
    offset = datetime.timedelta(days=-30)
    return [
        {
            "uid": feed.user_id,
            "name": feed.username,
            "count": feed.cnt,
        }
        for feed in (
            models.Feed.select(
                models.Feed.user_id,
                fn.MAX(models.Feed.username).alias("username"),
                fn.COUNT(models.Feed.content).alias("cnt"),
            )
            .group_by(models.Feed.user_id, models.Feed.username)
            .where(models.Feed.time >= (current_time + offset))
            .order_by(-fn.COUNT(models.Feed.content).alias("cnt"))
            .limit(100)
        )
    ]


@app.get("/rank/tietie")
async def tietie():
    current_time = datetime.datetime.now()
    offset = datetime.timedelta(days=-30)
    user_count = {}
    usernames = {}
    user_color = {}
    response = []
    for feed in (
        models.Feed.select(
            models.Feed.username,
            models.Feed.user_id,
            models.Feed.user_color,
            models.Feed.content,
        )
        .where(
            (models.Feed.time >= (current_time + offset))
            & models.Feed.content.contains("贴贴")
        )
        .order_by(models.Feed.time)
    ):
        if "贴贴" in feed.content.split("||")[0]:
            if user_count.get(feed.user_id) is None:
                user_count[feed.user_id] = 0
            user_count[feed.user_id] += 1
        usernames[feed.user_id] = feed.username
        user_color[feed.user_id] = feed.user_color
    user_count = sorted(user_count.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    for rank in enumerate(user_count):
        if rank[1][1] >= 5:
            response.append(
                {
                    "uid": rank[1][0],
                    "count": rank[1][1],
                    "name": usernames[rank[1][0]],
                    "color": user_color[rank[1][0]],
                }
            )
        if len(response) >= 100:
            break
    return response


@app.get("/rank/bePinged")
async def be_notificated():
    current_time = datetime.datetime.now()
    offset = datetime.timedelta(days=-30)
    user_count = {}
    usernames = {}
    response = []
    for feed in (
        models.Feed.select(
            models.Feed.username,
            models.Feed.user_id,
            models.Feed.content,
        )
        .where(
            (models.Feed.time >= (current_time + offset))
            & models.Feed.content.contains("@")
        )
        .order_by(models.Feed.time)
    ):
        parts = re.findall(r"\[(\S+)\]\(/user/(\d+)\)", feed.content)
        for tp in parts:
            if user_count.get(tp[1]) is None:
                user_count[tp[1]] = 0
            user_count[tp[1]] += 1
            usernames[tp[1]] = tp[0]
    user_count = sorted(user_count.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    for rank in enumerate(user_count):
        response.append(
            {
                "uid": rank[1][0],
                "count": rank[1][1],
                "name": usernames[rank[1][0]],
            }
        )
        if len(response) >= 100:
            break
    return response


@app.get("/rank/pingOthers")
async def notificate_others():
    current_time = datetime.datetime.now()
    offset = datetime.timedelta(days=-30)
    user_count = {}
    usernames = {}
    user_color = {}
    response = []
    for feed in (
        models.Feed.select(
            models.Feed.username,
            models.Feed.user_id,
            models.Feed.content,
        )
        .where(
            (models.Feed.time >= (current_time + offset))
            & models.Feed.content.contains("@")
        )
        .order_by(models.Feed.time)
    ):
        parts = re.findall(r"\[(\S+)\]\(/user/(\d+)\)", feed.content)
        if user_count.get(feed.user_id) is None:
            user_count[feed.user_id] = 0
        user_count[feed.user_id] += len(parts)
        usernames[feed.user_id] = feed.username
        user_color[feed.user_id] = feed.user_color
    user_count = sorted(user_count.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    for rank in enumerate(user_count):
        response.append(
            {
                "uid": rank[1][0],
                "count": rank[1][1],
                "name": usernames[rank[1][0]],
                "color": user_color[rank[1][0]],
            }
        )
        if len(response) >= 100:
            break
    return response
