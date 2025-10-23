from datetime import datetime

from app.core.singleton.firestore import db
from app.schemas.users import UserBaseDto


class UserRepository:
    def __init__(self, collection_name: str = "users"):
        self.collection = db.collection(collection_name)

    def create_user(self, data: UserBaseDto):
        date_time = datetime.now()
        extra_data = {
            "created_at": date_time,
            "updated_at": date_time,
            "deleted_at": None,
        }
        extra_data.update(data.model_dump())
        self.collection.add(extra_data)

    def user_exist_by_id(self, id: str):
        user = (
            self.collection.where("__name__", "in", [id])
            .where("deleted_at", "==", None)
            .get()
        )
        return bool(user)

    def user_exist_by_email(self, email: str):
        user = (
            self.collection.where("email", "in", [email])
            .where("deleted_at", "==", None)
            .get()
        )
        return bool(user)

    def get_user(self, id):
        users = (
            self.collection.where("__name__", "in", [id])
            .where("deleted_at", "==", None)
            .get()
        )
        if not len(users):
            return None

        user, *_rest = users
        return user.to_dict()

    def get_users(self):
        # this post has the solution to the filter keyword warning
        # https://stackoverflow.com/a/76285475
        users = []
        user_docs = self.collection.where("deleted_at", "==", None).stream()
        for user in user_docs:
            users.append(user.to_dict())
        return users

    def update_user(self, id, data: UserBaseDto):
        user = self.get_user(id)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            if not user:
                return None
            return user

        doc_ref = self.collection.document(user.id)

        extra_data = {
            "updated_at": datetime.now(),
        }
        extra_data.update(update_data)
        doc_ref.update(extra_data)
        return doc_ref.get().to_dict()

    def delete_user(self, id):
        if not self.user_exist_by_id(id):
            return None

        date_time = datetime.now()
        self.collection.document(id).update(
            {"updated_at": date_time, "deleted_at": date_time}
        )
        return True
