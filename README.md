# 🤖 Bot Python Éducatif

Un bot Telegram multilingue qui offre des leçons Python, des quiz et un environnement d'exécution de code, accompagné d'une interface web moderne.

## ✨ Fonctionnalités

- 🌐 Support multilingue (français et anglais)
- 📚 Leçons Python interactives
- ❓ Quiz pour tester vos connaissances
- 💻 Exécution de code Python en temps réel
- 🖥️ Interface web élégante


2. Installez les dépendances:
   ```bash
   pip install -r requirements.txt
   ```

3. Assurez-vous d'installer flask-cors pour l'interface web:
   ```bash
   pip install flask-cors
   ```

## 📦 Dépendances requises en détail

Pour que le projet fonctionne correctement, vous devez installer toutes les dépendances nécessaires:

### Dépendances principales:
```bash
# Bot Telegram
pip install python-telegram-bot==22.0

# Interface web
pip install flask==2.3.3
pip install flask-cors==5.0.1
pip install requests==2.31.0
```

### Vérification des dépendances:
Pour vérifier que toutes les dépendances sont correctement installées:

```bash
# Vérifier la version de python-telegram-bot
pip show python-telegram-bot

# Vérifier la version de Flask
pip show flask

# Vérifier que Flask-CORS est installé
pip show flask-cors
```

Si vous obtenez une erreur lors de l'exécution du bot ou de l'interface web, assurez-vous que toutes les dépendances sont à jour:

```bash
pip install --upgrade -r requirements.txt
```

## 🔧 Démarrage sans problèmes

### Étape 1: Réinitialiser le webhook Telegram
Pour éviter les conflits avec d'autres instances du bot:

```bash
python reset_webhook.py
```

### Étape 2: Démarrer le bot Telegram (dans un terminal)
Utilisez clean_bot.py pour une meilleure gestion des erreurs:

```bash
python clean_bot.py
```

### Étape 3: Démarrer l'interface web (dans un autre terminal)
```bash
cd interface_web
python app.py
```

