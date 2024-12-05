from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import pymysql
import csv
import math
import os
import random
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv('DB_PORT'))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

conn = pymysql.connect (host = DB_HOST,port = DB_PORT, user = DB_USER, password = DB_PASSWORD, db = DB_NAME, charset='utf8')
cur = conn.cursor()

app = FastAPI()

# CORS 설정
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 출처 목록
    allow_credentials=True,
    allow_methods=["POST","OPTIONS","GET"],  # 허용할 HTTP 메서드
    allow_headers=["*"],  # 허용할 헤더
)
def getDbConnection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        charset='utf8'
    )
def getHashedPassword(password):
    return bcrypt_context.hash(password)

def getMoonid():
    x = ''
    for _ in range(8):
        x += str(random.randint(0,9))
    return x

class CreateMoon(BaseModel):
    name: str  # 이름
    password: str  # 비밀번호



@app.post("/moon/newmoon")
def CreateMoon(request: CreateMoon):
    conn = getDbConnection()
    cur = conn.cursor()
    try:
        name = request.name
        password = getHashedPassword(request.password)
        moonid = getMoonid()
        query = "INSERT INTO moon (moonid, user_name, user_password, person) VALUES (%s, %s, %s, 0)"
        cur.execute(query, (moonid, name, password))
        conn.commit()   
        return moonid
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)