from fastapi import APIRouter, HTTPException
from database import get_connection
from models import ProductCreate

router = APIRouter()


@router.get("/products")
def get_products(categorie: str | None = None):
    with get_connection() as conn:
        if categorie is not None:
            if categorie not in ("cafe", "food"):
                raise HTTPException(400, "Catégorie invalide")

            rows = conn.execute("""
                SELECT * FROM products
                WHERE categorie = ? AND disponible = 1
            """, (categorie,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM products WHERE disponible = 1
            """).fetchall()

    return [dict(row) for row in rows]


@router.get("/products/{product_id}")
def get_product(product_id: int):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT * FROM products WHERE id = ?
        """, (product_id,)).fetchone()

    if row is None:
        raise HTTPException(404, "Produit introuvable")

    return dict(row)


@router.post("/products", status_code=201)
def add_product(product: ProductCreate):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO products
            (nom, description, prix, categorie, image_url, disponible)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            product.nom,
            product.description,
            product.prix,
            product.categorie,
            product.image_url,
            int(product.disponible)
        ))

        row = conn.execute(
            "SELECT * FROM products WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()

    return dict(row)


@router.delete("/products/{product_id}")
def delete_product(product_id: int):
    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE products SET disponible = 0 WHERE id = ?
        """, (product_id,))

        if cursor.rowcount == 0:
            raise HTTPException(404, "Produit introuvable")

    return {"message": "Produit désactivé"}

from fastapi import APIRouter, HTTPException
from database import get_connection
from models import OrderCreate

router = APIRouter()


@router.post("/orders", status_code=201)
def create_order(order: OrderCreate):
    with get_connection() as conn:
        client = conn.execute(
            "SELECT id FROM clients WHERE id = ?",
            (order.client_id,)
        ).fetchone()

        if client is None:
            raise HTTPException(404, "Client introuvable")

        quantities = {}
        for item in order.items:
            quantities[item.product_id] = (
                quantities.get(item.product_id, 0) + item.quantite
            )

        lignes = []
        total = 0.0

        for product_id, quantite in quantities.items():
            product = conn.execute("""
                SELECT id, prix FROM products
                WHERE id = ? AND disponible = 1
            """, (product_id,)).fetchone()

            if product is None:
                raise HTTPException(
                    400,
                    f"Produit {product_id} indisponible"
                )

            prix = float(product["prix"])
            total += prix * quantite
            lignes.append((product_id, quantite, prix))

        cursor = conn.execute("""
            INSERT INTO orders (client_id, total)
            VALUES (?, ?)
        """, (order.client_id, round(total, 2)))

        order_id = cursor.lastrowid

        conn.executemany("""
            INSERT INTO order_items
            (order_id, product_id, quantite, prix_unitaire)
            VALUES (?, ?, ?, ?)
        """, [
            (order_id, product_id, quantite, prix)
            for product_id, quantite, prix in lignes
        ])

    return {
        "message": "Commande créée",
        "order_id": order_id,
        "total": round(total, 2),
        "statut": "En attente"
    }


@router.get("/orders/{order_id}")
def get_order(order_id: int):
    with get_connection() as conn:
        order = conn.execute("""
            SELECT * FROM orders WHERE id = ?
        """, (order_id,)).fetchone()

        if order is None:
            raise HTTPException(404, "Commande introuvable")

        items = conn.execute("""
            SELECT oi.product_id, p.nom, oi.quantite,
                   oi.prix_unitaire,
                   oi.quantite * oi.prix_unitaire AS sous_total
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            WHERE oi.order_id = ?
        """, (order_id,)).fetchall()

    result = dict(order)
    result["items"] = [dict(item) for item in items]
    return result


@router.get("/clients/{client_id}/orders")
def get_client_orders(client_id: int):
    with get_connection() as conn:
        client = conn.execute(
            "SELECT id FROM clients WHERE id = ?",
            (client_id,)
        ).fetchone()

        if client is None:
            raise HTTPException(404, "Client introuvable")

        rows = conn.execute("""
            SELECT * FROM orders
            WHERE client_id = ?
            ORDER BY id DESC
        """, (client_id,)).fetchall()

    return [dict(row) for row in rows]