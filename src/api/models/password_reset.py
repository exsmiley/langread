from pydantic import BaseModel, EmailStr

class PasswordResetRequest(BaseModel):
    """Model for requesting a password reset"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Model for confirming a password reset with a new password"""
    token: str
    new_password: str
