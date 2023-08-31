from fastapi import APIRouter
from peewee import fn
from db import get_connection, models

db = get_connection()

app = APIRouter()


@app.get("/blackHistory/feed/{uid}")
async def get_history_feed(uid: int, per_page: int = 100, page: int = 1):
    response = []
    current_color = "Unknown"
    for feed in (
        models.Feed.select(
            models.Feed.id,
            models.Feed.username,
            models.Feed.user_color,
            models.Feed.content,
            models.Feed.time,
            models.Feed.grub_time,
        )
        .where(models.Feed.user_id == uid)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .order_by(-models.Feed.time)
    ):
        current_color = feed.user_color
        response.append(
            {
                "id": feed.id,
                "name": feed.username,
                "time": feed.time,
                "content": feed.content,
                "grab_time": feed.grub_time,
            }
        )
    return {"user_color": current_color, "feeds": response}


@app.get("/blackHistory/usernames/{uid}")
async def get_history_username_by_uid(uid: int):
    response = []
    is_visit = {}
    for feed in models.Feed.select(
        models.Feed.username,
    ).where(models.Feed.user_id == uid):
        if is_visit.get(feed.username) is None:
            response.append(feed.username)
            is_visit[feed.username] = 1
    return response


@app.get("/blackHistory/uids/{username}")
async def get_history_uid_by_username(username: str):
    response = []
    is_visit = {}
    for feed in models.Feed.select(
        models.Feed.user_id,
    ).where(fn.Lower(models.Feed.username) == fn.Lower(username)):
        if is_visit.get(feed.user_id) is None:
            response.append(feed.user_id)
            is_visit[feed.user_id] = 1
    return response
