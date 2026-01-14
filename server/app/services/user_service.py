from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.schemas.user import CreateUserPayload, TokenResponse, UpdateUserPayload
from app.utils.password import hash_password, verify_password
from app.utils.logger import logger
from app.models.user import User, UserRole
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.auth import create_access_token


class UserService:
    @staticmethod
    def create_new_user(user_data: CreateUserPayload, db: Session):
        """
        Create a new user account.

        Args:
            user_data (CreateUserPayload): The payload containing user information.
            db (Session): The active SQLAlchemy database session.

        Returns:
            User: The newly created user object.

        Raises:
            HTTPException:
                - 400: If the email already exists or password is too short.
                - 500: If a database or internal error occurs.

        Logging:
            - Debug: When starting user creation.
            - Info: On successful user creation.
            - Error: On integrity or database exceptions.
        """
        user_dict = user_data.model_dump(exclude_unset=True)
        try:
            email = user_dict["email"].lower()
            logger.debug(f"Creating new user: {user_dict['name']} ({email})")

            duplicate = db.query(User).filter(User.email == email).first()
            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists",
                )

            if len(user_dict["password"]) < 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must be at least 8 characters",
                )

            user_dict["email"] = email
            user_dict["password"] = hash_password(user_dict["password"])

            new_user = User(**user_dict)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            logger.info(
                f"Successfully created user - ID: {new_user.id} Email: {new_user.email}"
            )
            return new_user

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Integrity error creating user {user_dict.get('email', 'unknown')}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists or invalid data",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during user creation",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def get_all_users(current_user: User, db: Session):
        """
        Retrieve all registered users.

        Args:
            db (Session): The active SQLAlchemy session.

        Returns:
            list[User]: A list of all user records.

        Raises:
            HTTPException:
                - 500: If a database or internal error occurs.

        Logging:
            - Debug: On start of user retrieval.
            - Info: On successful fetch.
            - Error: On database-related issues.
        """
        try:
            logger.debug("Fetching all users")
            users = db.query(User).all()
            logger.info(f"Fetched {len(users)} users")
            return users
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching users: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch users",
            )

    @staticmethod
    def get_user_by_id(user_id: int, db: Session):
        """
        Retrieve a user by their unique ID.

        Args:
            user_id (int): The unique identifier of the user.
            db (Session): The active SQLAlchemy session.

        Returns:
            User: The user object if found.

        Raises:
            HTTPException:
                - 404: If no user is found with the provided ID.
                - 500: On database or internal server errors.

        Logging:
            - Debug: On retrieval attempt.
            - Warning: If user not found.
            - Error: On SQL errors.
        """
        try:
            logger.debug(f"Fetching user ID: {user_id}")
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User ID {user_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_id} not found",
                )
            logger.debug(f"Fetched user {user_id}: {user.name}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch user",
            )

    @staticmethod
    def update_user_details(
        user_id: int, update_data: UpdateUserPayload, current_user: User, db: Session
    ):
        """
        Update an existing user's account details.

        Args:
            user_id (int): The ID of the user to update.
            update_data (UpdateUserPayload): The fields to update.
            db (Session): The active SQLAlchemy session.

        Returns:
            User: The updated user object.

        Raises:
            HTTPException:
                - 400: If no fields are provided or if email/password is invalid.
                - 404: If the user does not exist.
                - 500: For database or internal errors.

        Logging:
            - Debug: When starting the update and listing modified fields.
            - Info: On successful update.
            - Error: On integrity or SQL exceptions.
        """
        try:
            if current_user.role is not UserRole.ADMIN or current_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admin or account owner can access this method",
                )
            user = UserService.get_user_by_id(user_id, db)
            update_dict = update_data.model_dump(exclude_unset=True)

            if not update_dict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided to update",
                )

            if "email" in update_dict:
                new_email = update_dict["email"].lower()
                email_conflict = (
                    db.query(User)
                    .filter(User.email == new_email, User.id != user_id)
                    .first()
                )
                if email_conflict:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already in use by another user",
                    )
                update_dict["email"] = new_email

            if "password" in update_dict and update_dict["password"]:
                if len(update_dict["password"]) < 8:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Password must be at least 8 characters",
                    )
                update_dict["password"] = hash_password(update_dict["password"])

            fields_to_update = [k for k in update_dict if k != "password"]
            if fields_to_update:
                logger.debug(f"Updating user {user_id}: {', '.join(fields_to_update)}")

            for field, value in update_dict.items():
                setattr(user, field, value)

            db.commit()
            db.refresh(user)
            logger.info(f"Updated user {user_id}: {user.name}")
            return user

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error updating user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
            )
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during update",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error updating user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def delete_user(user_id: int, current_user: User, db: Session):
        """
        Delete a user account from the system.

        Args:
            user_id (int): The ID of the user to delete.
            db (Session): The active SQLAlchemy session.

        Returns:
            User: The deleted user object.

        Raises:
            HTTPException:
                - 404: If the user does not exist.
                - 500: On database or internal errors.

        Logging:
            - Info: On successful deletion.
            - Error: On SQL or transaction failures.
        """
        try:
            if current_user.role is not UserRole.ADMIN or current_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admin or account owner can access this method",
                )
            user = UserService.get_user_by_id(user_id, db)
            db.delete(user)
            db.commit()
            logger.info(f"Deleted user {user_id}: {user.name}")
            return user

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during deletion",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error deleting user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def login_user(form_data: OAuth2PasswordRequestForm, db: Session):
        """
        Authenticate a user and issue a JWT access token.

        Args:
            form_data (OAuth2PasswordRequestForm): The OAuth2 login form containing username and password.
            db (Session): The active SQLAlchemy session.

        Returns:
            TokenResponse: A response containing the JWT token and token type.

        Raises:
            HTTPException:
                - 401: For invalid credentials.
                - 500: For database or internal server errors.

        Logging:
            - Debug: On login attempt.
            - Info: On successful authentication.
            - Warning: On failed login attempts.
            - Error: On unexpected or database issues.
        """
        try:
            username = form_data.username.lower()
            logger.debug(f"Login attempt for: {username}")

            user = db.query(User).filter(User.email == username).first()

            if not user or not verify_password(form_data.password, user.password):
                logger.warning(f"Failed login attempt for: {username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            token = create_access_token(
                {"user": {"email": user.email, "id": user.id, "role": str(user.role)}}
            )

            logger.info(f"User {user.id} ({user.email}) logged in successfully")
            return TokenResponse(access_token=token, token_type="bearer")

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during login for {form_data.username}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login service unavailable",
            )
        except Exception as e:
            logger.error(f"Unexpected login error for {form_data.username}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
