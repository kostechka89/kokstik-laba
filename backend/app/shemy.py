import re
from pydantic import BaseModel, field_validator


class RegistratsiyaZapros(BaseModel):
    login: str
    parol: str

    @field_validator("login")
    @classmethod
    def proverka_logina(cls, znachenie: str) -> str:
        if not re.fullmatch(r"[a-zA-Z0-9._-]{3,32}", znachenie):
            raise ValueError("login должен быть 3-32 символа и состоять из латиницы, цифр, . _ -")
        return znachenie

    @field_validator("parol")
    @classmethod
    def proverka_parolya(cls, znachenie: str) -> str:
        if len(znachenie) < 8:
            raise ValueError("parol должен быть не короче 8 символов")
        if not any(simv.islower() for simv in znachenie):
            raise ValueError("parol должен содержать строчную букву")
        if not any(simv.isupper() for simv in znachenie):
            raise ValueError("parol должен содержать заглавную букву")
        if not any(simv.isdigit() for simv in znachenie):
            raise ValueError("parol должен содержать цифру")
        if not re.search(r"[!@#$%^&*()_+\-\[\]{};':\"\\|,.<>/?`~]", znachenie):
            raise ValueError("parol должен содержать спецсимвол")
        return znachenie


class RegistratsiyaOtvet(BaseModel):
    message: str


class VhodZapros(BaseModel):
    login: str
    parol: str


class VhodOtvet(BaseModel):
    message: str
