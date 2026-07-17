from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel): # what cleint sends when registering email + pass
    email: EmailStr
    password: str
    
class UserOut(BaseModel): # what fastapi sends to the client
    id:int
    email: EmailStr
    
    class Config:
        from_attributes = True
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr 
    
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    
class EmailCheckRequest(BaseModel):
    email: EmailStr
    