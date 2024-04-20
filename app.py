from flask import Flask, request, render_template
from openai import OpenAI

client = OpenAI(api_key='sk-proj-p3EEROJCdAMdgcapJ0ZaT3BlbkFJL2PCjLlsCVGlvdvZ0b9z')

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def chat():
    # Get user prompt from the form
    user_prompt = request.form['prompt']
    
    # Use GPT to generate a response
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    
    # Extract the message content from the completion
    bot_response = completion.choices[0].message.content
    
    # Return the bot response
    return bot_response

if __name__ == '__main__':
    app.run(debug=True)
