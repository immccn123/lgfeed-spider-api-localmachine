from fastapi import FastAPI, Request, Response
from routers import routes

app = FastAPI(
    title="Luogu Feed Tools",
    description="懒得写了",
    version="0.0.1",
    contact={
        "name": "Imken Luo",
        "url": "https://imken.moe",
        "email": "me@imken.moe",
    },
    redoc_url=None,
)

app.include_router(routes)
