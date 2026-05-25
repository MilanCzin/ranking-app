from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "change_this_key"

DB = "titles.db"


# -------------------------
# DATABASE
# -------------------------
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS titles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -------------------------
# GET TITLES
# -------------------------
def get_titles():
    conn = get_db()

    titles = conn.execute("""
        SELECT name FROM titles
        ORDER BY id
    """).fetchall()

    conn.close()

    return [title["name"] for title in titles]


# -------------------------
# INSERT TITLE
# -------------------------
def insert_title(position, title):
    conn = get_db()

    titles = get_titles()

    titles.insert(position, title)

    conn.execute("DELETE FROM titles")

    for item in titles:
        conn.execute(
            "INSERT INTO titles (name) VALUES (?)",
            (item,)
        )

    conn.commit()
    conn.close()


# -------------------------
# DELETE TITLE
# -------------------------
def delete_title(title):
    conn = get_db()

    conn.execute(
        "DELETE FROM titles WHERE name = ?",
        (title,)
    )

    conn.commit()
    conn.close()


# -------------------------
# HOME
# -------------------------
@app.route("/")
def index():
    titles = get_titles()

    return render_template(
        "index.html",
        titles=titles
    )


# -------------------------
# START ADD
# -------------------------
@app.route("/start_add", methods=["POST"])
def start_add():
    titles = get_titles()

    new_title = request.form.get("title", "").strip()

    if not new_title or new_title in titles:
        return redirect(url_for("index"))

    session["new_title"] = new_title
    session["left"] = 0
    session["right"] = len(titles) - 1

    return redirect(url_for("compare"))


# -------------------------
# COMPARE
# -------------------------
@app.route("/compare")
def compare():
    titles = get_titles()

    new_title = session.get("new_title")

    if new_title is None:
        return redirect(url_for("index"))

    left = session.get("left")
    right = session.get("right")

    # empty list
    if len(titles) == 0:
        insert_title(0, new_title)

        session.clear()

        return redirect(url_for("index"))

    # finished binary search
    if left > right:
        insert_title(left, new_title)

        session.clear()

        return redirect(url_for("index"))

    mid = (left + right) // 2

    existing = titles[mid]

    return render_template(
        "compare.html",
        new_title=new_title,
        existing=existing
    )


# -------------------------
# ANSWER
# -------------------------
@app.route("/answer", methods=["POST"])
def answer():
    left = session.get("left")
    right = session.get("right")

    mid = (left + right) // 2

    response = request.form.get("answer")

    if response == "yes":
        session["right"] = mid - 1
    else:
        session["left"] = mid + 1

    return redirect(url_for("compare"))


# -------------------------
# DELETE
# -------------------------
@app.route("/delete/<path:title>")
def delete(title):
    delete_title(title)

    return redirect(url_for("index"))


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)