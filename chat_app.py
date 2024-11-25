#chat_app.py
from openai import OpenAI
import os
import subprocess
import time
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# === Constants ===
OPENAI_API_KEY_ENV_VAR = "OPENAI_API_KEY"
GPT_MODEL = "gpt-4o-mini"
UNIT_TEST_PROMPT = (
    "Also, please include running unit tests with asserts that check the logic of the program. "
    "Make sure to also check interesting edge cases. There should be at least 10 different unit tests. "
    "After all tests, print exactly this message (without quotes): 'All tests passed successfully.'"
)
SYSTEM_ROLE_MESSAGE = "You are a python programmer who can create a python program to solve a problem. Do not write any explanations, just show me the code itself."
MAX_LINT_ATTEMPTS = 3

# === Functions ===
def initialize_openai_client():
    api_key = os.getenv(OPENAI_API_KEY_ENV_VAR)
    return OpenAI(api_key=api_key)

def fetch_chatgpt_code(client, prompt, is_retry=False):
    try:
        if not is_retry:
            prompt_to_send = prompt + UNIT_TEST_PROMPT
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
        print(Fore.RED + f"Error fetching response from GPT: {e}")
        return None

def save_code_to_file(code, filename):
    print(f"\n{Style.BRIGHT}=== Saving Code ==={Style.RESET_ALL}")
    try:
        with open(filename, "w") as file:
            file.write(code)
        print(Fore.GREEN + f"Code saved to {filename}")
    except Exception as e:
        print(Fore.RED + f"Failed to save code: {e}")

def execute_generated_code(filename):
    try:
        print(f"\n{Style.BRIGHT}=== Executing Generated Code ==={Style.RESET_ALL}")
        start_time = time.perf_counter()
        result = subprocess.run(['python', filename], capture_output=True, text=True)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        if result.returncode == 0:
            if result.stdout:
                print(f"\n{Style.BRIGHT}{Fore.CYAN}=== Execution Output ==={Style.RESET_ALL}")
                print(f"{Fore.GREEN}{result.stdout}{Style.RESET_ALL}")
                if "All tests passed successfully" in result.stdout:
                    return True, str(execution_time)
            return False, "Tests did not pass successfully"
        else:
            error_msg = result.stderr
            print(f"{Fore.RED}Execution Error:{Style.RESET_ALL}\n{error_msg}")
            return False, error_msg
    except subprocess.CalledProcessError as e:
        error_msg = str(e)
        print(f"Error while executing the generated code: {error_msg}")
        return False, error_msg

def process_and_execute_code(client, prompt, filename, max_retries=5):
    print(f"\n{Style.BRIGHT}=== Processing Code ==={Style.RESET_ALL}")
    attempt = 1
    last_error = None
    last_code = None
    original_prompt = prompt
    
    while attempt <= max_retries:
        if attempt > 1:
            print(f"\n{Style.BRIGHT}Attempt {attempt}/{max_retries}{Style.RESET_ALL}")
            prompt = generate_retry_prompt(prompt, last_error, last_code)
            code_response = fetch_chatgpt_code(client, prompt, is_retry=True)
        else:
            code_response = fetch_chatgpt_code(client, prompt, is_retry=False)
        
        if code_response:
            output_code = extract_code_from_response(code_response)
            last_code = output_code  
            print("\n=== Python Code ===")
            print(output_code)
            save_code_to_file(output_code, filename)
            success, message = execute_generated_code(filename)

            if success:
                original_time = float(message)
                optimize_code(original_prompt, original_time, filename)

                # Add lint check after optimization
                lint_success = check_and_fix_lint(client, filename, original_prompt)
                if lint_success:
                    print("Code generation, optimization, and lint checking completed successfully!")
                else:
                    print("Code works but has some remaining lint issues.")
                return True
            else:
                last_error = message
        else:
            last_error = "Failed to get response from GPT"
            if attempt < max_retries:
                print(Fore.RED + f"Failed to fetch a valid response from GPT. Trying again")
        
        attempt += 1
    
    print(Fore.RED + "Code generation FAILED")
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
    print(f"\n{Style.BRIGHT}=== Optimizing Code ==={Style.RESET_ALL}")
    print(f"Current execution time: {original_time:.2f}ms")
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
    if not code_response:
        return None
    else:
        # Save optimized version to temporary file for testing
        temp_filename = "temp.py"
        try:
            optimized_code = extract_code_from_response(code_response)
            save_code_to_file(optimized_code, temp_filename)
            
            success, message = execute_generated_code(temp_filename)
            if success:
                optimized_time = float(message)
                
                # Only keep optimization if it's actually faster
                if optimized_time < original_time:
                    save_code_to_file(optimized_code, filename)
                    os.remove(temp_filename)
                    return optimized_time
                else:
                    print("Optimization attempt did not improve performance")
            else:
                print("Optimized version failed tests")
            return original_time
        except Exception as e:
            print(Fore.RED + f"Error during optimization: {e}")
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        return original_time

def read_code_from_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except Exception as e:
        raise Exception(f"Error reading file: {e}")

def run_pylint(filename):
    """Run pylint on the specified file and return the output."""
    try:
        result = subprocess.run(['pylint', filename], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(Fore.RED + f"Error running pylint: {e}")
        return None

def fix_lint_issues(client, lint_output, current_code, original_prompt):
    """Request ChatGPT to fix lint issues in the code."""
    prompt = f"""
    The following Python code has some pylint issues:
    ```python
    {current_code}
    ```
    
    Pylint output:
    {lint_output}
    
    Please fix all the lint issues while maintaining the same functionality.
    Original request: {original_prompt}
    """
    
    code_response = fetch_chatgpt_code(client, prompt, is_retry=True)
    if code_response:
        return extract_code_from_response(code_response)
    return None

def check_and_fix_lint(client, filename, original_prompt):
    print(f"\n{Style.BRIGHT}=== Checking Code Quality ==={Style.RESET_ALL}")
    attempts = 0
    while attempts < MAX_LINT_ATTEMPTS:
        lint_output = run_pylint(filename)
        if not lint_output or "Your code has been rated at 10.00/10" in lint_output:
            print(Fore.GREEN + "Amazing. No lint errors/warnings")
            return True
            
        print(Fore.RED + f"Found lint issues (attempt {attempts + 1}/{MAX_LINT_ATTEMPTS}):")
        print(lint_output)
        
        current_code = read_code_from_file(filename)
        fixed_code = fix_lint_issues(client, lint_output, current_code, original_prompt)
        
        if fixed_code:
            save_code_to_file(fixed_code, filename)
            print(Fore.GREEN + "Applied lint fixes")
        else:
            print(Fore.RED + "Failed to fix lint issues")
            break
            
        attempts += 1
    
    if attempts >= MAX_LINT_ATTEMPTS:
        print(Fore.RED + f"There are still lint errors/warnings")
    return False


if __name__ == "__main__":
    prompt = "Create a python program that checks if a number is prime. Do not write any explanations, just show me the code itself."
    filename = "generatedcode.py"
    client = initialize_openai_client()
    process_and_execute_code(client, prompt, filename)