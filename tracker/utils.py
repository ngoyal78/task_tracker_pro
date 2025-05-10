# tracker/utils.py
import logging
import json
import requests
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.conf import settings
import dateparser
import datetime

logger = logging.getLogger('tracker')

def compute_due_date(natural_text): 
    """Convert natural date expressions like 'next Monday' to YYYY-MM-DD"""
    # Special handling for "next Monday" or similar expressions
    import re
    next_day_match = re.search(r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', natural_text.lower())
    
    if next_day_match:
        day_name = next_day_match.group(1).capitalize()
        # Get today's date
        today = datetime.datetime.now()
        # Get today's weekday (0 = Monday, 6 = Sunday in Python's datetime)
        today_weekday = today.weekday()
        
        # Convert day name to weekday number (0-6)
        day_to_num = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        target_weekday = day_to_num[day_name]
        
        # Calculate days until next occurrence of the target day
        days_ahead = target_weekday - today_weekday
        if days_ahead <= 0:  # Target day is today or earlier in the week
            days_ahead += 7  # So we want next week's occurrence
            
        # Calculate the date
        next_day_date = today + datetime.timedelta(days=days_ahead)
        logger.info(f"Calculated next {day_name} as {next_day_date.strftime('%Y-%m-%d')}")
        return next_day_date.strftime('%Y-%m-%d')
    
    # Use dateparser for other expressions
    parsed_date = dateparser.parse(
        natural_text,
        settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.datetime.now(),
            'RETURN_AS_TIMEZONE_AWARE': False
        }
    )
    if parsed_date:
        return parsed_date.strftime('%Y-%m-%d')
    return None

def generate_task_from_prompt(prompt):
    """
    Generate task details from a text prompt using Ollama.
    If Ollama is not available, falls back to a rule-based extraction.
    
    Args:
        prompt (str): The user's text prompt describing the task
        
    Returns:
        dict: A dictionary containing generated task details or None if failed
    """
    if not prompt:
        logger.error("Empty prompt provided to task generator")
        return None
    
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    # First try using Ollama
    try:
        # Prepare the system prompt to guide the model
        system_prompt = f"""
        You are a task creation assistant for an auto surveyor business. Based on the user's description, extract the following details:
        - title: A concise title for the task (include vehicle identification if available)
        - description: A detailed description of what needs to be done, including:
          * Vehicle details (make, model, VIN if mentioned)
          * Location information
          * Damage description
          * Special instructions
        - priority: Either 'Low', 'Medium', or 'High' (use High for urgent cases or severe damage)
        - category_id: Suggest a category ID:
          * 1 for Initial Survey
          * 2 for Damage Assessment
          * 3 for Claims Processing
          * 4 for Final Inspection
        - due_date: Convert relative expressions like 'next Monday' into a date string in YYYY-MM-DD format, using today’s date as {today_str}.
        - assigned_to: Extract name of person to assign to if mentioned
        
        Format your response as a JSON object with these fields.
        """
        
        # Prepare the API request to Ollama
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "format": "json"
        }
        
        # Make the API request
        logger.info(f"Sending prompt to Ollama: {prompt[:50]}...")
        response = requests.post(url, json=payload, timeout=1200)  # Shorter timeout for faster fallback
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        generated_text = result.get('response', '')
        
        # Extract the JSON part from the response
        try:
            # Try to parse the entire response as JSON
            task_data = json.loads(generated_text)
            
            # Validate required fields
            required_fields = ['title', 'description', 'priority', 'category_id', 'due_date']
            for field in required_fields:
                if field not in task_data:
                    logger.warning(f"Missing required field in generated task: {field}")
                    task_data[field] = "Not specified" if field != 'category_id' else 1
            # Attempt to resolve due_date if it's still natural language
            logger.info(f"Inferred due_date '{task_data['due_date']}'")
            if 'due_date' in task_data:
                original_due = task_data['due_date']
                # If the original due date is "in a week", set it to 7 days from now
                if original_due.lower() == "in a week":
                    task_data['due_date'] = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
                    logger.info(f"Converted 'in a week' to '{task_data['due_date']}'")
                else:
                    parsed_due = compute_due_date(original_due)
                    if parsed_due:
                        task_data['due_date'] = parsed_due
                        logger.info(f"Converted due_date '{original_due}' → '{parsed_due}'")
                    else:
                        # If parsing fails, default to 7 days from now
                        task_data['due_date'] = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
                        logger.warning(f"Could not parse due_date: '{original_due}', defaulting to 7 days from now")
                   
            logger.info(f"Successfully generated task details from prompt using Ollama")
            return task_data
            
        except json.JSONDecodeError:
            # If not valid JSON, try to extract JSON from the text
            logger.warning("Failed to parse response as JSON, attempting to extract JSON")
            import re
            json_match = re.search(r'({.*})', generated_text, re.DOTALL)
            if json_match:
                try:
                    task_data = json.loads(json_match.group(1))
                    return task_data
                except json.JSONDecodeError:
                    logger.error("Failed to extract valid JSON from response")
                    # Fall through to rule-based extraction
            else:
                logger.error("No JSON-like structure found in response")
                # Fall through to rule-based extraction
                
    except (requests.exceptions.RequestException, Exception) as e:
        logger.warning(f"Error using Ollama: {str(e)}. Falling back to rule-based extraction.")
        # Fall through to rule-based extraction
    
    # Fallback: Rule-based extraction
    logger.info("Using rule-based extraction as fallback")
    return rule_based_task_extraction(prompt)

