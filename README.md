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