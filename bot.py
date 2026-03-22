import os
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from rag_engine import RAGEngine
from openrouter_engine import OpenRouterEngine

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

rag = RAGEngine()
ai_brain = OpenRouterEngine(api_key=OPENROUTER_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the Zomato Hybrid Assistant!\nUse /help to see commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *Zomato AI Assistant Help*\n\n"
        "✨ *Option A: Policy Search*\n"
        "Use `/ask <question>`\n\n"
        "🖼️ *Option B: Image Analysis*\n"
        "Use /image or simply Upload a photo to get a description."
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Please upload a photo to analyze it!")

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    
    
    if not query:
        await update.message.reply_text("Usage: /ask <your question>")
        return
    
    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    
    user_id = update.message.from_user.id
    chunks = rag.retrieve(query)
    answer = ai_brain.get_answer(user_id, query, chunks)
    
    source_names = list(set([c['source'] for c in chunks]))
    sources_text = ", ".join(source_names) if source_names else "Internal Knowledge"
    
    
    final_text = f"{answer}\n\n<b>Sources:</b> {sources_text}"
    
    try:
        await update.message.reply_text(final_text, parse_mode="HTML")
    except Exception:
        
        await update.message.reply_text(f"{answer}\n\nSources: {sources_text}")

async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles image uploads and saves to session memory."""
    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    
    user_id = update.message.from_user.id 
    photo_file = await update.message.photo[-1].get_file()
    temp_path = "vision_temp.jpg"
    await photo_file.download_to_drive(temp_path)
    
    description = ai_brain.get_image_description(user_id, temp_path)
    
    await update.message.reply_text(f"🖼️ **Analysis Result:**\n\n{description}", parse_mode="HTML")
    
    if os.path.exists(temp_path):
        os.remove(temp_path)

async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /summarize: Condenses the recent chat and vision results."""
    uid = update.message.from_user.id
    
   
    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    
    
    summary_text = ai_brain.summarize_chat(uid)
    
   
    await update.message.reply_text(f"📝 <b>Recent Activity Summary:</b>\n\n{summary_text}", parse_mode="HTML")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("image", image_command)) 
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("summarize", summarize)) 
    
    app.add_handler(MessageHandler(filters.PHOTO, image_handler))
    
    print("Hybrid Bot is now live ...")
    app.run_polling()