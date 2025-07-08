# German-Podcast-Transcriber
German Podcast Transcriber is a web application that uses Python's Flask framework along with HTML,CSS and JavaScript to allow users to transcribe German audios (podcasts or songs) locally. The underlying AI model used is OpenAI's whisper model that provides a transcription of the uploaded audio. There is also functionality of a vocabulary, in which words can be stored at any time and are translated into English for reference. Apart from this, this application also has all the standard functions of a standard audio player (seeking, transcription syncing with audio, transcription being highlighted etc.) 

## Navigation
- [Usage](#usage)
- [Setup and Installation](#installation-and-setup)
- [Tech Stack and Acknowledgements](#tech-stack-and-acknowledgements)

# Usage 
The application is very user-friendly and navigation through it is self-explanatory. 
Note:
1. The 'k' and spacebar keys can be used for play/pause functionality.
2. MP3, WAV, and M4A formats are supported, though MP3 should work the best.
3. Since the model runs locally, the time taken for the transcription to be ready depends on the machine it is run on. For reference, a ~40 minute audio takes about 5 minutes on a 8gb ram M1 Macbook Air. Audios whose transcription is done can be accessed immediately.
4. The translations may not always be completely accurate. 

## Here are a few screenshots from the website: 
1. Library Page
 <img width="1440" alt="image" src="https://github.com/user-attachments/assets/1c39e1dc-ecea-4e23-a34e-9cd31f63f610" />
2. Player
 <img width="1440" alt="image" src="https://github.com/user-attachments/assets/bdba670b-4795-4c7a-8de2-90cd5cba0570" />
3. Options after selecting words
 <img width="1440" alt="image" src="https://github.com/user-attachments/assets/8f49f335-b33f-4f10-aaa8-70534fc87e23" />
4. Vocabulary Page
 <img width="1440" alt="image" src="https://github.com/user-attachments/assets/37fad0b1-700f-4ae9-86a1-12b1bc9869b2" />
 
# Installation and Setup
1. Clone the repository, or download the zip file and unzip it.
2. Create a virtual environment and activate it
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3. Install required packages
    ```bash
    pip install -r requirements.txt
    ```
    Note: This includes 'torch' and 'whisper'. First run may take some time to download the whisper model weights.
4. Set Environment Variables
   First generate a secure secret key.
   ```bash
    python -c "import secrets; print(secrets.token_hex(16))"
    ```
    Copy the result. Then run the following code:
   ```bash
    # On Windows 
    set FLASK_APP=run.py
    set SECRET_KEY=copied-result-generated-above

    # On macOS/Linux 
    export FLASK_APP=run.py
    export SECRET_KEY=copied-result-generated-above
    ```
5. Initialize the database
   ```bash
    python -m flask init-db
    ```
6. Running the application
   ```bash
    python -m flask run
    ```
# Tech Stack and Acknowledgements
This project was made possible by a number of powerful and open-source libraries and freely available APIs. 

## Core Backend
* **Python**
* **[Flask](https://flask.palletsprojects.com/):** Lightweight micro Python web framework used to be build webservers and handle API requests 
* **[SQLAlchemy](https://www.sqlalchemy.org/):** Database toolkit used for ORM to interact with SQLite Database

## Audio Processing 
* **[OpenAI Whisper](https://github.com/openai/whisper)**: The model at the core of the application which transcribes the provided audio with time-stamps
* **[pydub](https://github.com/jiaaro/pydub):** Crucial library for manipuation of audio files

## Frontend
* HTML,CSS, and JavaScript

## External Services and APIs
* **[Free Dictionary API](https://dictionaryapi.dev/):** Used to provide detailed definitions and translations
* **[Deep-Translator](https://pypi.org/project/deep-translator/):** Used as a fallback to provide simple English Translations when primary dictionary API is unavailable.

