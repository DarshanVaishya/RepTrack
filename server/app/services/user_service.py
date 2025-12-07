from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import CreateUserPayload, TokenResponse, UpdateUserPayload
from app.utils.password import hash_password, verify_password
from app.utils.logger import logger
from app.models.user import User, UserRole
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.utils.auth import create_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


# TODO: Add error handling
class UserService:
    @staticmethod
    def create_new_user(user_data: CreateUserPayload, db: Session):
        user_dict = user_data.model_dump()
        logger.debug(f"Creating new user: {user_dict['name']}")

        duplicate = db.query(User).filter(User.email == user_dict["email"]).first()
        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

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
        logger.debug("Attempting to fetch all users.")
        users = db.query(User).all()
        logger.info(f"Successfully fetched {len(users)} users from the database.")
        return users

    @staticmethod
    def get_user_by_id(user_id: int, db: Session):
        logger.debug(f"Attempting to fetch user with id {user_id}.")
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            logger.error(f"User with id {user_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found.",
            )
        logger.debug(f"Successfully fetched user - ID: {user_id} Name: {user.name}")
        return user

    @staticmethod
    def update_user_details(user_id: int, update_data: UpdateUserPayload, db: Session):
        logger.debug(f"Updating user - ID: {user_id}")
        user = UserService.get_user_by_id(user_id, db)
        update_dict = update_data.model_dump(exclude_unset=True)
        update_dict["email"] = update_dict["email"].lower()

        fields_to_update = [k for k in update_dict.keys() if k != "password"]
        if fields_to_update:
            logger.debug(
                f"Updating fields for user {user_id}: {', '.join(fields_to_update)}"
            )

        if "password" in update_dict and update_dict["password"]:
            logger.debug(f"Password update requested for user {user_id}")
            update_dict["password"] = hash_password(update_dict["password"])

        for field, value in update_dict.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        logger.info(f"Successfully updated user - ID: {user_id}, Name: {user.name}")
        return user

    @staticmethod
    def delete_user(user_id: int, db: Session):
        user = UserService.get_user_by_id(user_id, db)
        db.delete(user)
        db.commit()
        return user

    @staticmethod
    def login_user(form_data: OAuth2PasswordRequestForm, db: Session):
        user = db.query(User).filter(User.email == form_data.username.lower()).first()

        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credentials",
            )

        token = create_access_token({"user": {"email": user.email, "id": user.id}})
        return TokenResponse(access_token=token)
