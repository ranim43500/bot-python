import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import json
import os
from utils.code_executor import execute_code

logging.basicConfig(level=logging.INFO)

LANGUAGE, MENU, QUIZ, CODE = range(4)

user_data_store = {}

def load_lesson(lang):
    path = f"lessons/{lang}/lesson1.txt"
    return open(path, encoding='utf-8').read()

def load_quiz(lang):
    path = f"quizzes/{lang}.json"
    return json.load(open(path, encoding='utf-8'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["fr", "en"]]
    await update.message.reply_text("Choose language / Choisis ta langue :", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return LANGUAGE

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text
    context.user_data['lang'] = lang
    await update.message.reply_text(f"Langue définie sur {lang}. Tape /menu pour commencer.")
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["/lesson", "/quiz", "/code"]]
    await update.message.reply_text("Choisis une option :", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return MENU

async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    text = load_lesson(lang)
    await update.message.reply_text(text)
    return MENU

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    quiz_data = load_quiz(lang)[0]
    context.user_data['quiz_answer'] = quiz_data['answer']
    reply_keyboard = [[o] for o in quiz_data['options']]
    await update.message.reply_text(quiz_data['question'], reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
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
    output = execute_code(update.message.text)
    await update.message.reply_text(f"Résultat :\n{output}")
    return MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Session terminée.")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token("7426449390:AAFvKcfiKArCsnd9_KpY6sETzK1VL4IJHtA").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_language)],
            MENU: [CommandHandler("menu", menu), CommandHandler("lesson", lesson), CommandHandler("quiz", quiz), CommandHandler("code", code)],
            QUIZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_quiz)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, execute_user_code)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()
