#!/bin/bash

echo "🚀 Setting up Ollama with your local models..."

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to be ready..."
sleep 5

# Check if Ollama is responding
until curl -s http://localhost:11434/api/version > /dev/null 2>&1; do
    echo "Waiting for Ollama to start..."
    sleep 2
done

echo "✅ Ollama is ready!"

# Check what models you have
echo "📁 Found these model files:"
docker exec ollama ls -la /models/

# Create Mistral model
echo "📥 Creating Mistral model from your local file..."
docker exec ollama bash -c 'cat > /tmp/Modelfile-mistral << EOF
FROM /models/mistral-7b-instruct-v0.2.Q4_K_M.gguf

TEMPLATE """<s>[INST] {{ .Prompt }} [/INST]"""

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER stop "</s>"
PARAMETER stop "[/INST]"
PARAMETER stop "[INST]"
PARAMETER num_predict 200
EOF'

# Import Mistral
docker exec ollama ollama create mistral -f /tmp/Modelfile-mistral

# Create CodeLlama model  
echo "📥 Creating CodeLlama model from your local file..."
docker exec ollama bash -c 'cat > /tmp/Modelfile-codellama << EOF
FROM /models/codellama-7b.Q4_K_M.gguf

TEMPLATE """<s>[INST] {{ .Prompt }} [/INST]"""

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER stop "</s>"
PARAMETER stop "[/INST]"
PARAMETER stop "[INST]"
PARAMETER num_predict 200
EOF'

# Import CodeLlama
docker exec ollama ollama create codellama -f /tmp/Modelfile-codellama

# Verify models are created
echo "🔍 Verifying models..."
docker exec ollama ollama list

echo "🧪 Testing models..."

# Test Mistral
echo "Testing Mistral..."
docker exec ollama ollama run mistral "Hello! Just say 'Mistral ready' and nothing else." --verbose

# Test CodeLlama  
echo "Testing CodeLlama..."
docker exec ollama ollama run codellama "Hello! Just say 'CodeLlama ready' and nothing else." --verbose

echo "✅ Setup complete! Your models are ready."
echo "🔗 Ollama API available at: http://localhost:11434"
