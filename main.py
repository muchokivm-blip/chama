import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from chama import Chama

FILE = os.environ.get("CHAMA_FILE", "chama.json")
STATIC = Path(__file__).parent / "static"

app = FastAPI(title="chama")
chama = Chama.load(FILE)


class Member(BaseModel):
    name: str = Field(min_length=1, max_length=40)


class Amount(BaseModel):
    amount: int = Field(ge=1)


class Close(BaseModel):
    paid: list[str]


@app.exception_handler(ValueError)
def bad_request(request, exc):
    return JSONResponse({"detail": str(exc)}, status_code=400)


def saved():
    chama.save(FILE)
    return chama.view()


@app.get("/api/chama")
def show():
    return chama.view()


@app.post("/api/members")
def add_member(body: Member):
    chama.add(body.name.strip())
    return saved()


@app.delete("/api/members/{name}")
def remove_member(name: str):
    chama.remove(name)
    return saved()


@app.put("/api/amount")
def set_amount(body: Amount):
    chama.set_amount(body.amount)
    return saved()


@app.post("/api/months")
def close_month(body: Close):
    chama.close_month(body.paid)
    return saved()


@app.post("/api/months/{n}/late")
def pay_late(n: int, body: Member):
    chama.pay_late(n, body.name)
    return saved()


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
