from flask import Flask, render_template, request, redirect
import sqlite3
from pathlib import Path
app = Flask(__name__)
def get_db_connection():
    """
    Izveido un atgriež savienojumu ar SQLite datubāzi.
    """
    db = Path(__file__).parent / "dreamfluff.db"
    
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/produkti/<int:product_id>")
def products_show(product_id):
    conn = get_db_connection()
    product = conn.execute(
        """
        SELECT "products".*, "materials"."materiali" AS "materiali", "izmers"."kads" AS "kads",  "color"."krasa" AS "krasa" 
        FROM "products"
        LEFT JOIN "materials" ON "products"."materials_id" = "materials"."id"
        LEFT JOIN "izmers" ON "products"."izmers_id" = "izmers"."id"
        LEFT JOIN "color" ON "products"."color_id" = "color"."id"
        WHERE "products"."id" = ?
        """,
        (product_id,)
    ).fetchone()

    # Iegūst atsauksmes par šo konkrēto produktu
    reviews = conn.execute(
        "SELECT * FROM atsauksmes WHERE produkts_id = ?", (product_id,)
    ).fetchall()
    
    conn.close()

    return render_template("products_show.html", product=product, reviews=reviews)

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/produkti")
def products():
    conn = get_db_connection() # Pieslēdzas datubāzei
    # Izpilda SQL vaicājumu, kas atlasa visus produktus
    
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close() # Aizver savienojumu ar datubāzi
    # Atgriežam HTML veidni "products.html", padodot produktus veidnei
    return render_template("products.html", products=products)
@app.route("/product/<int:product_id>")
def show_product(product_id):
    return products_show(product_id)
@app.route("/produkti/<int:product_id>/atsauksme", methods=["GET", "POST"])
def pievienot_atsauksmi(product_id):
    if request.method == "POST":
        vards = request.form["vards"]
        teksts = request.form["teksts"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO atsauksmes (produkts_id, vards, teksts) VALUES (?, ?, ?)",
            (product_id, vards, teksts)
        )
        conn.commit()
        conn.close()
        return redirect(f"/produkti/{product_id}")

    return render_template("pievienot_atsauksmi.html", product_id=product_id)
def create_reviews_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS atsauksmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produkts_id INTEGER NOT NULL,
            vards TEXT NOT NULL,
            teksts TEXT NOT NULL,
            FOREIGN KEY (produkts_id) REFERENCES products(id)
        )
    """)
    conn.commit()
    conn.close()
    print("Tabula atsauksmes ir izveidota vai jau eksistē.")
@app.route("/produkti/<int:product_id>/atsauksme/dzest/<int:review_id>", methods=["POST"])
def dzest_atsauksmi(product_id, review_id):
    conn = get_db_connection()

    # Dzēš atsauksmi no atsauksmju tabulas, izmantojot atsauksmes ID
    conn.execute("DELETE FROM atsauksmes WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()

    # Pāradresē uz produkta lapu, kurā tika dzēsta atsauksme
    return redirect(f"/produkti/{product_id}")



@app.route("/par-mums")
def about():
    return render_template("about.html")
if __name__ == "__main__":
    app.run(debug=True)
