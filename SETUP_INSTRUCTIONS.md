# Setting Up GenAI Task Creation with Ollama

This guide provides detailed instructions for setting up the GenAI-powered task creation feature in Task Tracker Pro using Ollama.

## Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher
- pip (Python package manager)
- Administrative access to install software on your machine

## Step 1: Install Ollama

Ollama is an open-source tool that lets you run large language models locally on your machine.

### Windows

1. Download the Ollama installer from [https://ollama.ai/download](https://ollama.ai/download)
2. Run the installer and follow the on-screen instructions
3. After installation, open a Command Prompt and run `ollama serve` to start the Ollama service

### macOS

1. Download the Ollama app from [https://ollama.ai/download](https://ollama.ai/download)
2. Open the downloaded DMG file and drag Ollama to your Applications folder
3. Launch Ollama from your Applications folder
4. Ollama will run in the menu bar

### Linux

1. Run the following command to install Ollama:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```
2. Start the Ollama service:
   ```bash
   ollama serve
   ```

## Step 2: Pull the Recommended Model

Task Tracker Pro is configured to use the Mistral model by default. You need to download this model:

```bash
ollama pull mistral
```

This will download the model, which is approximately 4GB in size. The download time depends on your internet connection speed.

> **Note**: You can use other models like `llama2` or `codellama` by updating your `.env` file after downloading them.

## Step 3: Configure Task Tracker Pro

1. Create or update your `.env` file in the project root directory with the following settings:

   ```
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=mistral
   WHISPER_ENABLED=False  # Set to True if you want to use voice input
   ```

2. If you want to use voice input (optional):
   
   ```bash
   pip install openai-whisper
   ```
   
   Then update your `.env` file:
   
   ```
   WHISPER_ENABLED=True
   ```

## Step 4: Test Your Setup

Run the provided test script to verify that everything is working correctly:

```bash
python test_ollama.py
```

This script will:
1. Check if Ollama is running
2. Verify if the Mistral model is available
3. Test task generation with a sample prompt

If all tests pass, you're ready to use the GenAI task creation feature!

## Troubleshooting

### Ollama Not Running

If you see an error that Ollama is not running:

1. Open a new terminal or command prompt
2. Run `ollama serve`
3. Keep this terminal open while using Task Tracker Pro

### Model Not Found

If the test script reports that the model is not found:

1. Check available models: `ollama list`
2. Pull the Mistral model: `ollama pull mistral`
3. Verify it was downloaded: `ollama list`

### Slow Response Times

If task generation is taking too long:

1. Ensure your computer meets the minimum requirements for running LLMs
2. Try a smaller model by updating your `.env` file:
   ```
   OLLAMA_MODEL=orca-mini
   ```
   (Remember to pull the model first: `ollama pull orca-mini`)

### Connection Errors

If you're getting connection errors:

1. Verify Ollama is running with `curl http://localhost:11434/api/version`
2. Check if any firewall or antivirus software is blocking the connection
3. Ensure the `OLLAMA_BASE_URL` in your `.env` file matches the address where Ollama is running

## Using Different Models

Ollama supports various models with different capabilities and resource requirements:

| Model | Size | Strengths | Command |
|-------|------|-----------|---------|
| mistral | ~4GB | Good all-around performance, balanced | `ollama pull mistral` |
| llama2 | ~4GB | Strong reasoning, instruction following | `ollama pull llama2` |
| codellama | ~4GB | Specialized for code and technical tasks | `ollama pull codellama` |
| orca-mini | ~1.5GB | Smaller, faster, less resource intensive | `ollama pull orca-mini` |

After pulling a different model, update your `.env` file to use it:

```
OLLAMA_MODEL=llama2  # or whichever model you want to use
```

## Advanced Configuration

### Running Ollama on a Different Machine

You can run Ollama on a different machine (with more resources) and connect to it:

1. On the server machine, run:
   ```bash
   OLLAMA_HOST=0.0.0.0 ollama serve
   ```

2. On your Task Tracker Pro machine, update your `.env` file:
   ```
   OLLAMA_BASE_URL=http://server-ip-address:11434
   ```

### Customizing System Prompts

If you want to customize how the AI extracts task details, you can modify the system prompt in `tracker/utils.py`.

## Getting Help

If you encounter any issues not covered in this guide:

1. Check the Ollama documentation: [https://github.com/ollama/ollama](https://github.com/ollama/ollama)
2. Look for error messages in the application logs: `logs/app.log`
3. Contact your system administrator or the Task Tracker Pro support team
