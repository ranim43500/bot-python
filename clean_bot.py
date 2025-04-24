import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import json
import os
import time
import sys
from utils.code_executor import execute_code

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
LANGUAGE, MENU, QUIZ, CODE = range(4)

# User database file
USER_DB_FILE = "users.json"

# Load users database
def load_users():
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

# Save users database
def save_users(users):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# Initialize user database
users_db = load_users()

def load_lesson(lang):
    path = f"lessons/{lang}/lesson1.txt"
    return open(path, encoding='utf-8').read()

def load_quiz(lang):
    path = f"quizzes/{lang}.json"
    return json.load(open(path, encoding='utf-8'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Reset user data to avoid conflicts
    context.user_data.clear()
    
    # Save user information
    user = update.effective_user
    user_id = str(user.id)
    
    # Store user information
    users_db[user_id] = {
        "id": user_id,
        "first_name": user.first_name,
        "last_name": user.last_name if user.last_name else "",
        "username": user.username if user.username else "",
        "lang": context.user_data.get('lang', 'en'),
        "joined_date": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    save_users(users_db)
    
    # Log the user information
    logger.info(f"New user started: ID: {user_id}, Name: {user.first_name} {user.last_name or ''}")
    
    # Keyboard with language options
    keyboard = [["🇫🇷 Français (fr)", "🇬🇧 English (en)"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"👋 Hello {user.first_name}! Choose language / Choisis ta langue :",
        reply_markup=reply_markup
    )
    return LANGUAGE

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text
    context.user_data['lang'] = lang
    
    # Update user language preference in database
    user_id = str(update.effective_user.id)
    if user_id in users_db:
        users_db[user_id]["lang"] = lang
        save_users(users_db)
    
    await update.message.reply_text(f"Langue définie sur {lang}. Tape /menu pour commencer.")
    return MENU

async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in users_db:
        user_data = users_db[user_id]
        await update.message.reply_text(
            f"🔑 ID: {user_data['id']}\n"
            f"👤 First name: {user_data['first_name']}\n"
            f"👤 Last name: {user_data['last_name']}\n"
            f"🌐 Language: {user_data['lang']}\n"
            f"📅 Joined: {user_data['joined_date']}"
        )
    else:
        await update.message.reply_text("User information not found.")
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    lang = context.user_data.get('lang', 'en')
    
    # Messages selon la langue
    menu_text = {
        'fr': f"Bonjour {user_first_name}! Voici les options disponibles:",
        'en': f"Hello {user_first_name}! Here are the available options:"
    }
    
    options_text = {
        'fr': [
            "📚 Leçons - Apprenez Python pas à pas",
            "❓ Quiz - Testez vos connaissances", 
            "💻 Code - Exécutez du code Python",
            "ℹ️ Info - Voir vos informations",
            "🔄 Langue - Changer de langue"
        ],
        'en': [
            "📚 Lessons - Learn Python step by step", 
            "❓ Quiz - Test your knowledge", 
            "💻 Code - Execute Python code",
            "ℹ️ Info - View your information",
            "🔄 Language - Change language"
        ]
    }
    
    # Création des boutons avec keyboard plus grand
    keyboard = [
        [options_text[lang][0]],
        [options_text[lang][1]],
        [options_text[lang][2]],
        [options_text[lang][3]],
        [options_text[lang][4]]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(menu_text[lang], reply_markup=reply_markup)
    return MENU

async def handle_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les choix à partir du menu textuel"""
    text = update.message.text
    lang = context.user_data.get('lang', 'en')
    
    # Vérifier quelle option a été sélectionnée
    if "📚" in text:
        return await lesson(update, context)
    elif "❓" in text:
        return await quiz(update, context)
    elif "💻" in text:
        return await code(update, context)
    elif "ℹ️" in text:
        return await user_info(update, context)
    elif "🔄" in text:
        return await change_language(update, context)
    else:
        # Message d'erreur selon la langue
        error_msg = {
            'fr': "Option non reconnue. Veuillez choisir une option du menu.",
            'en': "Unrecognized option. Please choose an option from the menu."
        }
        await update.message.reply_text(error_msg[lang])
        return await menu(update, context)

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Permet de changer la langue"""
    # Options de langue
    keyboard = [["🇫🇷 Français (fr)", "🇬🇧 English (en)"], ["🔙 Retour / Back"]]
    
    lang = context.user_data.get('lang', 'en')
    lang_text = {
        'fr': "Choisissez votre langue:",
        'en': "Choose your language:"
    }
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(lang_text[lang], reply_markup=reply_markup)
    return LANGUAGE

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Définit la langue de l'utilisateur"""
    text = update.message.text
    
    if "🔙 Retour / Back" in text:
        return await menu(update, context)
    
    # Extraire le code de langue (fr/en)
    if "fr" in text.lower():
        lang = "fr" 
    elif "en" in text.lower():
        lang = "en"
    else:
        # En cas d'entrée non reconnue, on reste en anglais par défaut
        lang = "en"
    
    context.user_data['lang'] = lang
    
    # Mettre à jour le profil utilisateur dans la base de données
    user_id = str(update.effective_user.id)
    if user_id in users_db:
        users_db[user_id]["lang"] = lang
        save_users(users_db)
    
    # Messages selon la langue
    success_msg = {
        'fr': f"✅ Langue définie sur français. Tapez /menu pour continuer.",
        'en': f"✅ Language set to English. Type /menu to continue."
    }
    
    await update.message.reply_text(success_msg[lang])
    return await menu(update, context)

async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche les leçons disponibles"""
    lang = context.user_data.get('lang', 'en')
    
    # Options de leçons
    lesson_text = {
        'fr': "Choisissez une leçon:",
        'en': "Choose a lesson:"
    }
    
    lessons = {
        'fr': [
            "📖 Leçon 1: Bases de Python",
            "📖 Leçon 2: Variables et Types",
            "📖 Leçon 3: Conditions",
            "📖 Leçon 4: Boucles",
        ],
        'en': [
            "📖 Lesson 1: Python Basics",
            "📖 Lesson 2: Variables and Types",
            "📖 Lesson 3: Conditions",
            "📖 Lesson 4: Loops",
        ]
    }
    
    # Création du clavier avec les leçons disponibles
    keyboard = [[lesson] for lesson in lessons[lang]]
    keyboard.append(["🔙 Retour au Menu"])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(lesson_text[lang], reply_markup=reply_markup)
    return LESSON_SELECTION

async def show_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche une leçon spécifique"""
    text = update.message.text
    lang = context.user_data.get('lang', 'en')
    
    if "🔙 Retour" in text:
        return await menu(update, context)
    
    # Extraire le numéro de leçon (1, 2, 3...)
    lesson_num = None
    for i in range(1, 5):  # 4 leçons disponibles pour l'instant
        if f"eçon {i}" in text or f"esson {i}" in text:
            lesson_num = i
            break
    
    if lesson_num is None:
        # Message d'erreur selon la langue
        error_msg = {
            'fr': "Leçon non reconnue. Veuillez choisir une leçon disponible.",
            'en': "Unrecognized lesson. Please choose an available lesson."
        }
        await update.message.reply_text(error_msg[lang])
        return await lesson(update, context)
    
    try:
        # Charger le contenu de la leçon
        lesson_path = f"lessons/{lang}/lesson{lesson_num}.txt"
        if os.path.exists(lesson_path):
            lesson_content = open(lesson_path, encoding='utf-8').read()
        else:
            # Si le fichier n'existe pas, message temporaire
            back_text = "🔙 Retour au Menu" if lang == "fr" else "🔙 Back to Menu"
            
            if lang == 'fr':
                lesson_content = f"Leçon {lesson_num} en cours de développement.\nRevenez bientôt!"
            else:
                lesson_content = f"Lesson {lesson_num} under development.\nCheck back soon!"
            
            # Ajouter bouton de retour
            keyboard = [[back_text]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(lesson_content, reply_markup=reply_markup)
            return LESSON_SELECTION
        
        # Diviser le contenu en plusieurs messages si nécessaire
        max_length = 4000  # Limite de taille des messages Telegram
        
        if len(lesson_content) <= max_length:
            # Ajouter bouton de retour
            back_text = "🔙 Retour au Menu" if lang == "fr" else "🔙 Back to Menu"
            keyboard = [[back_text]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(lesson_content, reply_markup=reply_markup)
        else:
            # Diviser en plusieurs messages
            chunks = [lesson_content[i:i+max_length] 
                     for i in range(0, len(lesson_content), max_length)]
            
            for i, chunk in enumerate(chunks):
                if i == len(chunks) - 1:  # Dernier message
                    back_text = "🔙 Retour au Menu" if lang == "fr" else "🔙 Back to Menu"
                    keyboard = [[back_text]]
                    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                    await update.message.reply_text(chunk, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(chunk)
        
        return LESSON_SELECTION
        
    except Exception as e:
        logger.error(f"Error showing lesson: {e}")
        
        # Message d'erreur selon la langue
        error_msg = {
            'fr': f"Erreur lors du chargement de la leçon: {str(e)}",
            'en': f"Error loading lesson: {str(e)}"
        }
        
        await update.message.reply_text(error_msg[lang])
        return await lesson(update, context)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    
    try:
        # Chargement des quiz
        quiz_data = load_quiz(lang)
        
        if not quiz_data:
            # Message d'erreur si pas de quiz disponible
            error_msg = {
                'fr': "Aucun quiz disponible pour le moment.",
                'en': "No quiz available at the moment."
            }
            await update.message.reply_text(error_msg[lang])
            return await menu(update, context)
        
        # Choisir un quiz aléatoire
        import random
        quiz_item = random.choice(quiz_data)
        
        context.user_data['quiz_answer'] = quiz_item['answer']
        context.user_data['quiz_explanation'] = quiz_item.get('explanation', '')
        
        # Créer les options
        options = quiz_item['options']
        keyboard = [[option] for option in options]
        
        # Ajouter option de retour
        back_text = "🔙 Retour au Menu" if lang == "fr" else "🔙 Back to Menu"
        keyboard.append([back_text])
        
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        
        # Message selon la langue
        quiz_intro = {
            'fr': "📝 Quiz: ",
            'en': "📝 Quiz: "
        }
        
        await update.message.reply_text(
            f"{quiz_intro[lang]}{quiz_item['question']}",
            reply_markup=reply_markup
        )
        return QUIZ
        
    except Exception as e:
        logger.error(f"Error loading quiz: {e}")
        
        # Message d'erreur selon la langue
        error_msg = {
            'fr': f"Erreur lors du chargement du quiz: {str(e)}",
            'en': f"Error loading quiz: {str(e)}"
        }
        
        await update.message.reply_text(error_msg[lang])
        return await menu(update, context)

async def check_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    lang = context.user_data.get('lang', 'en')
    
    if "🔙 Retour" in text or "Back" in text:
        return await menu(update, context)
    
    correct_answer = context.user_data.get('quiz_answer', '')
    explanation = context.user_data.get('quiz_explanation', '')
    
    if text == correct_answer:
        # Messages selon la langue
        success_msg = {
            'fr': "✅ Bonne réponse !",
            'en': "✅ Correct answer!"
        }
        
        # Ajouter l'explication si disponible
        response = success_msg[lang]
        if explanation:
            expl_text = {
                'fr': "\n\nExplication: ",
                'en': "\n\nExplanation: "
            }
            response += f"{expl_text[lang]}{explanation}"
        
        # Options après la réponse
        next_quiz_text = "❓ Autre Quiz" if lang == "fr" else "❓ Another Quiz"
        menu_text = "🔙 Retour au Menu" if lang == "fr" else "🔙 Back to Menu"
        
        keyboard = [[next_quiz_text], [menu_text]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(response, reply_markup=reply_markup)
        return QUIZ_RESULT
        
    else:
        # Messages selon la langue
        failure_msg = {
            'fr': f"❌ Mauvaise réponse. La bonne réponse était: {correct_answer}",
            'en': f"❌ Wrong answer. The correct answer was: {correct_answer}"
        }
        
        # Ajouter l'explication si disponible
        response = failure_msg[lang]
        if explanation:
            expl_text = {
                'fr': "\n\nExplication: ",
                'en': "\n\nExplanation: "
            }
            response += f"{expl_text[lang]}{explanation}"
        
        # Options après la réponse
        next_quiz_text = "❓ Autre Quiz" if lang == "fr" else "❓ Another Quiz"
        menu_text = "🔙 Retour au Menu" if lang == "fr" else "🔙 Back to Menu"
        
        keyboard = [[next_quiz_text], [menu_text]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(response, reply_markup=reply_markup)
        return QUIZ_RESULT

async def handle_quiz_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère la suite après un quiz (autre quiz ou retour au menu)"""
    text = update.message.text
    
    if "Autre Quiz" in text or "Another Quiz" in text:
        return await quiz(update, context)
    else:
        return await menu(update, context)

async def code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    
    # Messages selon la langue
    code_text = {
        'fr': "💻 Envoyez-moi votre code Python et je l'exécuterai pour vous.\n\nExemple:\n```\nprint('Bonjour!')\nfor i in range(5):\n    print(i)\n```",
        'en': "💻 Send me your Python code and I'll execute it for you.\n\nExample:\n```\nprint('Hello!')\nfor i in range(5):\n    print(i)\n```"
    }
    
    # Option de retour
    back_text = "🔙 Retour au Menu" if lang == "fr" else "🔙 Back to Menu"
    keyboard = [[back_text]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(code_text[lang], reply_markup=reply_markup)
    return CODE

async def execute_user_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    lang = context.user_data.get('lang', 'en')
    
    if "🔙 Retour" in text or "Back" in text:
        return await menu(update, context)
    
    try:
        # Exécuter le code
        output = execute_code(text)
        
        # Messages selon la langue
        result_text = {
            'fr': "✅ Résultat de l'exécution:",
            'en': "✅ Execution result:"
        }
        
        # Option après l'exécution
        run_again_text = "🔄 Exécuter autre code" if lang == "fr" else "🔄 Run more code"
        menu_text = "🔙 Retour au Menu" if lang == "fr" else "🔙 Back to Menu"
        
        keyboard = [[run_again_text], [menu_text]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(f"{result_text[lang]}\n\n```\n{output}\n```", reply_markup=reply_markup)
        return CODE_RESULT
        
    except Exception as e:
        logger.error(f"Error executing code: {e}")
        
        # Messages d'erreur selon la langue
        error_msg = {
            'fr': f"❌ Erreur lors de l'exécution du code: {str(e)}",
            'en': f"❌ Error executing code: {str(e)}"
        }
        
        # Option après l'erreur
        run_again_text = "🔄 Réessayer" if lang == "fr" else "🔄 Try again"
        menu_text = "🔙 Retour au Menu" if lang == "fr" else "🔙 Back to Menu"
        
        keyboard = [[run_again_text], [menu_text]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(error_msg[lang], reply_markup=reply_markup)
        return CODE_RESULT

async def handle_code_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère la suite après l'exécution de code (autre code ou retour au menu)"""
    text = update.message.text
    
    if "Exécuter autre" in text or "Run more" in text or "Réessayer" in text or "Try again" in text:
        return await code(update, context)
    else:
        return await menu(update, context)

async def error_handler(update, context):
    """Error handler for the bot."""
    error = context.error
    logger.error(f"Error: {context.error}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Annule la conversation et retourne à l'état initial."""
    lang = context.user_data.get('lang', 'en')
    
    # Messages selon la langue
    cancel_text = {
        'fr': "Session terminée. Envoyez /start pour recommencer.",
        'en': "Session ended. Send /start to begin again."
    }
    
    await update.message.reply_text(cancel_text[lang])
    return ConversationHandler.END

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only admins should be able to use this command
    admin_ids = ['7726471914']  # List of admin user IDs
    
    # Check if the command user is an admin
    user_id = str(update.effective_user.id)
    if user_id not in admin_ids:
        await update.message.reply_text("Sorry, you don't have permission to use this command.")
        return MENU
    
    # Parse the arguments: /add_user id first_name last_name lang
    args = context.args
    if len(args) < 4:
        await update.message.reply_text("Usage: /add_user <id> <first_name> <last_name> <lang>")
        return MENU
        
    new_id, first_name, last_name, lang = args[0], args[1], args[2], args[3]
    
    # Add the user to the database
    users_db[new_id] = {
        "id": new_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": "",
        "lang": lang,
        "joined_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "added_manually": True
    }
    save_users(users_db)
    
    logger.info(f"Manually added user: ID: {new_id}, Name: {first_name} {last_name}, Lang: {lang}")
    await update.message.reply_text(f"User added: ID: {new_id}, Name: {first_name} {last_name}, Lang: {lang}")
    return MENU

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only admins should be able to use this command
    admin_ids = ['7726471914']  # List of admin user IDs
    
    # Check if the command user is an admin
    user_id = str(update.effective_user.id)
    if user_id not in admin_ids:
        await update.message.reply_text("Sorry, you don't have permission to use this command.")
        return MENU
    
    # List all users
    if len(users_db) == 0:
        await update.message.reply_text("No users in database.")
    else:
        user_list = "Users in database:\n\n"
        for uid, user_data in users_db.items():
            user_list += f"🔑 ID: {user_data['id']}\n"
            user_list += f"👤 Name: {user_data['first_name']} {user_data['last_name']}\n"
            user_list += f"🌐 Lang: {user_data['lang']}\n"
            user_list += f"📅 Joined: {user_data['joined_date']}\n\n"
        
        await update.message.reply_text(user_list)
    return MENU

async def add_shayma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adds the specific user Shayma Dridi with ID 7726471914."""
    # Add the specific user to the database
    new_id = "7726471914"
    first_name = "Dridi"
    last_name = "Shayma"
    lang = "en"
    
    # Add the user to the database
    users_db[new_id] = {
        "id": new_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": "",
        "lang": lang,
        "joined_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "added_manually": True
    }
    save_users(users_db)
    
    logger.info(f"Added specific user: ID: {new_id}, Name: {first_name} {last_name}, Lang: {lang}")
    await update.message.reply_text(f"✅ Added specific user: ID: {new_id}, Name: {first_name} {last_name}, Lang: {lang}")
    return MENU

async def web_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Traite les messages de code provenant de l'interface web"""
    if "Code reçu depuis l'interface web" in update.message.text:
        # Extraction du code Python du message
        code_lines = update.message.text.split('\n')
        if len(code_lines) > 1:
            # Supprime la première ligne qui contient le préfixe
            code = '\n'.join(code_lines[1:])
            
            try:
                output = execute_code(code)
                lang = context.user_data.get('lang', 'en')
                
                # Options après l'exécution
                run_again_text = "🔄 Exécuter autre code" if lang == "fr" else "🔄 Run more code"
                menu_text = "🔙 Retour au Menu" if lang == "fr" else "🔙 Back to Menu"
                
                keyboard = [[run_again_text], [menu_text]]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                
                await update.message.reply_text(f"✅ Code de l'interface Web exécuté:\n\n```\n{output}\n```", 
                                              reply_markup=reply_markup)
                return CODE_RESULT
            except Exception as e:
                logger.error(f"Error executing web code: {e}")
                await update.message.reply_text(f"❌ Erreur lors de l'exécution du code web: {str(e)}")
        else:
            await update.message.reply_text("❌ Aucun code Python à exécuter")
    return MENU

def main():
    # Create the Application
    token = "7426449390:AAFvKcfiKArCsnd9_KpY6sETzK1VL4IJHtA"  
    application = Application.builder().token(token).build()
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Définir les états globalement pour qu'ils soient disponibles partout
    global LANGUAGE, MENU, QUIZ, CODE, LESSON_SELECTION, QUIZ_RESULT, CODE_RESULT
    LANGUAGE, MENU, QUIZ, CODE = range(4)
    LESSON_SELECTION = 4
    QUIZ_RESULT = 5
    CODE_RESULT = 6
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_language),
                CommandHandler("start", start)  # Permettre de redémarrer à tout moment
            ],
            MENU: [
                CommandHandler("menu", menu),
                CommandHandler("lesson", lesson),
                CommandHandler("quiz", quiz),
                CommandHandler("code", code),
                CommandHandler("info", user_info),
                CommandHandler("add_user", add_user),
                CommandHandler("list_users", list_users),
                CommandHandler("add_shayma", add_shayma),
                MessageHandler(filters.Regex(r"Code reçu depuis l'interface web"), web_code),
                # Gestion des options textuelles du menu
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_choice)
            ],
            LESSON_SELECTION: [
                CommandHandler("menu", menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, show_lesson)
            ],
            QUIZ: [
                CommandHandler("menu", menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, check_quiz)
            ],
            QUIZ_RESULT: [
                CommandHandler("menu", menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quiz_result)
            ],
            CODE: [
                CommandHandler("menu", menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, execute_user_code)
            ],
            CODE_RESULT: [
                CommandHandler("menu", menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code_result)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start)
        ],
        allow_reentry=True,
        name="main_conversation"
    )
    
    application.add_handler(conv_handler)
    
    # Handler pour les commandes générales disponibles à tout moment
    application.add_handler(MessageHandler(
        filters.COMMAND & ~filters.Regex(r"^/(start|menu|lesson|quiz|code|info|cancel)$"),
        lambda update, context: update.message.reply_text("Commande non reconnue. Essayez /menu ou /start.")
    ))
    
    # Start the Bot with clean state
    logger.info("Starting bot...")
    try:
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Critical error starting bot: {e}")
        # Retry with a delay if needed
        time.sleep(5)
        logger.info("Attempting to restart...")
        application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main() 