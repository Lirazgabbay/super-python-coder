#chat_app.py
from openai import OpenAI
import os
import subprocess

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def fetch_chatgpt_code(prompt, is_retry=False):
    try:
        if not is_retry:
            unit_test_prompt = "Also, please include running unit tests with asserts that check the logic of the program. Make sure to also check interesting edge cases. There should be at least 10 different unit tests. After all tests, print exactly this message (without quotes): 'All tests passed successfully.'"
            prompt_to_send = prompt + unit_test_prompt
        else:
            prompt_to_send = prompt
            
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a python programer who can create a python program to solve a problem. Do not write any explanations, just show me the code itself."},
                {"role": "user", "content": prompt_to_send}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error fetching response from GPT: {e}")
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
                print("Execution Output:\n", result.stdout)
                if "All tests passed successfully" in result.stdout:
                    return True, None
            return False, "Tests did not pass successfully"
        else:
            error_msg = result.stderr
            print("Execution Error:\n", error_msg)
            return False, error_msg
    except subprocess.CalledProcessError as e:
        error_msg = str(e)
        print(f"Error while executing the generated code: {error_msg}")
        return False, error_msg

def process_and_execute_code(prompt, filename, max_retries=5):
    attempt = 1
    last_error = None
    last_code = None
    original_prompt = prompt
    
    while attempt <= max_retries:
        if attempt > 1:
            print(f"\nAttempt {attempt}/{max_retries}")
            prompt = f"""
            The previous code had the following error:
            {last_error}
            Here was the last generated code that had the error:
            ```python
            {last_code}
            ```  
            Please fix the code and show the complete corrected version:
            Original request: {original_prompt}
            """
            code_response = fetch_chatgpt_code(prompt, is_retry=True)
        else:
            code_response = fetch_chatgpt_code(prompt, is_retry=False)
        
        if code_response:
            output_code = code_response.replace("```python", "").replace("```", "").strip()
            last_code = output_code  
            print("\n=== Python Code ===")
            print(output_code)
            save_code_to_file(output_code, filename)
            success, error = execute_generated_code(filename)
            
            if success:
                return True
            else:
                last_error = error
                if attempt < max_retries:
                    print(f"Error running generated code! Error: {error}. Trying again")
        else:
            last_error = "Failed to get response from GPT"
            if attempt < max_retries:
                print(f"Failed to fetch a valid response from GPT. Trying again")
        
        attempt += 1
    
    print("Code generation FAILED")
    return False

if __name__ == "__main__":
    prompt = "Create a python program that checks if a number is prime. Do not write any explanations, just show me the code itself."
    process_and_execute_code(prompt,"generatedcode.py")