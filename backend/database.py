import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "database.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                adresse TEXT NOT NULL,
                telephone TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                description TEXT DEFAULT '',
                prix REAL NOT NULL CHECK(prix >= 0),
                categorie TEXT NOT NULL
                    CHECK(categorie IN ('cafe', 'food')),
                image_url TEXT DEFAULT '',
                disponible INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                date_commande TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                statut TEXT NOT NULL DEFAULT 'En attente',
                total REAL NOT NULL DEFAULT 0,
                FOREIGN KEY(client_id) REFERENCES clients(id)
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantite INTEGER NOT NULL CHECK(quantite > 0),
                prix_unitaire REAL NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            );
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

        if count == 0:
            produits = [
                ("Café Express", "Café classique", 2.0, "cafe", ""),
                ("Cappuccino", "Café au lait mousseux", 4.5, "cafe", ""),
                ("Croissant", "Croissant frais", 2.5, "food", ""),
                ("Sandwich", "Sandwich maison", 6.0, "food", ""),
                ("Pizza", "Pizza préparée sur place", 9.0, "food", "")
            ]

            conn.executemany("""
                INSERT INTO products
                (nom, description, prix, categorie, image_url)
                VALUES (?, ?, ?, ?, ?)
            """, produits)


def init_database():
    create_tables()