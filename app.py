from flask import Flask, request, render_template, session
from flask_session import Session
from openai import OpenAI

client = OpenAI(api_key='sk-proj-p3EEROJCdAMdgcapJ0ZaT3BlbkFJL2PCjLlsCVGlvdvZ0b9z')

app = Flask(__name__)
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def home():
    session.clear()  # Clear any existing session on new entry to the home page
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def chat():
    # Get user prompt from the form
    user_prompt = request.form['prompt']
    
    # Initialize or extend the conversation history
    if 'history' not in session:
        session['history'] = []
    session['history'].append({"role": "user", "content": user_prompt})
    
    # Use GPT to generate a response with the full conversation history
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=session['history']
    )
    
    # Extract the message content from the completion and store it
    bot_response = completion.choices[0].message.content
    session['history'].append({"role": "assistant", "content": bot_response})
    
    # Return the bot response
    return bot_response

if __name__ == '__main__':
    app.run(debug=True)