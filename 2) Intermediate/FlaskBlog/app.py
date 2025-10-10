from flask import Flask, render_template, request, redirect, url_for, session
import json
from pathlib import Path
from datetime import datetime
import markdown
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

POSTS_FILE = Path("posts.json")
USERS_FILE = Path("users.json")

# ----------------- Load/Save -----------------
def load_posts():
    if POSTS_FILE.exists():
        return json.loads(POSTS_FILE.read_text())
    return []

def save_posts(posts):
    POSTS_FILE.write_text(json.dumps(posts, indent=2))

def load_users():
    if USERS_FILE.exists():
        return json.loads(USERS_FILE.read_text())
    admin = {"admin": hashlib.sha256("admin".encode()).hexdigest()}
    USERS_FILE.write_text(json.dumps(admin, indent=2))
    return admin

users = load_users()

# ----------------- Authentication -----------------
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if username in users and users[username] == hashed:
            session["username"] = username
            return redirect(url_for("index"))
        return "Invalid credentials", 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

# ----------------- Routes -----------------
@app.route("/")
def index():
    posts = load_posts()
    posts.sort(key=lambda x: x["date"], reverse=True)
    for post in posts:
        post["content_html"] = markdown.markdown(post["content"][:300] + "...")
    return render_template("index.html", posts=posts, user=session.get("username"))

@app.route("/post/<int:post_id>")
def post(post_id):
    posts = load_posts()
    post_item = next((p for p in posts if p["id"] == post_id), None)
    if not post_item:
        return "Post not found", 404
    post_item["content_html"] = markdown.markdown(post_item["content"])
    return render_template("post.html", post=post_item, user=session.get("username"))

@app.route("/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        posts = load_posts()
        new_id = max([p["id"] for p in posts], default=0) + 1
        post_item = {
            "id": new_id,
            "title": title,
            "content": content,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        posts.append(post_item)
        save_posts(posts)
        return redirect(url_for("index"))
    return render_template("new_post.html", post=None)

@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    posts = load_posts()
    post_item = next((p for p in posts if p["id"] == post_id), None)
    if not post_item:
        return "Post not found", 404
    if request.method == "POST":
        post_item["title"] = request.form.get("title")
        post_item["content"] = request.form.get("content")
        save_posts(posts)
        return redirect(url_for("post", post_id=post_id))
    return render_template("new_post.html", post=post_item)

@app.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    posts = load_posts()
    posts = [p for p in posts if p["id"] != post_id]
    save_posts(posts)
    return redirect(url_for("index"))

# ----------------- Run App -----------------
if __name__ == "__main__":
    app.run(debug=True)
