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
    
    reply_keyboard = [["fr", "en"]]
    await update.message.reply_text(
        f"Hello {user.first_name}! Choose language / Choisis ta langue :",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
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
    reply_keyboard = [["/lesson", "/quiz", "/code"], ["/info"]]
    await update.message.reply_text(
        "Choisis une option :",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MENU

async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    try:
        text = load_lesson(lang)
        await update.message.reply_text(text)
    except Exception as e:
        logger.error(f"Error loading lesson: {e}")
        await update.message.reply_text("Une erreur s'est produite lors du chargement de la leçon.")
    return MENU

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    try:
        quiz_data = load_quiz(lang)[0]
        context.user_data['quiz_answer'] = quiz_data['answer']
        reply_keyboard = [[o] for o in quiz_data['options']]
        await update.message.reply_text(
            quiz_data['question'],
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
    except Exception as e:
        logger.error(f"Error loading quiz: {e}")
        await update.message.reply_text("Une erreur s'est produite lors du chargement du quiz.")
    return QUIZ

async def check_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == context.user_data.get('quiz_answer'):
        await update.message.reply_text("✅ Bonne réponse !")
    else:
        await update.message.reply_text("❌ Mauvaise réponse.")
    return MENU

async def code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envoie-moi ton code Python. Exemple : print('Hello')")
    return CODE

async def execute_user_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        output = execute_code(update.message.text)
        await update.message.reply_text(f"Résultat :\n{output}")
    except Exception as e:
        logger.error(f"Error executing code: {e}")
        await update.message.reply_text(f"Erreur lors de l'exécution: {str(e)}")
    return MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Session terminée.")
    return ConversationHandler.END

async def error_handler(update, context):
    """Error handler for the bot."""
    logger.error(f"Error: {context.error}")

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
                await update.message.reply_text(f"✅ Code de l'interface Web exécuté:\n\n{output}")
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
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_language)],
            MENU: [
                CommandHandler("menu", menu),
                CommandHandler("lesson", lesson),
                CommandHandler("quiz", quiz),
                CommandHandler("code", code),
                CommandHandler("info", user_info),
                CommandHandler("add_user", add_user),
                CommandHandler("list_users", list_users),
                CommandHandler("add_shayma", add_shayma),
                MessageHandler(filters.Regex(r"Code reçu depuis l'interface web"), web_code)
            ],
            QUIZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_quiz)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, execute_user_code)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # Start the Bot with clean state
    logger.info("Starting bot...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main() 