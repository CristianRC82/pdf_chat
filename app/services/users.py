from fastapi import HTTPException

from app.repository.user_repository import UserRepository
from app.schemas.users import UserBaseDto


class UserService:
    """
    Service class to handle users
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create(self, user: UserBaseDto):
        if self.repository.user_exist_by_email(user.email):
            raise HTTPException(status_code=409, detail="The user already exists")
        self.repository.create_user(user)

    def get_user(self, id: str):
        user = self.repository.get_user(id)
        if not user:
            raise HTTPException(status_code=404, detail="The user does not exists")
        return user

    def get_all(self):
        return self.repository.get_users()

    def update_user(self, id, data):
        user_updated = self.repository.update_user(id, data)
        if not user_updated:
            raise HTTPException(status_code=404, detail="The user does not exists")
        print(user_updated)
        return user_updated

    def delete_user(self, id: str):
        user_deleted = self.repository.delete_user(id)
        if not user_deleted:
            raise HTTPException(status_code=404, detail="The user does not exists")
