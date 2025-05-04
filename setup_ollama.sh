#!/bin/bash

echo "==================================="
echo "Ollama Setup for Task Tracker Pro"
echo "==================================="
echo

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed on your system."
    echo
    echo "Please install Ollama from https://ollama.ai/download"
    echo "After installation, run this script again."
    echo
    read -p "Press Enter to continue..."
    exit 1
fi

echo "Ollama is installed. Checking if Ollama service is running..."
echo

# Check if Ollama service is running
if ! curl -s http://localhost:11434/api/version &> /dev/null; then
    echo "Ollama service is not running."
    echo
    echo "Starting Ollama service..."
    ollama serve &
    echo "Waiting for Ollama to start..."
    sleep 5
    
    # Check again if service is running
    if ! curl -s http://localhost:11434/api/version &> /dev/null; then
        echo "Failed to start Ollama service."
        echo "Please start it manually with 'ollama serve' in a separate terminal."
        echo
        read -p "Press Enter to continue..."
        exit 1
    fi
    echo "Ollama service started successfully."
else
    echo "Ollama service is running."
fi
echo

# Check available models
echo "Checking available models..."
ollama list

echo
echo "Recommended model for Task Tracker Pro: mistral"
echo

# Check if mistral model is available
if ! ollama list | grep -q "mistral"; then
    echo "The recommended model 'mistral' is not available."
    echo
    read -p "Would you like to pull the mistral model now? (y/n): " INSTALL_MODEL
    if [[ $INSTALL_MODEL == "y" || $INSTALL_MODEL == "Y" ]]; then
        echo
        echo "Pulling mistral model (this may take a few minutes)..."
        ollama pull mistral
        echo
        echo "Model downloaded successfully."
    else
        echo
        echo "You can pull the model later with 'ollama pull mistral'"
        echo "Or use a different model by updating your .env file."
    fi
else
    echo "The recommended model 'mistral' is already available."
fi

echo
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo
echo "You can now use the GenAI task creation feature."
echo "Make sure your .env file has the following settings:"
echo
echo "OLLAMA_BASE_URL=http://localhost:11434"
echo "OLLAMA_MODEL=mistral"
echo
echo "To test your setup, run: python test_ollama.py"
echo
read -p "Press Enter to continue..."
