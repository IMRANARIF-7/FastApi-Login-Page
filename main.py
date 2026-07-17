from database import engine, Base
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from routes.auth_routes import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

import models
from models import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    


app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:3000", "http://127.0.0.1:3000"] #domain 

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins, # this makes sure that the request form urls in origin make it through
    allow_credentials = True, # this makes sure to allow cookies n authorizatio headers
    allow_methods = ['*'], # make sure http methods like get post put etc are allwoed 
    allow_headers = ['*'] # allows custom header to go through
)

app.include_router(auth_router)



        
        
# passlib[bcrypt] - handles password hashign
# python-jose[cryptography] - creates and verifies jwt tokens
# python-multipart - required by FastApi to form login - data (OAuth2standard)

