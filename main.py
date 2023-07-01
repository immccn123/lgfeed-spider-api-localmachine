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


@app.middleware("http")
async def auth(request: Request, call_next):
    if request.headers.get("X-LGF-Auth") != "ImkenHaomeng":
        return Response(status_code=403)
    response = await call_next(request)
    return response


app.include_router(routes)
