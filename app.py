

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import requests
from urllib.parse import quote
app = Flask(__name__)
app.secret_key = "third_eye_secret_key"

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- ABOUT ----------------
@app.route("/about")
def about():
    return render_template("about.html")


# ---------------- FEATURES ----------------
@app.route("/features")
def features():
    return render_template("features.html")


# ---------------- CONTACT ----------------
@app.route("/contact")
def contact():
    return render_template("contact.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("third_eye.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

          session["user"] = user[1]   # user's name

          return redirect(url_for("dashboard"))
        else:
            return render_template(
                "login.html",
                error="Invalid Email or Password"
            )

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("third_eye.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            conn.close()

            return render_template(
                "register.html",
                error="Email already registered! Please login."
            )

    return render_template("register.html")



# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("third_eye.db")
    cursor = conn.cursor()

    # Total registered users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Total generated faces
    cursor.execute("SELECT COUNT(*) FROM faces")
    total_faces = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        username=session["user"],
        total_users=total_users,
        total_faces=total_faces
    )
# ---------------- HISTORY ----------------
@app.route("/history", methods=["GET", "POST"])
def history():

    conn = sqlite3.connect("third_eye.db")
    cursor = conn.cursor()

    if request.method == "POST":

        gender = request.form["gender"]

        cursor.execute(
            "SELECT * FROM faces WHERE gender=? ORDER BY id DESC",
            (gender,)
        )

    else:

        cursor.execute(
            "SELECT * FROM faces ORDER BY id DESC"
        )

    faces = cursor.fetchall()

    conn.close()

    return render_template("history.html", faces=faces)
# ---------------- DELETE HISTORY ----------------
@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("third_eye.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM faces WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("history"))


# ---------------- GENERATE PAGE ----------------
@app.route("/generate")
def generate():
    return render_template("generate.html")


# ---------------- RESULT ----------------
# ---------------- RESULT ----------------
@app.route("/result", methods=["POST"])
def result():

    gender = request.form["gender"]
    age = request.form["age"]
    face = request.form["face"]
    hair = request.form["hair"]
    eyes = request.form["eyes"]
    skin = request.form["skin"]
    description = request.form["description"]

    prompt = f"""
Highly realistic forensic police sketch.

Gender: {gender}
Age: {age}
Face Shape: {face}
Hair Color: {hair}
Eye Color: {eyes}
Skin Tone: {skin}

Description:
{description}

Front-facing portrait.
Neutral facial expression.
Plain white background.
Photorealistic.
High quality.
Highly detailed.
"""

    # Generate AI Image
    image_path = generate_image(prompt)

    # Save details into SQLite database
    conn = sqlite3.connect("third_eye.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO faces
        (gender, age, face, hair, eyes, skin, description, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        gender,
        age,
        face,
        hair,
        eyes,
        skin,
        description,
        image_path
    ))

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        gender=gender,
        age=age,
        face=face,
        hair=hair,
        eyes=eyes,
        skin=skin,
        description=description,
        image=image_path
    )


# ---------------- AI IMAGE FUNCTION ----------------
def generate_image(prompt):

    prompt = quote(prompt)

    url = f"https://image.pollinations.ai/prompt/{prompt}"

    response = requests.get(url)

    # Check API response
    print("Status Code:", response.status_code)
    print("Content Type:", response.headers.get("Content-Type"))

    # Print error only if the response is NOT an image
    if "image" not in response.headers.get("Content-Type", ""):
        print(response.text[:200])

    folder = os.path.join(app.static_folder, "generated_images")
    os.makedirs(folder, exist_ok=True)

    image_path = os.path.join(folder, "generated_image.png")

    with open(image_path, "wb") as f:
        f.write(response.content)

    return "generated_images/generated_image.png"


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)