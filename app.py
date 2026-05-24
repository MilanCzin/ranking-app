from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "change_this_key"

FILE = "titles.json"


# -------------------------
# LOAD DATA
# -------------------------
if os.path.exists(FILE):
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            titles = json.load(f)
    except:
        titles = []
else:
    titles = []


# -------------------------
# SAVE DATA
# -------------------------
def save():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(titles, f, indent=2)


# -------------------------
# HOME
# -------------------------
@app.route("/")
def index():
    return render_template("index.html", titles=titles)


# -------------------------
# START BINARY SEARCH ADD
# -------------------------
@app.route("/start_add", methods=["POST"])
def start_add():
    new_title = request.form.get("title", "").strip()

    if not new_title or new_title in titles:
        return redirect(url_for("index"))

    session["new_title"] = new_title
    session["left"] = 0
    session["right"] = len(titles) - 1

    return redirect(url_for("compare"))


# -------------------------
# COMPARE STEP
# -------------------------
@app.route("/compare")
def compare():
    new_title = session.get("new_title")

    if new_title is None:
        return redirect(url_for("index"))

    left = session.get("left")
    right = session.get("right")

    if len(titles) == 0:
        titles.append(new_title)
        save()
        session.clear()
        return redirect(url_for("index"))

    if left > right:
        titles.insert(left, new_title)
        save()
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
# ANSWER (binary search step)
# -------------------------
@app.route("/answer", methods=["POST"])
def answer():
    response = request.form.get("answer")

    left = session.get("left")
    right = session.get("right")
    mid = (left + right) // 2

    if response == "yes":
        session["right"] = mid - 1
    else:
        session["left"] = mid + 1

    return redirect(url_for("compare"))


# -------------------------
# DELETE ITEM
# -------------------------
@app.route("/delete/<path:title>")
def delete(title):
    if title in titles:
        titles.remove(title)
        save()

    return redirect(url_for("index"))


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)