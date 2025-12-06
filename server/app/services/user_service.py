from sqlalchemy.orm import Session
from app.schemas.user import CreateUserPayload
from app.utils.password import hash_password
from app.utils.logger import logger
from app.models.user import User


class UserService:
    @staticmethod
    def create_new_user(user_data: CreateUserPayload, db: Session):
        user_dict = user_data.model_dump()
        logger.debug(f"Creating new user: {user_dict['name']}")

        user_dict["password"] = hash_password(user_dict["password"])

        new_user = User(**user_dict)
        new_user.email = new_user.email.lower()
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(
            f"Successfully created new user - ID: {new_user.id} Email: {new_user.email}"
        )

        return new_user

    @staticmethod
    def get_all_users(db: Session):
        users = db.query(User).all()
        return users

    @staticmethod
    def get_user_by_id(user_id: int, db: Session):
        user = db.query(User).filter(User.id == user_id).first()
        return user
