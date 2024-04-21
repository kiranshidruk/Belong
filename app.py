from flask import Flask, request, render_template, session, send_file, jsonify
from flask_session import Session
from werkzeug.utils import secure_filename
from openai import OpenAI
from pydub import AudioSegment
from pathlib import Path
import os
import time

client = OpenAI(api_key='sk-proj-p3EEROJCdAMdgcapJ0ZaT3BlbkFJL2PCjLlsCVGlvdvZ0b9z')

app = Flask(__name__)
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

system_prompt = """
You are an expert Lawyer specializing in immigration. You will ask the user about which immigration form they are looking to fill out today.
 You will ask questions sequentially to collect all information about EACH OF THE FOLLOWING. You need to ONLY ask questions about those:
Alien Registration Number(s) (A-Number) (if any)
U.S. Social Security Number (if any)
USCIS Online Account Number (if any)
Complete Last Name
First Name
Middle Name
Other names used (include maiden name and aliases)
Residence in the U.S. (where you physically reside), including:
Street Number and Name
Apt. Number
City
State
Zip Code
Telephone Number
Mailing Address in the U.S. (if different than the address in item 8), including:
In Care Of (if applicable)
Street Number and Name
Apt. Number
City
State
Zip Code
Telephone Number
Gender (Male or Female)
Marital Status (Single, Married, Divorced, Widowed)
Date of Birth (mm/dd/yyyy)
City and Country of Birth
Present Nationality (Citizenship)
Nationality at Birth
Race, Ethnic, or Tribal Group
Religion
Once all necessary information is collected, You will be ready to write the first page of the user's application, and you will communicate that with the user. RESPOND IN THE LANGUAGE THE USER IS SPEAKING THEN finally you will 
You will rewrite each of those fields but filled in with the user information (IN ENGLISH):
Alien Registration Number(s) (A-Number) (if any) <user-parsed information>
U.S. Social Security Number (if any) <user-parsed information>
USCIS Online Account Number (if any) <user-parsed information>
Complete Last Name <user-parsed information>
First Name <user-parsed information>
Middle Name <user-parsed information>
Other names used (include maiden name and aliases) <user-parsed information>
Residence in the U.S. (where you physically reside), including: <user-parsed information>
Street Number and Name <user-parsed information>
Apt. Number <user-parsed information>
City <user-parsed information>
State <user-parsed information>
Zip Code <user-parsed information>
Telephone Number <user-parsed information>
Gender (Male or Female) <user-parsed information>
Marital Status (Single, Married, Divorced, Widowed) <user-parsed information>
Date of Birth (mm/dd/yyyy) <user-parsed information>
City and Country of Birth <user-parsed information>
Present Nationality (Citizenship) <user-parsed information>
Nationality at Birth <user-parsed information>
Race, Ethnic, or Tribal Group <user-parsed information>
Religion <user-parsed information>

"""


@app.route("/")
def home():
    session.clear()  # Clear any existing session
    # Set an initial system prompt for greeting
    session['history'] = [
        {"role": "system", "content": system_prompt}
    ]
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def chat():
    user_prompt = request.form['prompt'].strip()
    session['history'].append({"role": "user", "content": user_prompt})

    determine_next_prompt(user_prompt)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=session['history']
    )

    bot_response = completion.choices[0].message.content
    session['history'].append({"role": "assistant", "content": bot_response})

    # Convert the bot's response to speech
    speech_file_path = generate_speech(bot_response)

    return jsonify({
        'text': bot_response,
        'audio_url': '/audio/' + speech_file_path.name  # assuming the audio is accessible via a static path
    })

def generate_speech(text):
    timestamp = int(time.time())  # Get current time in seconds since epoch
    speech_file_path = Path(__file__).parent / f"speech_{timestamp}.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path

@app.route('/audio/<filename>')
def download_file(filename):
    return send_file(Path(__file__).parent / filename, as_attachment=True)

def determine_next_prompt(user_input):
    # Logic to add system prompts based on user input
    if 'asylum' in user_input.lower():
        add_system_prompt("The user is filling out an asylum application. Start by asking for their Alien Registration Number (A-Number), if any.")
    elif 'a-number' in user_input.lower():
        add_system_prompt("Ask for the user's U.S. Social Security Number next.")
    elif 'social security number' in user_input.lower():
        add_system_prompt("Next, ask for the user's USCIS Online Account Number.")
    # Extend with more checks and prompts as needed

def add_system_prompt(prompt):
    session['history'].append({"role": "system", "content": prompt})

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    # Define the directory for saving audio files
    upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    # Create the directory if it does not exist
    os.makedirs(upload_dir, exist_ok=True)

    if 'audio' in request.files:
        audio_file = request.files['audio']
        filename = secure_filename(audio_file.filename)  # Should now have .mp3 due to JS change
        save_path = os.path.join(upload_dir, filename)
        audio_file.save(save_path)

        # Convert webm to wav
        sound = AudioSegment.from_file(save_path, format="webm")
        wav_path = save_path.replace(".webm", ".wav")
        sound.export(wav_path, format="wav")

        # Now send the .wav file for transcription
        with open(wav_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=file
            )

        # Clean up files
       # os.remove(save_path)  # Clean up original file
        #os.remove(wav_path)   # Clean up converted file
        print(transcription.text)
        return {'transcription': transcription.text}

    return {'error': 'No audio file provided'}, 400

if __name__ == '__main__':
    app.run(debug=True)