from pydantic import BaseModel, EmailStr, Field, SecretStr, model_validator


class SignUpSchema(BaseModel):
    email: EmailStr = Field(
        min_length=5, max_length=100, description="Email of the user"
    )
    password: SecretStr = Field(min_length=6, max_length=100, description="Password")
    password_confirmation: SecretStr = Field(
        min_length=6, max_length=100, description="Password"
    )

    @model_validator(mode="after")
    def password_match(self):
        if (
            self.password.get_secret_value()
            != self.password_confirmation.get_secret_value()
        ):
            raise ValueError("Password and Password confirmation does not match")

        return self


class LoginSchema(BaseModel):
    email: EmailStr = Field(
        min_length=5, max_length=100, description="Email of the user"
    )
    password: SecretStr = Field(min_length=6, max_length=100, description="Password")


class TokenResponseSchema(BaseModel):
    access_token: str
