from flask import Flask, render_template, request
import requests

app = Flask(__name__)

BOT_TOKEN = "7426449390:AAFvKcfiKArCsnd9_KpY6sETzK1VL4IJHtA"
CHAT_ID = "123456789"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        code = request.form["code"]
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": f"Code reçu depuis l'interface web :\n{code}"
        })
        return render_template("index.html", message="✅ Code envoyé au bot avec succès !")
    return render_template("index.html", message="")

if __name__ == "__main__":
    app.run(debug=True)

