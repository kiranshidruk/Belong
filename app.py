from flask import Flask, request, render_template, session
from flask_session import Session
from openai import OpenAI

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
Once all necessary information is collected, You will be ready to write the first page of the user's application, and you will communicate that with the user. 
You will rewrite each of those fields but filled in with the user information:
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