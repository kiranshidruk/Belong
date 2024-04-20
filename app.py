from flask import Flask, request, render_template, session
from flask_session import Session
from openai import OpenAI

client = OpenAI(api_key='sk-proj-p3EEROJCdAMdgcapJ0ZaT3BlbkFJL2PCjLlsCVGlvdvZ0b9z')

app = Flask(__name__)
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

system_prompt = "Hello! I am an expert Lawyer specializing in immigration. Which immigration form are you looking to fill out today?"


@app.route("/")
def home():
    session.clear()  # Clear any existing session
    # Set an initial system prompt for greeting
    session['history'] = [
        {"role": "system", "content": "The user is accessing the immigration form assistance service. Begin with a greeting and ask which form they need help with."}
    ]
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def chat():
    user_prompt = request.form['prompt'].strip()
    session['history'].append({"role": "user", "content": user_prompt})

    # Decide what system prompt to add based on user input
    determine_next_prompt(user_prompt)

    # Generate response using OpenAI
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=session['history']
    )

    bot_response = completion.choices[0].message.content
    session['history'].append({"role": "assistant", "content": bot_response})

    return bot_response

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

if __name__ == '__main__':
    app.run(debug=True)