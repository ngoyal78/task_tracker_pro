#!/usr/bin/env python
"""
Test script for Ollama integration with Task Tracker Pro.
This script verifies that Ollama is properly set up and can generate task details.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
import time

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
    """Print a formatted header"""
    print(f"\n{BLUE}{BOLD}{'=' * 50}{RESET}")
    print(f"{BLUE}{BOLD}{text.center(50)}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 50}{RESET}\n")

def print_success(text):
    """Print a success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_warning(text):
    """Print a warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_error(text):
    """Print an error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    """Print an info message"""
    print(f"{BLUE}ℹ {text}{RESET}")

def check_ollama_running():
    """Check if Ollama is running"""
    print_info("Checking if Ollama is running...")
    
    # Get Ollama base URL from environment or use default
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
    """Check if the required model is available"""
    print_info("Checking model availability...")
    
    # Get model name from environment or use default
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
    """Test generating a task from a prompt"""
    print_info("Testing task generation...")
    
    # Get configuration from environment
    model_name = os.getenv("OLLAMA_MODEL", "mistral")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Sample prompt
    prompt = "Create a weekly report on sales performance by Friday."
    
    # System prompt to guide the model
    system_prompt = """
    You are a task creation assistant. Based on the user's description, extract the following details:
    - title: A concise title for the task
    - description: A detailed description of what needs to be done
    - priority: Either 'Low', 'Medium', or 'High'
    - category_id: Suggest a category ID (1 for Development, 2 for Design, 3 for Marketing, 4 for Operations)
    - due_date: A reasonable due date in YYYY-MM-DD format
    
    Format your response as a JSON object with these fields.
    """
    
    try:
        print_info(f"Sending prompt to {model_name}: '{prompt}'")
        
        # Prepare the API request
        url = f"{base_url}/api/generate"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "format": "json"
        }
        
        # Make the API request
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            
            # Try to parse the response as JSON
            try:
                task_data = json.loads(generated_text)
                
                # Check if all required fields are present
                required_fields = ['title', 'description', 'priority', 'category_id', 'due_date']
                missing_fields = [field for field in required_fields if field not in task_data]
                
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
    """Main function to run all tests"""
    print_header("Ollama Integration Test")
    
    # Check if Ollama is running
    if not check_ollama_running():
        return False
    
    # Check if the model is available
    if not check_model_availability():
        return False
    
    # Test task generation
    if not test_task_generation():
        return False
    
    print_header("All Tests Passed!")
    print_success("Ollama is properly configured and working with Task Tracker Pro")
    print_info("You can now use the AI-powered task creation feature")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
