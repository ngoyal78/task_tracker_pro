#!/usr/bin/env python
"""
Test script for Ollama integration with Task Tracker Pro.
This script verifies that Ollama is properly set up and can generate task details.
"""

import os
import sys
import json
import requests
import time
import dateparser
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ANSI color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{BOLD}{'=' * 50}{RESET}")
    print(f"{BLUE}{BOLD}{text.center(50)}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 50}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ {text}{RESET}")

def compute_due_date(natural_text):
    """Convert natural date expressions like 'next Monday' to YYYY-MM-DD"""
    parsed_date = dateparser.parse(natural_text, settings={'PREFER_DATES_FROM': 'future'})
    if parsed_date:
        return parsed_date.strftime('%Y-%m-%d')
    return None

def check_ollama_running():
    print_info("Checking if Ollama is running...")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        response = requests.get(f"{base_url}/api/version", timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            print_success(f"Ollama is running (version: {version_info.get('version', 'unknown')})")
            return True
        else:
            print_error(f"Ollama returned unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to Ollama at {base_url}")
        print_info("Make sure Ollama is installed and running with 'ollama serve'")
        return False
    except Exception as e:
        print_error(f"Error checking Ollama: {str(e)}")
        return False

def check_model_availability():
    print_info("Checking model availability...")
    model_name = os.getenv("OLLAMA_MODEL", "mistral")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name') for model in models]
            if model_name in model_names:
                print_success(f"Model '{model_name}' is available")
                return True
            else:
                print_warning(f"Model '{model_name}' is not available")
                print_info(f"Available models: {', '.join(model_names) if model_names else 'None'}")
                print_info(f"You can pull the model with: ollama pull {model_name}")
                return False
        else:
            print_error(f"Error checking models: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error checking model availability: {str(e)}")
        return False

def test_task_generation():
    print_info("Testing task generation...")
    model_name = os.getenv("OLLAMA_MODEL", "mistral")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    prompt = "Routine check for VIN MH12DE1433 at Pune scheduled next Monday"

    system_prompt = f"""
    You are an intelligent assistant for an automotive field task tracker system that logs and manages tasks related to vehicle surveys, diagnostics, and inspections.

    When given a prompt that may mention vehicles (e.g., VINs), locations, times, or maintenance actions, extract and format the following fields:

    - title: A concise summary of the task (e.g., "Routine Inspection - MH12DE1433")
    - description: A detailed description of what needs to be done, including vehicle info, location, and schedule
    - priority: 'High' if safety-related or urgent, otherwise 'Medium' or 'Low'
    - category_id: Use:
        1 for Diagnostics/Engineering,
        2 for Survey/Inspection,
        3 for Data Collection,
        4 for Logistics/Operations
    - due_date: Convert relative expressions like 'next Monday' into a date string in YYYY-MM-DD format, using today’s date as {time.strftime('%Y-%m-%d')}.

    Always format your response as a JSON object with these fields.
    """

    try:
        print_info(f"Sending prompt to {model_name}: '{prompt}'")
        url = f"{base_url}/api/generate"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "format": "json"
        }

        start_time = time.time()
        response = requests.post(url, json=payload, timeout=180)
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')

            try:
                task_data = json.loads(generated_text)

                required_fields = ['title', 'description', 'priority', 'category_id', 'due_date']
                missing_fields = [field for field in required_fields if field not in task_data]

                # Attempt to resolve due_date if it's still natural language
                if 'due_date' in task_data:
                    original_due = task_data['due_date']
                    parsed_due = compute_due_date(original_due)
                    if parsed_due:
                        task_data['due_date'] = parsed_due
                        print_info(f"Converted due_date '{original_due}' → '{parsed_due}'")
                    else:
                        print_warning(f"Could not parse due_date: '{original_due}'")

                if missing_fields:
                    print_warning(f"Generated task is missing fields: {', '.join(missing_fields)}")
                else:
                    print_success(f"Task generation successful (took {end_time - start_time:.2f}s)")
                    print_info("Generated task:")
                    print(json.dumps(task_data, indent=2))
                    return True

            except json.JSONDecodeError:
                print_warning("Could not parse response as JSON")
                print_info("Raw response:")
                print(generated_text[:500] + "..." if len(generated_text) > 500 else generated_text)
                return False
        else:
            print_error(f"Error generating task: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error testing task generation: {str(e)}")
        return False

def main():
    print_header("Ollama Integration Test")

    if not check_ollama_running():
        return False

    if not check_model_availability():
        return False

    if not test_task_generation():
        return False

    print_header("All Tests Passed!")
    print_success("Ollama is properly configured and working with Task Tracker Pro")
    print_info("You can now use the AI-powered task creation feature")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
