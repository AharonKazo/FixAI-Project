from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import time
from typing import Optional
from PIL import Image 
from  prometheus_flask_exporter import PrometheusMetrics

load_dotenv() 
API_KEY = os.getenv("GEMINI_KEY")
app = Flask(__name__)
metrics = PrometheusMetrics(app)

try:
    from google import genai  # type: ignore
except Exception:
    genai = None

db_host = os.getenv("DB_HOST", "127.0.0.1")
db_name = os.getenv("DB_NAME", "flask")
db_user = os.getenv("DB_USER", "flask")
db_password = os.getenv("DB_PASSWORD", "password")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    advice = db.Column(db.Text, nullable=True)

def init_db_with_retry(max_attempts: int = 30, sleep_seconds: float = 2.0) -> None:
    last_exc: Optional[Exception] = None
    for _ in range(max_attempts):
        try:
            with app.app_context():
                db.create_all()
            return
        except Exception as exc:  
            last_exc = exc
            time.sleep(sleep_seconds)
    if last_exc:
        raise last_exc


init_db_with_retry()

@app.route('/', methods=["GET"])
def index():
    t = Todo.query.all()
    return render_template("index.html", list_todo=t)
@app.route('/add', methods=["POST"])
def add():
    title = request.form.get("title")
    file = request.files.get("file")

    if not title and (not file or file.filename == ''):
        return redirect(url_for("index"))

    advice_text = "המערכת עמוסה, נסה שוב בעוד דקה."
    if not API_KEY:
        advice_text = "שגיאה: מפתח ה-API של ג'מיני אינו מוגדר. לא ניתן לקבל הערכת מחיר."
    
    if genai is not None and API_KEY:
        client = genai.Client(api_key=API_KEY)
        
       
        model_name = "gemini-flash-lite-latest" 
        
        prompt = f"תן לי הערכת מחיר קצרה מאוד (עד 3 משפטים) לפי השוק הישראלי לתיקון: {title if title else 'המתואר בתמונה'}."
        contents = [prompt]

        if file and file.filename != '':
            try:
                img = Image.open(file.stream)
                contents.append(img)
            except Exception as e:
                print(f"Error opening image: {e}")

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents
            )
            advice_text = getattr(response, "text", advice_text) or advice_text
        except Exception as e:
            print(f"AI Error: {e}")
            if "429" in str(e):
                advice_text = "חרגת מהמכסה לדקה זו. המתן 60 שניות."

    new_todo = Todo(title=title if title else "משימת תמונה", complete=False, advice=advice_text)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("index"))

@app.route('/update/<int:todo_id>')
def update(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo:
        todo.complete = not todo.complete
        db.session.commit()
    return redirect(url_for("index"))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug)



