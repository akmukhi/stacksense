from respositories.IUserRepository import IUserRepository
from entity_manager.entity_manager import entity_manager
from DTO.User import User, ActiveSession
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends
from passlib.context import CryptContext
from datetime import timedelta
from passlib.hash import bcrypt
from datetime import dataetime
import jwt
from jwt import PyJWTError
from fastapi import HTTPException

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

#Crypt Context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository(IUserRepository):
    def __init__(self):
        self.em = entity_manager.get_collection(os.environ.get("USER_COLLECTION"))
        self.activeSessionEntityManager = entity_manager.get_collection(os.environ.get("ACTIVE_SESSION_COLLECTION"))

    def register(self, user : User):
        usr = self.em.find_one({"username": user.username})

        if usr is None:
            self.em.insert_one(
                {
                    "username": user.username,
                    "password": bcrypt.using(rounds=12).hash(user.password)
                }
            )
            return user
        else:
            return False
        
    def create_access_token(self, data: dict, expires_delta):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, os.environ.get("SECRET_KEY"), algorithm=os.environ.get("ALGORITHM"))
        return encoded_jwt
    
    def get_user(self, username: str) :
        usr = self.em.find_one({"username": username})

        if usr is not None:
            return User(
                username = usr["username"],
                password = usr["password"]
            )
        return None
    
    def is_password_correct(self, form_data: OAuth2PasswordRequestForm = Depends()) -> bool:
        user = self.get_user(form_data.username)

        if user is None or not pwd_context.verify(form_data.password, user.password):
            return False
        return True

    def get_access_token(self, form_data = OAuth2PasswordRequestForm = Depends()):
        
    