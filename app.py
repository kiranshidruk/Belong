from flask import Flask, jsonify
from openai import OpenAI

client = OpenAI(api_key='sk-proj-p3EEROJCdAMdgcapJ0ZaT3BlbkFJL2PCjLlsCVGlvdvZ0b9z')


app = Flask(__name__)

@app.route("/")
def home():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert lawyer, especially in the manners of US immigration. You will provide legal advice for users"},
            {"role": "user", "content": "I am struggling with filling in my student application and I don't know where to start"}
        ]
    )
    
    # Extract the message content from the completion
    message_content = completion.choices[0].message.content
    
    # Return the message content directly as a response
    return message_content

if __name__ == '__main__':
    app.run(debug=True)