def rule_based_task_extraction(prompt):
    """
    Extract task details from a prompt using simple rule-based approach.
    Used as a fallback when Ollama is not available.
    
    Args:
        prompt (str): The user's text prompt describing the task
        
    Returns:
        dict: A dictionary containing extracted task details
    """
    from datetime import datetime, timedelta
    import re
    
    # Initialize task data with defaults
    task_data = {
        'title': 'New Task',
        'description': prompt,
        'priority': 'Medium',
        'category_id': 1,  # Default to first category
        'due_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    }
    
    # Extract title (first sentence or first 50 chars)
    first_sentence_match = re.match(r'^([^.!?]+[.!?])', prompt)
    if first_sentence_match:
        task_data['title'] = first_sentence_match.group(1).strip()
    else:
        # If no sentence found, use first 50 chars
        task_data['title'] = prompt[:50] + ('...' if len(prompt) > 50 else '')
    
    # Extract priority
    if re.search(r'\bhigh\s+priority\b|\bpriority\s*:\s*high\b|\bimportant\b|\burgent\b', prompt, re.I):
        task_data['priority'] = 'High'
    elif re.search(r'\blow\s+priority\b|\bpriority\s*:\s*low\b|\bnot\s+urgent\b|\bcan\s+wait\b', prompt, re.I):
        task_data['priority'] = 'Low'
    
    # Extract category for auto surveyor business
    if re.search(r'\bdamage\s+assessment\b|\bdamage\b|\bassess\b', prompt, re.I):
        task_data['category_id'] = 2  # Damage Assessment
    elif re.search(r'\bclaims?\b|\bprocessing\b|\binsurance\b|\bclaim\s+processing\b', prompt, re.I):
        task_data['category_id'] = 3  # Claims Processing
    elif re.search(r'\bfinal\b|\binspection\b|\bfinal\s+inspection\b|\bclose\b', prompt, re.I):
        task_data['category_id'] = 4  # Final Inspection
    else:
        task_data['category_id'] = 1  # Default to Initial Survey
        
    # Extract vehicle information
    vin_match = re.search(r'\b([A-HJ-NPR-Z0-9]{17})\b', prompt)  # Standard VIN format
    if vin_match:
        task_data['description'] = f"VIN: {vin_match.group(1)}\n\n{task_data['description']}"
        if 'VIN' not in task_data['title']:
            task_data['title'] = f"Survey for VIN {vin_match.group(1)[:8]}"
            
    # Extract assigned person
    assign_match = re.search(r'(?:assign(?:ed)?\s+to|for)\s+([A-Z][a-z]+)', prompt)
    if assign_match:
        task_data['assigned_to'] = assign_match.group(1)
    
    # Extract due date
    # First check for "next Monday" or similar expressions
    next_day_match = re.search(r'by\s+next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', prompt.lower())
    if next_day_match:
        day_name = next_day_match.group(1).capitalize()
        # Get today's date
        today = datetime.now()
        # Get today's weekday (0 = Monday, 6 = Sunday in Python's datetime)
        today_weekday = today.weekday()
        
        # Convert day name to weekday number (0-6)
        day_to_num = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        target_weekday = day_to_num[day_name]
        
        # Calculate days until next occurrence of the target day
        days_ahead = target_weekday - today_weekday
        if days_ahead <= 0:  # Target day is today or earlier in the week
            days_ahead += 7  # So we want next week's occurrence
            
        # Calculate the date
        next_day_date = today + timedelta(days=days_ahead)
        logger.info(f"Rule-based extraction: Calculated next {day_name} as {next_day_date.strftime('%Y-%m-%d')}")
        task_data['due_date'] = next_day_date.strftime('%Y-%m-%d')
    else:
        # Check other date patterns
        date_patterns = [
            # Format: by January 15, 2023
            r'by\s+(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})',
            # Format: by 15 January 2023
            r'by\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\w+),?\s+(\d{4})',
            # Format: by 2023-01-15
            r'by\s+(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
            # Format: by 01/15/2023
            r'by\s+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            # Format: by next week/month
            r'by\s+next\s+(\w+)',
            # Format: in 5 days/weeks
            r'in\s+(\d+)\s+(\w+)'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, prompt, re.I)
            if match:
                try:
                    due_date = None
                    if 'next' in pattern:
                        # Handle "next week/month"
                        time_unit = match.group(1).lower()
                        if time_unit == 'week':
                            due_date = datetime.now() + timedelta(days=7)
                        elif time_unit == 'month':
                            # Approximate a month as 30 days
                            due_date = datetime.now() + timedelta(days=30)
                    elif 'in' in pattern:
                        # Handle "in X days/weeks"
                        amount = int(match.group(1))
                        unit = match.group(2).lower()
                        if 'day' in unit:
                            due_date = datetime.now() + timedelta(days=amount)
                        elif 'week' in unit:
                            due_date = datetime.now() + timedelta(days=amount*7)
                    
                    if due_date:
                        task_data['due_date'] = due_date.strftime('%Y-%m-%d')
                        break
                except Exception as e:
                    # If date parsing fails, keep the default
                    logger.warning(f"Error parsing date pattern: {str(e)}")
    
    logger.info(f"Rule-based extraction completed: {task_data['title']}")
    return task_data

def transcribe_audio(audio_file):
    """
    Transcribe audio to text using Whisper API.
    
    Args:
        audio_file: The audio file object to transcribe
        
    Returns:
        str: The transcribed text or None if failed
    """
    try:
        # Check if whisper is installed
        import whisper
    except ImportError:
        logger.error("Whisper is not installed. Install with 'pip install openai-whisper'")
        return None
        
    try:
        # Load the Whisper model (will download if not present)
        model = whisper.load_model("base")
        
        # Save the uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
            
        # Transcribe the audio
        logger.info(f"Transcribing audio file: {temp_path}")
        result = model.transcribe(temp_path)
        transcribed_text = result["text"]
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        logger.info(f"Successfully transcribed audio: {transcribed_text[:50]}...")
        return transcribed_text
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return None

def send_whatsapp_message(to_number, message_body):
    """
    Send a WhatsApp message using Twilio API.
    
    Args:
        to_number (str): The recipient's phone number
        message_body (str): The message content to send
        
    Returns:
        str or None: The message SID if successful, None if failed
        
    Raises:
        No exceptions are raised as they are caught and logged internally
    """
    # Validate inputs
    if not to_number or not message_body:
        logger.error("Invalid parameters: phone number or message body is empty")
        return None
        
    try:
        # Initialize Twilio client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Format the phone number for WhatsApp
        whatsapp_number = f'whatsapp:{to_number}'
        
        # Send the message
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            body=message_body,
            to=whatsapp_number
        )
        
        # Log success
        logger.info(f"WhatsApp message sent to {to_number}: {message.sid}")
        return message.sid
        
    except TwilioRestException as e:
        # Log Twilio-specific errors
        logger.error(f"Twilio error sending WhatsApp message to {to_number}: {str(e)}")
        return None
    except Exception as e:
        # Log any other unexpected errors
        logger.error(f"Unexpected error sending WhatsApp message to {to_number}: {str(e)}")
        return None
