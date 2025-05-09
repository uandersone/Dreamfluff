from flask import Flask, render_template, request, redirect
import sqlite3
from pathlib import Path

app = Flask(__name__)

DB_PATH = Path(__file__).parent / "dreamfluff.db"

# Funkcija, lai izveidotu savienojumu ar datubāzi
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Pārliecināmies, ka atsauksmes tabula ir izveidota
conn = get_db_connection()
conn.execute('''CREATE TABLE IF NOT EXISTS atsauksmes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produkts_id INTEGER NOT NULL,
    vards TEXT NOT NULL,
    teksts TEXT NOT NULL,
    FOREIGN KEY (produkts_id) REFERENCES products(id)
)''')
conn.commit()
conn.close()

# Rāda visus produktus
@app.route("/produkti")
def produkti():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template("products.html", products=products)

# Rāda produkta detaļas un atsauksmes
@app.route("/produkti/<int:product_id>")
def produkta_skats(product_id):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    atsauksmes = conn.execute("SELECT * FROM atsauksmes WHERE produkts_id = ?", (product_id,)).fetchall()
    conn.close()
    return render_template("products_show.html", product=product, atsauksmes=atsauksmes)

# Pievieno jaunu atsauksmi
@app.route("/produkti/<int:product_id>/atsauksme", methods=["GET", "POST"])
def pievienot_atsauksmi(product_id):
    if request.method == "POST":
        vards = request.form["vards"]
        teksts = request.form["teksts"]

        conn = get_db_connection()
        conn.execute("INSERT INTO atsauksmes (produkts_id, vards, teksts) VALUES (?, ?, ?)", (product_id, vards, teksts))
        conn.commit()
        conn.close()

        return redirect(f"/produkti/{product_id}")

    return render_template("pievienot_atsauksmi.html", product_id=product_id)

# Rediģē atsauksmi
@app.route("/atsauksme/<int:id>/edit", methods=["GET", "POST"])
def rediget_atsauksmi(id):
    conn = get_db_connection()
    atsauksme = conn.execute("SELECT * FROM atsauksmes WHERE id = ?", (id,)).fetchone()

    if request.method == "POST":
        vards = request.form["vards"]
        teksts = request.form["teksts"]

        conn.execute("UPDATE atsauksmes SET vards = ?, teksts = ? WHERE id = ?", (vards, teksts, id))
        conn.commit()
        conn.close()

        return redirect(f"/produkti/{atsauksme['produkts_id']}")

    conn.close()
    return render_template("rediget_atsauksmi.html", atsauksme=atsauksme)

# Dzēš atsauksmi
@app.route("/atsauksme/<int:id>/delete", methods=["POST"])
def dzest_atsauksmi(id):
    conn = get_db_connection()
    atsauksme = conn.execute("SELECT * FROM atsauksmes WHERE id = ?", (id,)).fetchone()

    conn.execute("DELETE FROM atsauksmes WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(f"/produkti/{atsauksme['produkts_id']}")

if __name__ == "__main__":
    app.run(debug=True)