L'interface web sera accessible à l'adresse: [http://127.0.0.1:5500](http://127.0.0.1:5500)

## ✅ Comment activer et utiliser le bot

### Pour activer le bot sur Windows:

1. Ouvrez deux fenêtres PowerShell ou Command Prompt
2. Dans la première fenêtre:
   ```
   cd C:\chemin\vers\bot-python
   python reset_webhook.py
   python clean_bot.py
   ```
3. Dans la deuxième fenêtre:
   ```
   cd C:\chemin\vers\bot-python\interface_web
   python app.py
   ```
4. Ouvrez votre navigateur et accédez à: http://127.0.0.1:5500
5. Sur la page web, cliquez sur le bouton "Démarrer le bot sur Telegram"
6. Une fois sur Telegram, envoyez `/start` au bot pour l'activer
7. Le bot est maintenant prêt à être utilisé!

### Vérification que le bot est activé:
- Le terminal exécutant clean_bot.py devrait afficher des messages de connexion réussie
- Vous devriez recevoir une réponse du bot après avoir envoyé `/start`
- Dans l'interface web, vous pourrez envoyer du code qui sera exécuté par le bot

### Activation de l'interface web en détail:

Si vous rencontrez des problèmes avec l'interface web, suivez ces étapes supplémentaires:

1. Vérifiez que le serveur Flask fonctionne correctement:
   - Vous devriez voir `Running on http://127.0.0.1:5500` dans le terminal
   - Aucune erreur ne devrait être affichée

2. Si l'interface ne se charge pas:
   - Essayez d'accéder à http://localhost:5500 (alternative à 127.0.0.1)
   - Vérifiez qu'aucun autre service n'utilise le port 5500

3. Si vous voyez une erreur 405 (Method Not Allowed):
   - Assurez-vous que Flask-CORS est correctement installé: `pip install flask-cors`
   - Redémarrez l'application Flask

4. Si l'envoi de code ne fonctionne pas:
   - Assurez-vous d'avoir d'abord démarré une conversation avec le bot sur Telegram
   - Vérifiez les logs du terminal Flask pour voir les erreurs spécifiques

5. Pour forcer l'arrêt et redémarrer proprement:
   ```
   # Sur Windows
   taskkill /F /IM python.exe
   # Puis redémarrez les deux serveurs
   ```

## 📱 Utilisation du bot Telegram

1. Recherchez votre bot sur Telegram (utilisez le lien affiché dans l'interface web)
2. Démarrez une conversation en envoyant `/start`
3. Sélectionnez votre langue préférée (fr/en)
4. Utilisez le menu pour accéder aux:
   - Leçons (`/lesson`)
   - Quiz (`/quiz`)
   - Éditeur de code (`/code`)
   - Informations utilisateur (`/info`)

## 💡 Résolution des problèmes courants

### Erreur "Conflict: terminated by other getUpdates request"
```bash
# Arrêtez toutes les instances Python en cours d'exécution
taskkill /F /IM python.exe   # Windows
pkill -f python              # Linux/Mac

# Réinitialisez le webhook
python reset_webhook.py

# Redémarrez le bot
python clean_bot.py
```

### Erreur "chat not found" dans l'interface web
1. Assurez-vous d'avoir démarré une conversation avec le bot sur Telegram
2. Envoyez `/start` au bot
3. Réessayez d'envoyer du code depuis l'interface web

### L'interface web n'est pas accessible
1. Vérifiez que le serveur Flask est en cours d'exécution
2. Assurez-vous d'utiliser le bon port (5500)
3. Vérifiez les logs dans la console

## 📄 Structure du projet
```
bot-python/
├── bot.py                  # Bot principal original
├── clean_bot.py            # Version améliorée du bot avec gestion d'erreurs
├── reset_webhook.py        # Utilitaire pour réinitialiser le webhook
├── requirements.txt        # Dépendances du projet
├── utils/                  # Utilitaires
│   └── code_executor.py    # Exécuteur de code Python sécurisé
├── lessons/                # Contenu des leçons
│   ├── fr/                 # Leçons en français
│   └── en/                 # Leçons en anglais
├── quizzes/                # Quiz interactifs
│   ├── fr.json             # Quiz en français
│   └── en.json             # Quiz en anglais
└── interface_web/          # Interface web moderne
    ├── app.py              # Application Flask
    ├── templates/          # Templates HTML
    └── static/             # Fichiers CSS et assets
```

## 👨‍💻 Développé par
Dridi Shayma 

## 🚀 Guide de démarrage rapide

Si vous êtes pressé et voulez simplement démarrer le bot rapidement, suivez ces étapes:

```bash
# 1. Installer les dépendances
pip install python-telegram-bot==22.0 flask==2.3.3 flask-cors==5.0.1 requests==2.31.0

# 2. Réinitialiser le webhook
python reset_webhook.py

# 3. Démarrer le bot (dans une fenêtre)
python clean_bot.py

# 4. Démarrer l'interface web (dans une autre fenêtre)
cd interface_web
python app.py

# 5. Ouvrir http://127.0.0.1:5500 dans votre navigateur
# 6. Cliquer sur "Démarrer le bot sur Telegram"
# 7. Envoyer /start au bot sur Telegram
```

## 🔍 Dépannage avancé

### Problème: Aucune réponse du bot Telegram
```
1. Vérifiez que le token du bot est correct dans clean_bot.py
2. Assurez-vous que le bot est en cours d'exécution (terminal affichant "Application started")
3. Essayez de réinitialiser le webhook: python reset_webhook.py
4. Vérifiez la connexion internet
```

### Problème: Interface web inaccessible
```
1. Vérifiez le port utilisé dans app.py (devrait être 5500)
2. Assurez-vous qu'aucun pare-feu ne bloque le port
3. Essayez d'utiliser localhost au lieu de 127.0.0.1
4. Essayez de redémarrer l'application Flask
```

### Problème: Erreur Flask-CORS
```
1. Installez Flask-CORS: pip install flask-cors
2. Vérifiez que l'import est correct dans app.py
3. Assurez-vous que CORS(app) est appelé après la création de l'application
```

### Problème: Code Python non exécuté
```
1. Vérifiez que vous avez démarré une conversation avec le bot via /start
2. Assurez-vous que le bot et l'interface web utilisent le même token et ID
3. Vérifiez les logs dans les deux terminaux pour identifier l'erreur
```

Si vous rencontrez d'autres problèmes, n'hésitez pas à consulter la documentation officielle de [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) et [Flask](https://flask.palletsprojects.com/).