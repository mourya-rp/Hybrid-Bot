# Hybrid-Bot (RAG + VISION)
This repository contains a high-performance, lightweight GenAI bot. It implements a Hybrid Architecture , merging (RAG) document retrieval with multimodal image analysis into a single Telegram interface.

# Demo Screenshots
Screenshots demonstrating working interactions are located in the Demo_screenshots folder.

# System Design:
The system is designed for modularity and clear data flow, separating the bot interface from the retrieval and vision engines


<img width="4011" height="2993" alt="system_design" src="https://github.com/user-attachments/assets/c66d02fe-9486-43e2-8d07-c9c5619f7aaa" />

## Logic Flow:

Retrieval (RAG): Documents are split into chunks , embedded using a local sentence-transformers model , and queried using vector similarity.

Vision: Uploaded images are buffered and sent to a multimodal LLM to generate captions and metadata.

Memory: Every interaction is cached in a session-based dictionary to enable historical awareness

## Tech Stack & Model Selection:

Chosen for a balance of efficiency and performance:

Bot Framework: python-telegram-bot (v22.7).

Embeddings: all-MiniLM-L6-v2 (Local model for fast, offline vectorization).

LLM & Vision: Gemini 2.5 flash (via OpenRouter API) for state-of-the-art multimodal reasoning.

Containerization: Docker for consistent environment deployment.

## High-Tier Enhancements :
This submission implements all Optional Enhancements :

 Message History Awareness: Maintains a rolling history of the last 5 interactions per user.

 Source Snippets: Every RAG response explicitly identifies the source document used for the answer.

 Smart Caching: Local embedding avoids redundant API calls for seen queries.

 /summarize Command: Synthesizes the last image analysis and chat history into a comprehensive report.

 # How to Run Locally :

 1. Prerequisites

- Docker Desktop installed.

- Telegram Bot Token (via @BotFather).

- OpenRouter API Key.

 2. Configuration

 Create a .env file in the root directory:

 TELEGRAM_TOKEN=your_token_here
OPENROUTER_API_KEY=your_key_here

3. Deployment via Docker

### Build the image
docker build -t hybrid-bot .

### Run the container (with unbuffered logs for real-time monitoring)

docker run --rm -e PYTHONUNBUFFERED=1 --env-file .env -v "$(pwd)/docs:/app/docs" hybrid-bot

## Usage Instructions

/start — Initialize the bot.

/ask <query> — Query the Zomato policy knowledge base.

Upload Image — Send a photo to receive a description and tags.

/summarize — Summarize the current session history and last image.

/help — View usage instructions
 
