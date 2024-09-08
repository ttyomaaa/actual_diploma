from fastapi import (FastAPI,
                     WebSocket,
                     Request,
                     WebSocketDisconnect,
                     HTTPException,
                     Response)
from starlette.staticfiles import StaticFiles
from links import generate_tmp_link, verify_tmp_link
from config.settings import SECRET_KEY
from fastapi.templating import Jinja2Templates
from user_handler import process_message, process_room
from pydantic import BaseModel
from celery import Celery
from fill_tables import context_list
from db.insert_data import create_room
from load_models import load_models
from celery.result import AsyncResult
import os
import asyncio

import uuid
import redis.asyncio as redis

os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")

rdb = redis.from_url("redis://localhost:6379?decode_responses=True")

cel = Celery('tasks',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             broker_connection_retry_on_startup=True
             )

models = load_models()


class LinkRequest(BaseModel):
    author_id: str
    expiration_minutes: int


@cel.task
def generate_link_task(author_id, expiration_minutes):
    loop = asyncio.get_event_loop()
    room_id, last_idx = loop.run_until_complete(create_room(models=models, published_by=author_id, contexts=context_list))
    loop.run_until_complete(process_room(room_id=room_id, last_idx=last_idx, rdb=rdb))
    temporary_link = generate_tmp_link(str(room_id), SECRET_KEY, expiration_minutes)

    return temporary_link


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="generate_poll.html")


@app.post("/generate_link")
async def generate_link(request: LinkRequest):
    task = generate_link_task.apply_async(args=(request.author_id, request.expiration_minutes))

    return {"task_id": task.id}


@app.get("/check_task_status/{task_id}")
async def check_task_status(task_id: str):
    task = AsyncResult(task_id)
    return {"status": task.status, "result": task.result}


@app.websocket("/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    user_id = websocket.cookies.get("user_id")

    try:
        while True:
            data = await websocket.receive_text()
            responses = await process_message(user_id=user_id,
                                              room_id=room_id,
                                              message=data,
                                              models=models,
                                              rdb=rdb)
            await websocket.send_text(responses[0])
            await websocket.send_text(responses[1])
    except WebSocketDisconnect:
        print("disconnected!")


@app.get("/chat/{room_id}")
async def get_chat(request: Request, room_id: str, token: str):
    if verify_tmp_link(token, SECRET_KEY) == room_id:
        response = Response(
            content=templates.TemplateResponse("chat.html", {"request": request, "room_id": room_id}).body
        )
        if 'user_id' not in request.cookies:
            user_id = str(uuid.uuid4())
            response.set_cookie(key="user_id", value=user_id)
        return response
        # return templates.TemplateResponse("chat.html", {"request": request, "room_id": room_id})
    else:
        raise HTTPException(status_code=401, detail="expired or does not exist")
