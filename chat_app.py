#chat_app.py
from openai import OpenAI
import os
import subprocess

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def fetch_chatgpt_code(prompt):
    try:
        unit_test_prompt =  "Also, please include running unit tests with asserts that check the logic of the program. Make sure to also check interesting edge cases. There should be at least 10 different unit tests. At the end of the test suite, print a message indicating that all tests passed successfully if no asserts fail."
        prompt_to_send = prompt + unit_test_prompt
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a python programer who can create a python program to solve a problem. Do not write any explanations, just show me the code itself."},
                {"role": "user", "content": prompt_to_send}
            ]
        )
        response = completion.choices[0].message.content
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_code_to_file(code, filename):
    try:
        with open(filename, "w") as file:
            file.write(code)
        print(f"Code saved to {filename}")
    except Exception as e:
        print(f"Failed to save code: {e}")

def execute_generated_code(filename):
    try:
        print("\n=== Executing Generated Code ===\n")
        result = subprocess.run(['python', filename], capture_output=True, text=True)
        if result.returncode == 0:
            if result.stdout:
                print("Execution Output:\n",result.stdout)  
            else:
                print("No output from the generated code.")
        else:
            print("Execution Error:\n", result.stderr)  
    except subprocess.CalledProcessError as e:
        print(f"Error while executing the generated code: {e}")

filename="generatedcode.py"
prompt = "Create a python program that checks if a number is prime. Do not write any explanations, just show me the code itself."
code_response = fetch_chatgpt_code(prompt)
if code_response:
    output_code = code_response.replace("```python", "").replace("```", "").strip()
    print("\n=== Python Code ===")
    print(output_code)
    save_code_to_file(output_code,filename)
    execute_generated_code(filename)
else:
    print("Failed to fetch a valid response from GPT.")