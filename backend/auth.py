import hashlib
import hmac
import secrets

from fastapi import APIRouter, HTTPException
from database import get_connection
from models import ClientCreate, LoginData

router = APIRouter()


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200_000
    ).hex()


@router.post("/clients", status_code=201)
def register_client(client: ClientCreate):
    salt = secrets.token_hex(16)
    password_hash = hash_password(client.password, salt)

    try:
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO clients
                (nom, prenom, adresse, telephone, email, salt, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                client.nom,
                client.prenom,
                client.adresse,
                client.telephone,
                client.email.lower(),
                salt,
                password_hash
            ))

            client_id = cursor.lastrowid

        return {
            "message": "Inscription réussie",
            "client_id": client_id
        }

    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise HTTPException(
                status_code=409,
                detail="Email déjà utilisé"
            )
        raise


@router.post("/login")
def login(data: LoginData):
    with get_connection() as conn:
        client = conn.execute("""
            SELECT id, salt, password_hash
            FROM clients
            WHERE email = ?
        """, (data.email.lower(),)).fetchone()

    if client is None:
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect"
        )

    candidate = hash_password(data.password, client["salt"])

    if not hmac.compare_digest(candidate, client["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect"
        )

    return {
        "message": "Connexion réussie",
        "client_id": client["id"]
    }


@router.get("/clients/{client_id}")
def get_client(client_id: int):
    with get_connection() as conn:
        client = conn.execute("""
            SELECT id, nom, prenom, adresse, telephone, email
            FROM clients WHERE id = ?
        """, (client_id,)).fetchone()

    if client is None:
        raise HTTPException(404, "Client introuvable")

    return dict(client)