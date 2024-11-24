#chat_app.py
from openai import OpenAI
import os

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def fetch_chatgpt_code(prompt):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a python programer who can create a python program to solve a problem. Do not write any explanations, just show me the code itself."},
                {"role": "user", "content": prompt}
            ]
        )
        response = completion.choices[0].message.content
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

prompt = "Create a python program that checks if a number is prime. Do not write any explanations, just show me the code itself."
code_response = fetch_chatgpt_code(prompt)
if code_response:
    print("\n=== Python Code ===")
    print(code_response)
else:
    print("Failed to fetch a valid response from GPT.")
