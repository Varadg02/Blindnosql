Blind NoSQL Injection Toolkit
This repository contains a collection of Python scripts and JSON payloads designed to test for, exploit, and demonstrate Blind NoSQL injection vulnerabilities, particularly focusing on authentication bypass and data extraction.

Files and Components
Nosql.py: A command-line tool used to test target URLs for NoSQL vulnerabilities and attempt login bypasses.

It works by establishing a baseline response (measuring length, status code, and response time) using a bogus payload.

It checks for vulnerabilities using time-based delays, status code changes, or response length differences.

It provides an educational breakdown of why an injection was successful when a vulnerability is found.

payload.json: A dictionary file containing various NoSQL injection payloads that Nosql.py iterates through.

It includes payloads utilizing operators like $ne (not equal), $gt (greater than), $regex, $exists, $type, $in, and $or.

It also includes a time-based payload utilizing the $where operator to force the server to sleep.

blind_extractor.py: A script designed to extract flags or passwords character-by-character using a "Low and Slow" Blind NoSQL extraction technique.

It iterates through alphanumeric characters and symbols using the $regex operator to guess the password one character at a time.

It features built-in evasion by sleeping for a random interval between 120 and 180 seconds before testing each character.

Console.json: A sample JavaScript fetch snippet demonstrating how an attacker could manually exploit the NoSQL login bypass vulnerability directly from a browser console by sending {"$ne": "wrong_password"}.

Usage Requirements
Python 3.x

requests library

Running the Tools
1. Vulnerability Scanning and Auth Bypass (Nosql.py)
Run the script by passing the target login URL as an argument:

Bash
python Nosql.py http://localhost:5000/login
From the interactive menu, you can set the target username, session cookie, test all payloads for vulnerabilities, or attempt to bypass the login.

2. Data Extraction (blind_extractor.py)
To begin extracting a password or flag for a specific user (defaults to "admin"), run:

Bash
python blind_extractor.py
Note: Due to the evasion techniques implemented in the script, this process can take several hours to days to complete.

Disclaimer: These tools are provided for educational and authorized security testing purposes only.

Author 
- Varad Gandhi
