#chat_app.py
from openai import OpenAI
import os
import subprocess

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def fetch_chatgpt_code(prompt):
    try:
        unit_test_prompt = "Also, please include running unit tests with asserts that check the logic of the program. Make sure to also check interesting edge cases. There should be at least 10 different unit tests. After all tests, print exactly this message (without quotes): 'All tests passed successfully.'"
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
                if "All tests passed successfully" in result.stdout:
                    return True
            else:
                print("No output from the generated code.")
            return False
        else:
            print("Execution Error:\n", result.stderr)
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error while executing the generated code: {e}")
        return False

def process_and_execute_code(prompt, filename):
    code_response = fetch_chatgpt_code(prompt)
    if code_response:
        output_code = code_response.replace("```python", "").replace("```", "").strip()
        print("\n=== Python Code ===")
        print(output_code)
        save_code_to_file(output_code, filename)
        return execute_generated_code(filename)
    else:
        print("Failed to fetch a valid response from GPT.")
        return False

if __name__ == "__main__":
    prompt = "Create a python program that checks if a number is prime. Do not write any explanations, just show me the code itself."
    process_and_execute_code(prompt,"generatedcode.py")