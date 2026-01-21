from passlib.context import CryptContext

from app.nastroyki import nastroyki


kontekst = CryptContext(
    schemes=[nastroyki.hash_scheme],
    deprecated="auto",
    argon2__time_cost=nastroyki.argon2_time_cost,
    argon2__memory_cost=nastroyki.argon2_memory_cost,
    argon2__parallelism=nastroyki.argon2_parallelism,
)


def sdelat_hash(parol: str) -> str:
    return kontekst.hash(parol)


def proverit_parol(parol: str, password_hash: str) -> bool:
    return kontekst.verify(parol, password_hash)
