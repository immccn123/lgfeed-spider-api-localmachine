import datetime

from fastapi import APIRouter

from db import get_connection, models

db = get_connection()

app = APIRouter()


@app.get("/rank/dragon")
async def dragon_king():
    current_time = datetime.datetime.now()
    offset = datetime.timedelta(days=-30)
    user_count = {}
    usernames = {}
    user_color = {}
    for feed in (
        models.Feed.select(
            models.Feed.username, models.Feed.user_id, models.Feed.user_color
        )
        .where(models.Feed.time >= (current_time + offset))
        .order_by(models.Feed.time)
    ):
        if user_count.get(feed.user_id) is None:
            user_count[feed.user_id] = 0
        user_count[feed.user_id] += 1
        usernames[feed.user_id] = feed.username
        user_color[feed.user_id] = feed.user_color
    user_count = sorted(user_count.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    for rank in enumerate(user_count):
        user_count[rank[0]] = {
            "uid": rank[1][0],
            "count": rank[1][1],
            "name": usernames[rank[1][0]],
            "color": user_color[rank[1][0]],
        }
    return user_count[0:100]


@app.get("/rank/tietie")
async def tietie():
    # TODO: WIP
    return []

@app.get("/rank/notification")
async def notification():
    # TODO: WIP
    return []
