from openai import OpenAI

client = OpenAI(api_key='sk-proj-p3EEROJCdAMdgcapJ0ZaT3BlbkFJL2PCjLlsCVGlvdvZ0b9z')

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are an expert lawyer, especially in the manners of US immigration. You will provide legal advice for users"},
    {"role": "user", "content": "I am struggling with filling in my student application and I don't know where to start"}
  ]
)

print(completion.choices[0].message)
pass


# defaults to getting the key using os.environ.get("OPENAI_API_KEY")
# if you saved the key under a different environment variable name, you can do something like:
# client = OpenAI(
#   api_key=os.environ.get("CUSTOM_ENV_NAME"),
# )