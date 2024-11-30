#chat_app.py
from openai import OpenAI
import os
import subprocess
from tqdm import tqdm
import time
from colorama import init, Fore, Style, Back

# Initialize colorama
init(autoreset=True)

# === Color Scheme Constants ===
def print_header(text):
    print(f"\n{Style.BRIGHT}{Fore.BLUE}{Back.WHITE}=== {text} ==={Style.RESET_ALL}")

def print_subheader(text):
    print(f"\n{Style.BRIGHT}{Fore.CYAN}>> {text} <<{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.YELLOW}ℹ {text}{Style.RESET_ALL}")

# === Constants ===
OPENAI_API_KEY_ENV_VAR = "OPENAI_API_KEY"
GPT_MODEL = "gpt-4o-mini"
UNIT_TEST_PROMPT = (
    "Also, please include running unit tests with asserts that check the logic of the program. "
    "Make sure to also check interesting edge cases. There should be at least 10 different unit tests. "
)
SYSTEM_ROLE_MESSAGE = "You are a python programmer who can create a python program to solve a problem. Do not write any explanations, just show me the code itself."
MAX_LINT_ATTEMPTS = 3

# === Functions ===
def initialize_openai_client():
    with tqdm(total=100, desc="Initializing OpenAI Client", unit="%", ncols=80) as pbar:
        for _ in range(5): 
            time.sleep(0.5)  
            pbar.update(20)  
        pbar.update(100 - pbar.n) 
    
    api_key = os.getenv(OPENAI_API_KEY_ENV_VAR)
    return OpenAI(api_key=api_key)

def fetch_chatgpt_code(client, prompt, is_retry=False):
    try:
        prompt_to_send = prompt + UNIT_TEST_PROMPT if not is_retry else prompt 
        with tqdm(total=100, desc="Fetching GPT Response", unit="%", ncols=80) as pbar:
            for _ in range(4): 
                time.sleep(0.5)  
                pbar.update(25)  

            completion = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_ROLE_MESSAGE},
                    {"role": "user", "content": prompt_to_send}
                ]
            )
            pbar.update(100 - pbar.n)  

        return completion.choices[0].message.content

    except Exception as e:
        print_error(f"Error fetching response from GPT: {e}")
        return None

def save_code_to_file(code, filename):
    print_subheader("Saving Code")
    try:
        with tqdm(total=100, desc="Saving Code to File", unit="%", ncols=80) as pbar:
            for _ in range(5): 
                time.sleep(0.2)  
                pbar.update(20)  
            with open(filename, "w") as file:
                file.write(code)
            pbar.update(100 - pbar.n)  
        print_success(f"Code saved to {filename}")
    except Exception as e:
        print_error(f"Failed to save code: {e}")

def execute_generated_code(filename):
    try:
        print_header("Executing Generated Code")
        
        # Initialize the progress bar
        with tqdm(total=100, desc="Code Execution in Progress", unit="%", ncols=80) as pbar:
            start_time = time.perf_counter()
            process = subprocess.Popen(['python', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            result_stdout, result_stderr = process.communicate()
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
            pbar.update(100 - pbar.n)

        if process.returncode == 0:
            # If return code is 0 and no stderr, tests passed successfully
            if not result_stderr:
                print_subheader("Test Results")
                if result_stdout:
                    print(f"{Fore.WHITE}{result_stdout}{Style.RESET_ALL}")
                print_success(f"All tests passed! Execution completed in {execution_time:.2f}ms")
                return True, str(execution_time)
            return False, "Tests did not pass successfully"
        else:
            error_msg = result_stderr
            print_error("Execution Error:")
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
            return False, error_msg
    except Exception as e:
        error_msg = str(e)
        print_error(f"Error while executing the generated code: {error_msg}")
        return False, error_msg

def process_and_execute_code(client, prompt, filename, max_retries=5):
    print_header("Processing Code")
    attempt = 1
    last_error = None
    last_code = None
    original_prompt = prompt
    
    while attempt <= max_retries:
        if attempt > 1:
            print_subheader(f"Attempt {attempt}/{max_retries}")
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
                optimize_code(client, original_prompt, original_time, filename)

                # Add lint check after optimization
                lint_success = check_and_fix_lint(client, filename, original_prompt)
                if lint_success:
                    print_success("Code generation, optimization, and lint checking completed successfully!")
                else:
                    print_error("Code works but has some remaining lint issues.")
                return True
            else:
                last_error = message
                print_error(f"Error running generated code! Error: {last_error}. Trying again")
        else:
            last_error = "Failed to get response from GPT"
            if attempt < max_retries:
                print_info("Failed to fetch a valid response from GPT. Trying again")
        
        attempt += 1
    
    print_error("Code generation FAILED")
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

def optimize_code(client, original_prompt, original_time, filename):
    print_header("Optimizing Code")
    print_info(f"Current execution time: {original_time:.2f}ms")
    try:
        current_code = read_code_from_file(filename)
    except Exception as e:
        print_error(str(e))
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
                
                if optimized_time < original_time:
                    print_success(f"Optimization successful! New execution time: {optimized_time:.2f}ms")
                    print_info(f"Code running time optimized! It now runs in {optimized_time:.2f} ms, while before it was {original_time:.2f} ms.")
                    print_info(f"Improvement: {((original_time - optimized_time) / original_time * 100):.1f}%")
                    save_code_to_file(optimized_code, filename)
                    os.remove(temp_filename)
                    return optimized_time
                else:
                    print("Optimization attempt did not improve performance")
            else:
                print("Optimized version failed tests")
                return original_time
        except Exception as e:
            print_error(f"Error during optimization: {e}")
        finally:
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
        print_error(f"Error running pylint: {e}")
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
    print_header("Checking Code Quality")
    attempts = 0
    while attempts < MAX_LINT_ATTEMPTS:
        with tqdm(total=100, desc=f"Lint Check Attempt {attempts + 1}", unit="%", ncols=80) as pbar:
            for _ in range(5): 
                time.sleep(0.2)  
                pbar.update(20)  
        
            # Run pylint
            lint_output = run_pylint(filename)
            pbar.update(100 - pbar.n) 

        if not lint_output or "Your code has been rated at 10.00/10" in lint_output:
            print(Fore.GREEN + "Amazing. No lint errors/warnings")
            return True
            
        print_error(f"Found lint issues (attempt {attempts + 1}/{MAX_LINT_ATTEMPTS}):")
        print(f"{Fore.YELLOW}{lint_output}{Style.RESET_ALL}")
        
        current_code = read_code_from_file(filename)
        fixed_code = fix_lint_issues(client, lint_output, current_code, original_prompt)
        
        if fixed_code:
            save_code_to_file(fixed_code, filename)
            print_success("Applied lint fixes")
            lint_output = run_pylint(filename)
            if not lint_output or "Your code has been rated at 10.00/10" in lint_output:
                print(Fore.GREEN + "All lint issues resolved!")
                return True
        else:
            print_error("Failed to fix lint issues")
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