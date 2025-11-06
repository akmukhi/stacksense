from abc import abstractmethod
from DTO.User import User
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends

class IUserRepository:
    @abstractmethod
    