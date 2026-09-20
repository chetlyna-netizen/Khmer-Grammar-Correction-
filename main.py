import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Your requested token and API key
TELEGRAM_TOKEN = "8640621902:AAHIFGQKcVHvt6wKUPy389GKEIhh3rVrBp4"
GEMINI_API_KEY = "AQ.Ab8RN6L43PuBCRazjYamn6j3eH7c1ASOcUE5gy8APJPgaf_lDg"

ai_client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
You are an expert Khmer proofreader and grammar checker.
When analyzing Khmer text:
1. If you encounter unrecognized, misspelled, or slang words, try your best to infer their meaning from context and suggest the correct standard Khmer spelling.
2. If a word is completely unrecognizable or ambiguous, explicitly list it under "Unrecognized Words" and ask the user to clarify.
3. Never refuse to respond or output empty text. Always return a structured response.

Format your output strictly as:
1. ❌ **ខុស/មិនស្គាល់ (Mistakes/Unrecognized):** List words and proposed fixes.
2. ✅ **លទ្ធផលត្រឹមត្រូវ (Corrected Sentence):** Complete corrected sentence.
3. 💡 **ការពន្យល់ (Explanation):** Brief explanation in Khmer.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("សួស្តី! ខ្ញុំជាជំនួយការបញ្ជាក់និងកែសម្រួលអក្ខរក្រម និងវេយ្យាករណ៍ភាសាខ្មែររបស់អ្នក។")

async def handle_khmer_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    prompt = f"Please analyze and correct the following Khmer text:\n\n{user_text}"
    
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"system_instruction": SYSTEM_INSTRUCTION}
        )
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("មិនអាចពិនិត្យពាក្យនេះបានទេ! សូមព្យាយាមផ្ញើឃ្លា ឬប្រយោគផ្សេង។")
            
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        await update.message.reply_text("មានបញ្ហាក្នុងការតភ្ជាប់ទៅកាន់ប្រព័ន្ធ AI។ សូមព្យាយាមម្ដងទៀត។")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_khmer_text))
    
    # Render deployment settings
    PORT = int(os.environ.get("PORT", 10000))
    RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
    
    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/{TELEGRAM_TOKEN}"
        logging.info(f"Starting webhook server on port {PORT}...")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=webhook_url
        )
    else:
        # Fallback for local testing
        print("Running locally with polling...")
        app.run_polling()

if __name__ == '__main__':
    main()
