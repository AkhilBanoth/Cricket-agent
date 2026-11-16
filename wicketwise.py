import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

AI_NAME = "WicketWise"
DOC_PATH = "cricket_knowledge.txt"
MODEL = "gemini-3.5-flash"
FALLBACK = "I couldn't find that in my cricket records."


def load_document(path):
    if not os.path.exists(path):
        sys.exit(f"Document not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        sys.exit("The document is empty.")
    return text


def build_system_prompt(document):
    return f"""You are {AI_NAME}, a friendly cricket assistant.

RULES:
1. Answer ONLY using the information inside the DOCUMENT below.
2. Do NOT use outside knowledge, guesses, or assumptions, even if you know the answer.
3. If the answer is not in the DOCUMENT, reply exactly: "{FALLBACK}"
4. If the question is not about cricket or the document, politely say you only answer questions from your cricket records.
5. Keep answers short, clear, and in a cheerful tone. You may do simple arithmetic on numbers from the DOCUMENT.

DOCUMENT:
\"\"\"
{document}
\"\"\"
"""


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY not found. Add it to your .env file.")

    document = load_document(DOC_PATH)
    client = genai.Client(api_key=api_key)

    chat = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(document),
            temperature=0.2,
        ),
    )

    print(f"\nWelcome to {AI_NAME}! Ask me about cricket. Type 'exit' to quit.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{AI_NAME}: Stumps! See you next time.")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit", "bye"}:
            print(f"{AI_NAME}: Stumps! See you next time.")
            break
        try:
            response = chat.send_message(question)
            print(f"{AI_NAME}: {response.text}\n")
        except Exception as e:
        
            print(f"{AI_NAME}: Something went wrong ({e})\n")


if __name__ == "__main__":
    main()
