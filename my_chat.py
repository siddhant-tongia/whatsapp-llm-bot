
from dotenv import load_dotenv
from openai import OpenAI
import os
import json

load_dotenv()

# create Gemini client using OpenAI compatibility and environment variable
client = OpenAI(
    api_key = os.getenv("API_KEY"),
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)
# This take the input from the user. And send somewhere and get something back called responce.

# I send the message to openai that message has the role : "user", content is something that user typed and then store that come back as a responce then print it.
messages = []
while True:
    user_input = input("You: ")
    
    if(user_input == "quit"):
        with open("chat_history.json","w") as f:
            json.dump(messages,f,indent=4)
        break

    else:
        messages.append({"role": "user" , "content": user_input})
        response = client.chat.completions.create(
            model = "gemini-1.5-flash",
            messages = messages
        )
        messages.append({"role": "assistant" , "content": response.choices[0].message.content})

        print("Assistant:", response.choices[0].message.content)

# while True:
    # take user_input
    # if user_input == "quit" : break
    # send to API
    # print the response


