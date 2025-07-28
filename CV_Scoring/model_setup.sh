
echo "python -m spacy download en_core_web_sm"

echo "🚀 Setting up Ollama with your local models..."

echo "📁 Found these model files:"
docker exec ollama ls -la /models/

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

docker exec ollama ollama create mistral -f /tmp/Modelfile-mistral

echo "🔍 Verifying models..."
docker exec ollama ollama list

echo "🧪 Testing models..."