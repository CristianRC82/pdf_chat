import logging

from fastapi import Depends, status
from fastapi.routing import APIRouter

from app.repository.user_repository import UserRepository
from app.schemas.users import UserBaseDto, UserUpdateDto
from app.services.users import UserService

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service():
    repository = UserRepository(collection_name="users")
    return UserService(repository)


@router.post("", status_code=status.HTTP_201_CREATED, description="Create an user", summary="This API will ")
def create_user(
    user: UserBaseDto,
    service: UserService = Depends(get_user_service),
):
    logger.info("Start process to create a new user")
    return service.create(user)


@router.get("/{id}")
def get_user(
    id: str,
    service: UserService = Depends(get_user_service),
):
    return service.get_user(id)


@router.get("")
def get_users(
    service: UserService = Depends(get_user_service),
):
    return service.get_all()


@router.patch("/{id}")
def update_user(
    id: str,
    user: UserUpdateDto,
    service: UserService = Depends(get_user_service),
):
    return service.update_user(id, user)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: str,
    service: UserService = Depends(get_user_service),
):
    return service.delete_user(id)
