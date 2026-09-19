import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("8640621902:AAHIFGQKcVHvt6wKUPy389GKEIhh3rVrBp4")
GEMINI_API_KEY = os.environ.get("AQ.Ab8RN6L43PuBCRazjYamn6j3eH7c1ASOcUE5gy8APJPgaf_lDg")

ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Updated prompt that handles unknown/unclear words safely
SYSTEM_INSTRUCTION = """
You are an expert Khmer proofreader and grammar checker.
When analyzing Khmer text:
1. If you encounter unrecognized, misspelled, or slang words, try your best to infer their meaning from context and suggest the correct standard Khmer spelling.
2. If a word is completely unrecognizable or ambiguous, explicitly list it under "Unrecognized Words" and ask the user to clarify.
3. Never refuse to respond or output empty text. Always return a structured response.

Format your output strictly as:
1. âŒ **áž–áž¶áž€áŸ’áž™ážáž»ážŸ/áž˜áž·áž“ážŸáŸ’áž‚áž¶áž›áŸ‹ (Mistakes/Unrecognized):** List words and proposed fixes.
2. âœ… **áž›áŸ’áž”áŸ‡ážáŸ’ážšáž¹áž˜ážáŸ’ážšáž¼ážœ (Corrected Sentence):** Complete corrected sentence.
3. ðŸ’¡ **áž€áž¶ážšáž–áž“áŸ’áž™áž›áŸ‹ (Explanation):** Brief explanation in Khmer.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ážŸáž½ážŸáŸ’ážáž¸! áž•áŸ’áž‰áž¾ážŸáž¶ážšáž‡áž¶áž—áž¶ážŸáž¶ážáŸ’áž˜áŸ‚ážšáž˜áž€áž‘áž¸áž“áŸáŸ‡ ážáŸ’áž‰áž»áŸ†áž“áž¹áž„áž‡áž½áž™áž–áž·áž“áž·ážáŸ’áž™áž¢áž€áŸ’ážážšáž¶ážœáž·ážšáž»áž‘áŸ’áž’ áž“áž·áž„ážœáŸáž™áŸ’áž™áž¶áž€ážšážŽáŸáž‡áž¼áž“áŸ”")

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
        
        # Safely extract text to avoid crashes if output is blocked or empty
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("áž˜áž·áž“áž¢áž¶áž…áž–áž·áž“áž·ážáŸ’áž™áž–áž¶áž€áŸ’áž™áž“áŸáŸ‡áž”áž¶áž“áž‘áŸáŸ” ážŸáž¼áž˜áž–áŸ’áž™áž¶áž™áž¶áž˜ážŸážšážŸáŸážšáž¡áž¾áž„ážœáž·áž‰ážŠáŸ„áž™áž”áž“áŸ’ážáŸ‚áž˜ážŠáž€ážƒáŸ’áž›áž¶ áž¬áž–áž·áž“áž·ážáŸ’áž™áž–áž¶áž€áŸ’áž™áž–áž·áž”áž¶áž€áŸ—áŸ”")
            
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        await update.message.reply_text("áž˜áž¶áž“áž”áž‰áŸ’áž áž¶áž€áŸ’áž“áž»áž„áž€áž¶ážšáž–áž·áž“áž·ážáŸ’áž™áž¢ážáŸ’ážáž”áž‘áž“áŸáŸ‡áŸ” ážŸáž¼áž˜áž–áŸ’áž™áž¶áž™áž¶áž˜ážŸážšážŸáŸážšáž–áž¶áž€áŸ’áž™áž²áŸ’áž™áž…áŸ’áž”áž¶ážŸáŸ‹áž‡áž¶áž„áž˜áž»áž“áž”áž“áŸ’ážáž·áž…áŸ”")

def main():
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        raise ValueError("Missing TELEGRAM_TOKEN or GEMINI_API_KEY environment variables.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_khmer_text))
    
    app.run_polling()

if __name__ == '__main__':
    main()