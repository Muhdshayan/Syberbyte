#!/bin/bash

# SmartRecruit AI Quick Start Script

echo "🚀 Starting SmartRecruit AI..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "🧠 Downloading NLP models..."
python -m spacy download en_core_web_sm

# Check if model files exist
if [ ! -f "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf" ]; then
    echo "⚠️  Warning: Mistral model not found in models/"
    echo "Please download mistral-7b-instruct-v0.2.Q4_K_M.gguf and place it in the models/ directory"
fi

if [ ! -f "models/codellama-7b.Q4_K_M.gguf" ]; then
    echo "⚠️  Warning: CodeLlama model not found in models/"
    echo "Please download codellama-7b.Q4_K_M.gguf and place it in the models/ directory"
fi

# Create necessary directories
mkdir -p data/vectors/chroma
mkdir -p data/resumes
mkdir -p data/job_descriptions

# Start the application
echo "🎯 Starting API server..."
python main.py &

# Wait for server to start
sleep 10

# Run tests
echo "🧪 Running test suite..."
python test_system.py

echo "✅ SmartRecruit AI is ready!"
echo "📡 API available at: http://localhost:8000"
echo "📚 Documentation at: http://localhost:8000/docs"