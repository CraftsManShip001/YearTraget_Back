from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import pymysql
import logging
import os
import random
import bcrypt
from passlib.hash import bcrypt
from dotenv import load_dotenv


logging.basicConfig(level=logging.ERROR, filename='app.log', format='%(asctime)s - %(message)s')
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
    "http://localhost:3001",
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
    return bcrypt.hash(password.encode('utf-8'))

def checkPassword(password, hashed):
    return bcrypt.verify(password, hashed)

def getMoonid():
    x = ''
    for _ in range(8):
        x += str(random.randint(0,9))
    return x

class CreateMoon(BaseModel):
    name: str  # 이름
    password: str  # 비밀번호
    password_check: str #비밀번호 확인

class ViewMoon(BaseModel):
    moonid:int
    
class WriteWish(BaseModel):
    name: str = Field(..., max_length=50)
    moonid: int
    wish: str = Field(..., max_length=255)
    
class GetPersonCount(BaseModel):
    moonid: int
    password: str

class ViewMoon(BaseModel):
    moonid: int

class ViewPerson(BaseModel):
    moonid: int
    password: str

@app.post("/moon/newmoon")
def CreateMoon(request: CreateMoon):
    try:
        with getDbConnection() as conn:
            with conn.cursor() as cur:
                name = request.name
                password = request.password
                password_check = request.password_check
                
                if password != password_check:
                    return 'Password is incorrect'
                
                password = getHashedPassword(password)
                moonid = getMoonid()
                query = "INSERT INTO moon (moonid, user_name, user_password, person) VALUES (%s, %s, %s, 0)"
                cur.execute(query, (moonid, name, password))
                conn.commit()
            return moonid
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        print(e)
        return {"error": "Internal server error"}, 500
        
@app.post('/moon/view')   
def ViewMoon(request: ViewMoon):
    try:
        with getDbConnection() as conn:
            with conn.cursor() as cur:
                moonid = request.moonid
                check = int(moonid)
                query = "SELECT * FROM moon where moonid = %s"
                cur.execute(query, (moonid,))
                result = cur.fetchall()
                if not result:
                    return "Moon ID not found", 404
            return result[0][1]
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return {"error": "Internal server error"}, 500
@app.post('/moon/write')
def WriteWish(request: WriteWish):
    try:
        with getDbConnection() as conn:
            with conn.cursor() as cur:
                name = request.name
                moonid = request.moonid
                wish = request.wish
                
                check = int(moonid)
                if not moonid or not name or not wish:
                    return {"error": "All fields are required"}, 400
                query = "INSERT INTO wishes (moonid, writer, wish) VALUES (%s, %s, %s)"
                cur.execute(query, (moonid,name,wish))
                
                query  = "UPDATE moon set person = person + 1 WHERE moonid = %s"
                cur.execute(query,(moonid,))
                conn.commit()
            return "Wish saved successfully"
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return {"error": "Internal server error"}, 500

@app.post('/moon/count')
def GetPersonCount(request:GetPersonCount):
    try:
        with getDbConnection() as conn:
            with conn.cursor() as cur:
                moonid = request.moonid
                check = int(moonid)
                password = request.password
                query = "SELECT user_password FROM moon where moonid = %s"
                cur.execute(query, (moonid,))
                result = cur.fetchone()
                if result and checkPassword(password,result[0]):
                    query = "SELECT person FROM moon where moonid = %s"
                    cur.execute(query, (moonid,))
                    person = cur.fetchone()
                    query = "SELECT user_name FROM moon where moonid = %s"
                    cur.execute(query, (moonid,))
                    name = cur.fetchone()
                    return {"person":person,"name":name}
                else:
                    return {"error": "Password is incorrect"}, 401
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return {"error": "Internal server error"}, 500

@app.post('/moon/person')
def ViewPerson(request:ViewPerson):
    try:
        with getDbConnection() as conn:
            with conn.cursor() as cur:
                moonid = request.moonid
                check = int(moonid)
                password = request.password
                query = "SELECT user_password FROM moon where moonid = %s"
                cur.execute(query, (moonid,))
                result = cur.fetchone()
                if result and checkPassword(password,result[0]):
                    query = "SELECT person FROM moon where moonid = %s"
                    cur.execute(query, (moonid,))
                    person = cur.fetchone()
                    query = "SELECT writer FROM wishes where moonid = %s"
                    cur.execute(query, (moonid,))
                    names = cur.fetchall()
                    return {"person":person,"names":names}
                else:
                    return {"error": "Password is incorrect"}, 401
                
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return {"error": "Internal server error"}, 500
    



if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)