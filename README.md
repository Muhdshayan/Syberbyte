# Syberbyte Setup Instructions

## Backend/Frontend Code Setup

1. Run the following command:
   ```bash
   git clone https://github.com/Muhdshayan/Syberbyte.git
   ```
2. Navigate to the Syberbyte directory
3. Run the following command:
   ```bash
   git checkout -b Backend/Hamza origin/Backend/Hamza
   ```
4. Run the following command:
   ```bash
   docker compose up --watch --build
   ```

## AI/ML Code Setup

### Terminal 1 - Docker Compose Setup

1. Run the following command:
   ```bash
   git clone https://github.com/Muhdshayan/Syberbyte.git
   ```
2. Navigate to the Syberbyte directory
3. Run the following command:
   ```bash
   git checkout -b Ai/Wisam origin/Ai/Wisam
   ```
4. Navigate to the `CV_Scoring` directory
4. Run the following command:
   ```bash
   docker compose up --build
   ```
5. Download the Mistral model from: [https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf)
6. Place the downloaded model file in `CV_Scoring/models` directory
7. Open another PowerShell terminal and run:
   ```bash
   docker exec -it ollama bash
   ```
8. Run the following command to create the model configuration:
   ```bash
   cat > /tmp/Modelfile-mistral <<EOF
   FROM /models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
   TEMPLATE """<s>[INST] {{ .Prompt }} [/INST]"""
   PARAMETER temperature 0.1
   PARAMETER top_p 0.9
   PARAMETER stop "</s>"
   PARAMETER stop "[/INST]"
   PARAMETER stop "[INST]"
   PARAMETER num_predict 200
   EOF
   ```
9. Create the Mistral model:
   ```bash
   ollama create mistral -f /tmp/Modelfile-mistral
   ```
10. Exit the container:
   ```bash
   exit
   ```

### Terminal 2 - Python Setup

1. Install spaCy:
   ```bash
   pip install spacy
   ```
2. Download the English language model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
3. Install requirements:
   ```bash
   pip install -r server.txt
   ```
4. Run the application:
   ```bash
   python run_both.py
   ```
