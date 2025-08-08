# Syberbyte Setup Instructions

A. Download and install vscode:
https://code.visualstudio.com/

B. Download and Install Docker Desktop and Select Windows Container instead of Wsl 2 integration During the setup:
https://docs.docker.com/desktop/

C. Download and Install Github Desktop and Login on it after installation:
https://desktop.github.com/download/

D. Download and Install Python3.11 from the Windows Store and tick the 'ADD PATH variables' option if it appears.

E. Start Both Docker and Github Desktop

F. Cloning:
1. Make a folder to store your project
2. Go to Github Desktop and From the Top right menu select 'File' and then select 'Clone repository'.
3. A dialog box will appear, select 'URL' from the options on this dialog box and in the 'Repository URL or GitHub usemame and repository' field paste the URL: https://github.com/Muhdshayan/Syberbyte.git
4. In the bottom of the box select the path of the folder you made to store your project.
5. Click Clone and wait for it to complete.
6. Now from the options click 

. ## Backend/Frontend Code Setup

1. Run the following command:
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
