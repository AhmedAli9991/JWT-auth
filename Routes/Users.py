from http import cookies
from re import L
from fastapi import APIRouter, status, HTTPException,Depends,Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_schemas import pydantic_Users
from DB.SQL_Alchemy_Models.Models_Users import Users
from Utils.passwords import hash,verify
from DB.db_setup import get_db
from Utils.JWT import create_tokens,get_current_user
from config import settings
from sqlalchemy.future import select
from sqlalchemy import insert
ACCESS_KEY = settings.access_key
REFRESH_KEY = settings.refresh_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE = settings.access_expire
REFRESH_TOKEN_EXPIRE = settings.refresh_expire

router = APIRouter()
@router.post('/Login',status_code=status.HTTP_200_OK, response_model= pydantic_Users.final_user)
async def login(User:pydantic_Users.base_user,response:Response,db: AsyncSession = Depends(get_db)):
    query = select(Users).where(User.email == Users.email)
    result = await db.execute(query)
    found = result.scalar_one_or_none()
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid Email")
    checkpass = verify(User.password,found.password)
    if not checkpass:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid password")    
    data={"id":found.id,"name":found.name,"email":found.email}
    ACCESS_TOKEN=create_tokens(data,ACCESS_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE)
    REFRESH_TOKEN=create_tokens(data,REFRESH_KEY,ALGORITHM,REFRESH_TOKEN_EXPIRE)
    response.set_cookie(key="ACCESS_TOKEN",value=ACCESS_TOKEN,max_age=300000,httponly=True)
    response.set_cookie(key="REFRESH_TOKEN",value=REFRESH_TOKEN,max_age=900000,httponly=True)
    return found 

@router.post('/Signup',status_code=status.HTTP_201_CREATED, response_model= pydantic_Users.final_user)
async def create_user(User:pydantic_Users.in_user,db: AsyncSession = Depends(get_db)):
    query = select(Users).where(User.email == Users.email)
    result = await db.execute(query)
    found = result.scalar_one_or_none()
    if found:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="already exists")
    password = hash(User.password)
    User.password = password
    new = insert(Users).values(**User.dict())
    await db.execute(new)
    query = select(Users).where(User.email == Users.email)
    result = await db.execute(query)
    found = result.scalar_one_or_none()
    return found

@router.post('/Logout')
def Logout(response:Response,current_user = Depends(get_current_user)):
    if(current_user):
        response.delete_cookie("ACCESS_TOKEN")
        response.delete_cookie("REFRESH_TOKEN")
        return "deleted cookies"
    else:
        return "cookies do not exist"

@router.get('/Get')
def getUser(current_user = Depends(get_current_user)):
    if(current_user):
        return current_user
        