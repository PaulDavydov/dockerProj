import os, sys
from uuid import UUID, uuid4
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

MONGODB_CONNECTION_STRING = os.environ["MONGODB_CONNECTION_STRING"]

client = AsyncIOMotorClient(MONGODB_CONNECTION_STRING, uuidRepresentation="standard")
db = client.todolist
todos = db.todos

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['http://localhost'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

app = FastAPI(middleware=middleware)

class TodoItem(BaseModel):
    id: UUID = Field(default_factory = uuid4, alias = "_id")
    content: str

class TodoItemCreate(BaseModel):
    content: str

@app.post("/todos", response_model=TodoItem)
async def create_todo(item: TodoItemCreate):
    new_todo = TodoItem(content=item.content)
    await todos.insert_one(new_todo.model_dump(by_alias=True))
    return new_todo

@app.get("/todos", response_model=list[TodoItem])
async def read_todos():
    return await todos.find().to_list(length=None)

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: UUID):
    delete_result = await todos.delete_one({"_id": todo_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}