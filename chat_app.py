#chat_app.py
from openai import OpenAI
import os
import subprocess
import time

# === Constants ===
OPENAI_API_KEY_ENV_VAR = "OPENAI_API_KEY"
GPT_MODEL = "gpt-4o-mini"
UNIT_TEST_PROMPT_SUFFIX = (
    "Also, please include running unit tests with asserts that check the logic of the program. "
    "Make sure to also check interesting edge cases. There should be at least 10 different unit tests. "
    "After all tests, print exactly this message (without quotes): 'All tests passed successfully.'"
)
SYSTEM_ROLE_MESSAGE = "You are a python programmer who can create a python program to solve a problem. Do not write any explanations, just show me the code itself."

# === Functions ===
def initialize_openai_client():
    api_key = os.getenv(OPENAI_API_KEY_ENV_VAR)
    return OpenAI(api_key=api_key)

def fetch_chatgpt_code(client, prompt, is_retry=False):
    try:
        if not is_retry:
            prompt_to_send = prompt + UNIT_TEST_PROMPT_SUFFIX
        else:
            prompt_to_send = prompt
            
        completion = client.chat.completions.create(
            model= GPT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_ROLE_MESSAGE},
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
        start_time = time.perf_counter()
        result = subprocess.run(['python', filename], capture_output=True, text=True)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        if result.returncode == 0:
            if result.stdout:
                print("Execution Output:\n", result.stdout)
                if "All tests passed successfully" in result.stdout:
                    return True, str(execution_time)
            return False, "Tests did not pass successfully"
        else:
            error_msg = result.stderr
            print("Execution Error:\n", error_msg)
            return False, error_msg
    except subprocess.CalledProcessError as e:
        error_msg = str(e)
        print(f"Error while executing the generated code: {error_msg}")
        return False, error_msg

def process_and_execute_code(client, prompt, filename, max_retries=5):
    attempt = 1
    last_error = None
    last_code = None
    original_prompt = prompt
    
    while attempt <= max_retries:
        if attempt > 1:
            print(f"\nAttempt {attempt}/{max_retries}")
            prompt = generate_retry_prompt(prompt, last_error, last_code)
            code_response = fetch_chatgpt_code(client, prompt, is_retry=True)
        else:
            code_response = fetch_chatgpt_code(client, prompt, is_retry=False)
        
        if code_response:
            output_code =  extract_code_from_response(code_response)
            last_code = output_code  
            print("\n=== Python Code ===")
            print(output_code)
            save_code_to_file(output_code, filename)
            success, message = execute_generated_code(filename)
            
            if success:
                original_time = float(message)
                new_time = float(optimize_code(original_prompt, original_time, filename))
                if new_time and new_time < original_time:
                    print(f"Code running time optimized! It now runs in {new_time:.2f} ms, while before it was {original_time:.2f} ms.")
                return True
            else:
                last_error = message
                if attempt < max_retries:
                    print(f"Error running generated code! Error: {message}. Trying again")
        else:
            last_error = "Failed to get response from GPT"
            if attempt < max_retries:
                print(f"Failed to fetch a valid response from GPT. Trying again")
        
        attempt += 1
    
    print("Code generation FAILED")
    return False

def generate_retry_prompt(original_prompt, last_error, last_code):
    return f"""
    The previous code had the following error:
    {last_error}
    Here was the last generated code that had the error:
    ```python
    {last_code}
    ```  
    Please fix the code and show the complete corrected version:
    Original request: {original_prompt}
    """

def extract_code_from_response(response):
    return response.replace("```python", "").replace("```", "").strip()

def optimize_code(original_prompt, original_time, filename):
    try:
        current_code = read_code_from_file(filename)
    except Exception as e:
        print(e)
        return original_time

    prompt_to_optimize = f"""
            The previous code had running time of {original_time} ms
            Please keep the same unit tests but create more efficient code that runs faster
            Here was the last generated code:
            ```python
            {current_code}
            ```  
            Original request: {original_prompt}
            """
    code_response = fetch_chatgpt_code(client, prompt_to_optimize)
    if code_response:
        output_code = extract_code_from_response(code_response)
        save_code_to_file(output_code, filename)
        success, message = execute_generated_code(filename)
        if success:
            return message
        else:
            return original_time

def read_code_from_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except Exception as e:
        raise Exception(f"Error reading file: {e}")

if __name__ == "__main__":
    prompt = "Create a python program that checks if a number is prime. Do not write any explanations, just show me the code itself."
    filename = "generatedcode.py"
    client = initialize_openai_client()
    process_and_execute_code(client, prompt, filename)