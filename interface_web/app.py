from flask import Flask, render_template, request, jsonify
import requests
from flask_cors import CORS  # Import pour gérer le CORS

app = Flask(__name__)
CORS(app)  # Activer CORS pour toutes les routes

BOT_TOKEN = "7426449390:AAFvKcfiKArCsnd9_KpY6sETzK1VL4IJHtA"
CHAT_ID = "7726471914"  # ID Telegram de Shayma Dridi

def get_bot_info():
    """Récupérer les informations du bot depuis l'API Telegram"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return data.get("result", {})
    except Exception as e:
        print(f"Erreur lors de la récupération des informations du bot: {e}")
    
    return {"username": "votre_bot_username", "first_name": "Bot Python"}

@app.route("/", methods=["GET", "POST"])
def index():
    bot_info = get_bot_info()
    
    if request.method == "POST":
        code = request.form["code"]
        try:
            response = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
                "chat_id": CHAT_ID,
                "text": f"Code reçu depuis l'interface web :\n{code}"
            })
            
            # Vérifier si l'envoi a réussi
            if response.status_code == 200:
                return render_template("index.html", message="✅ Code envoyé au bot avec succès !", bot_info=bot_info)
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"description": "Erreur inconnue"}
                error_msg = error_data.get("description", "Erreur inconnue")
                
                if "chat not found" in error_msg:
                    error_msg = "Chat non trouvé. Assurez-vous d'avoir démarré une conversation avec le bot sur Telegram en envoyant /start"
                
                print(f"Erreur Telegram API: {response.status_code} - {response.text}")
                return render_template("index.html", message=f"❌ Erreur: {error_msg}", bot_info=bot_info)
        except Exception as e:
            print(f"Exception: {str(e)}")
            return render_template("index.html", message=f"❌ Erreur: {str(e)}", bot_info=bot_info)
    
    return render_template("index.html", message="", bot_info=bot_info)

# Route pour gérer les requêtes CORS preflight
@app.route("/", methods=["OPTIONS"])
def options():
    return "", 200

# Ajout d'un point de terminaison pour les tests
@app.route("/test", methods=["GET"])
def test():
    return jsonify({"status": "ok", "message": "API is working"})

if __name__ == "__main__":
    print("Starting web interface on http://127.0.0.1:5500")
    app.run(debug=True, port=5500)

