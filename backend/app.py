from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_cors import CORS

from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from sentence_transformers import SentenceTransformer

import openai
import requests
import os
from weaviate import Client

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

client = Client("http://localhost:8080")

schema = {
    "classes": [
        {
            "class": "Feedbacks",
            "description": "A class to store user reviews with embeddings and timestamps",
            "properties": [
                {
                    "name": "text",
                    "dataType": ["text"],
                    "description": "The content of the user review"
                },
                {
                    "name": "timestamp",
                    "dataType": ["date"],
                    "description": "The time the review was submitted"
                }
            ]
        }
    ]
}

client.schema.create(schema)
model = SentenceTransformer('all-MiniLM-L6-v2')

app = Flask(__name__)
CORS(app)

def call_generate_feedbacks():
    try:
        response = requests.get("http://localhost:5000/generate-feedbacks")
        if response.status_code == 200:
            print("Feedback received.")
            if response.json().get("publish", True):
                tweet = response.json()["message"]
                # post_tweet(tweet)
        else:
            print(f"Error while generating feedback: {response.json()}")
    except Exception as e:
        print(f"Error while generating feedback: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(call_generate_feedbacks, 'interval', minutes=1)
scheduler.start()

@app.route('/feed-database', methods=['POST'])
def feed_database():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid input. 'message' is required."}), 400

    message = data['message']
    review_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    review_embedding = model.encode(message).tolist()

    client.data_object.create(
        {
            "text": message,
            "timestamp": review_timestamp
        },
        "Feedbacks",
        vector=review_embedding
    )

    return jsonify({"message": "Message added successfully."}), 201


@app.route('/generate-feedbacks', methods=['GET'])
def generate_feedbacks():

    result = client.query.get("Feedbacks", ["text"]).with_limit(1000).do()
    feedback_texts = [feedback['text'] for feedback in result['data']['Get']['Feedbacks']]
    all_feedbacks_text = " | ".join(feedback_texts)

    preprompt = """
    You are a reporter about the ETH global hackathon in bangkok. You have received feedback from your users about the event.
    Make a summary of the following feedbacks.
    each feedback is separated by a pipe (|) character.
    your summary should be concise in a tweet-like format, with a maximum of 280 characters.
    """

    template = """
    {preprompt}

    Feedbacks: {feedbacks}
    """

    prompt_template = PromptTemplate(input_variables=["preprompt", "feedbacks"], template=template)




    prompt = prompt_template.format(preprompt=preprompt, feedbacks=all_feedbacks_text)
    llm = ChatOpenAI(model="gpt-4o-mini")
    chain = LLMChain(llm=llm, prompt=prompt_template)
    output = chain.run({"preprompt": prompt, "feedbacks": all_feedbacks_text})


    return jsonify({"status": 200, "publish": True, "message": output})


if __name__ == '__main__':
    app.run(debug=True)