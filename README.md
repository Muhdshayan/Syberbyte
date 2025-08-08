# Syberbyte Setup Instructions


## Installation Process:

A. Download and install vscode:
https://code.visualstudio.com/

B. In the windows search bar search turn windows features on or off and click on it when the option appears, the tick all of the following features:
1. Containers
2. Hyper-V
3. Windows Hypervisor Platform
4. Virtual Machine Platform
click ok and then restart the device.

Note: If this fails enable Virtualization from the bios. 


C. Download and Install Docker Desktop and Select Windows Container instead of Wsl 2 integration During the setup:
https://docs.docker.com/desktop/

D. Download and Install Github Desktop and Login on it after installation:
https://desktop.github.com/download/

E. Download and Install Python3.11 from the Windows Store and tick the 'ADD PATH variables' option if it appears.

F. Start Both Docker Desktop and Github Desktop applications.

G. Cloning:
1. Make a folder to store your project
2. Go to Github Desktop and From the Top right menu select 'File' and then select 'Clone repository'.
3. A dialog box will appear, select 'URL' from the options on this dialog box and in the 'Repository URL or GitHub usemame and repository' field paste the URL: https://github.com/Muhdshayan/Syberbyte.git
4. In the bottom of the box select the path of the folder you made to store your project.
5. Click Clone and wait for it to complete.
6. Now from the options on github desktop click open in visual studio code.
7. From the options in the top of vs code click on 'View' and then 'Terminal' and wait for the terminal to load.

## Backend/Frontend Code Setup

1. In the terminal write the following command:
   ```bash
   cd Application
   ```
2. Then Run the following command:
   ```bash
   docker compose up --watch --build
   ```
and wait for everything to load (takes about 5-10 mins)
## AI/ML Code Setup

1. In the terminal header click on the '+' option and a new terminal is created.

2. In this new terminal navigate to the 'AI_Module' directory using the command
   ```bash
   cd AI_Module
   ```
3. Then Run the following command:
   ```bash
   docker compose up --build
   ```
4. In the project folder create a new folder named 'models'.   
5. Download the Mistral model from: https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF?show_file_info=Mistral-7B-Instruct-v0.3-Q3_K_M.gguf and place it in that folder.
6. In the terminal header click on the '+' option and a new terminal is created.
7. In this new terminal run:
   ```bash
   docker cp "models\Mistral-7B-v0.3.Q3_K_M.gguf" ollama:/models/
   ```
8. 2. In this new terminal navigate to the 'AI_Module' directory using the command
   ```bash
   cd AI_Module
   ```
10. Then in the  Run the following command to create the model configuration: 
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
11. Create the Mistral model:
   ```bash
   ollama create mistral -f /tmp/Modelfile-mistral
   ```
11. Exit the container:
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
