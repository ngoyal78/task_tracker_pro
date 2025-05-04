# GenAI-Powered Task Creation for Auto Surveyors

This document provides information about the GenAI-powered task creation feature customized for auto surveyor businesses.

## Overview

The Task Tracker Pro application has been extended with GenAI capabilities to enable auto surveyors to create tasks using natural language descriptions. The system uses Ollama to run open-source models locally, ensuring privacy and offline capability.

## Features

- **Natural Language Task Creation**: Describe vehicle surveys, damage assessments, and insurance claims in plain language
- **Voice Input Support**: Speak your task descriptions using the optional Whisper integration
- **Intelligent Data Extraction**: Automatically extracts key information like:
  - Vehicle details (make, model, VIN)
  - Location information
  - Damage descriptions
  - Assignment preferences
  - Due dates and priorities
- **Privacy-Focused**: All processing happens locally on your machine
- **No API Costs**: Uses free, open-source models

## Auto Surveyor Specific Capabilities

The system has been customized to understand auto surveyor terminology and extract relevant information:

1. **Vehicle Identification**: Automatically detects and extracts VIN numbers, make, and model information
2. **Damage Assessment**: Recognizes damage descriptions and severity levels
3. **Location Tracking**: Extracts location information for vehicles
4. **Insurance Details**: Captures insurance company names and policy numbers
5. **Task Categorization**: Automatically categorizes tasks as:
   - Initial Survey (Category 1)
   - Damage Assessment (Category 2)
   - Claims Processing (Category 3)
   - Final Inspection (Category 4)

## Example Use Cases

### Basic Vehicle Survey
```
Survey completed for VIN WB02A1234 near Indore. Minor rear damage. Assign to Ramesh. Due tomorrow.
```

### Urgent Damage Assessment
```
Urgent: Need damage assessment for Honda Civic with VIN 1HGCM82633A123456 involved in major collision in Mumbai. Customer needs report for insurance claim by end of day. Severe front-end damage with airbag deployment.
```

### Claims Processing
```
Process insurance claim for Toyota Fortuner (VIN MHFYZ59G7KP085421) surveyed last week. All documentation received from customer. Moderate damage to driver side door and fender. Insurance company: ICICI Lombard. Policy #: IL-AUTO-12345.
```

### Final Inspection
```
Final inspection needed for Maruti Swift (VIN MA3EWDE1S00152437) at Sharma Motors workshop in Delhi. Repairs completed after rear-end collision. Verify paint matching and bumper alignment. Assign to Vikram for Thursday.
```

## Setup Instructions

1. Follow the instructions in `SETUP_INSTRUCTIONS.md` to install and configure Ollama
2. Run the setup script appropriate for your operating system:
   - Windows: `setup_ollama.bat`
   - macOS/Linux: `setup_ollama.sh`
3. Test your setup with `python test_ollama.py`
4. Start using the GenAI task creation feature from the dashboard

## Customizing the System

If you need to customize the system further for your specific auto surveyor business:

1. **Modify the System Prompt**: Edit the system prompt in `tracker/utils.py` to include additional fields or instructions
2. **Update Rule-Based Extraction**: Enhance the rule-based extraction in `tracker/utils.py` to capture additional patterns
3. **Add Custom Categories**: Update the category IDs in the system prompt to match your business categories

## Tips for Best Results

1. Include as much vehicle information as possible (VIN, make, model)
2. Clearly describe the damage and its severity
3. Specify the location of the vehicle
4. Mention any deadlines or priority levels
5. Include the name of the person the task should be assigned to
6. For claims processing, include insurance details when available

## Example Prompts

For more example prompts and expected outputs, see `example_prompts.md` or access it from the AI task creation page.
