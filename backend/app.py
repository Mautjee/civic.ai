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

client = Client("http://35.233.164.207:8080")

model = SentenceTransformer('all-MiniLM-L6-v2')

app = Flask(__name__)
CORS(app)

def call_generate_feedbacks():
    try:
        response = requests.get("http://35.233.164.207:3000/generate-feedbacks")
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

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    if not data or 'question' not in data:
        return jsonify({"error": "Invalid input. 'question' is required."}), 400

    question = data['question']
    query_embedding = model.encode(question).tolist()
    result = client.query.get("Feedbacks", ["text", "timestamp"]).with_near_vector({
        "vector": query_embedding,
        "certainty": 0.7
    }).with_limit(5).do()

    if result and result['data']['Get']['Feedbacks']:
        all_feedbacks_text = " | ".join([feedback['text'] for feedback in result['data']['Get']['Feedbacks']])

        preprompt = """
            Answer the question with a concise summary, and using the feedback as context.
            """
        template = """
            {preprompt}

            Question: {question}
            Feedback: {feedback}
            """
        prompt_template = PromptTemplate(input_variables=["preprompt", "question", "feedback"], template=template)
        prompt = prompt_template.format(preprompt=preprompt, question=question, feedback=all_feedbacks_text)
        llm = ChatOpenAI(model="gpt-4o-mini")
        chain = LLMChain(llm=llm, prompt=prompt_template)
        output = chain.run({"preprompt": prompt, "question": question, "feedback": all_feedbacks_text})
        return jsonify({"status": 200, "message": output})
    return jsonify({"status": 200, "message": "No similar reviews found."})

@app.route('/latest-feedback', methods=['GET'])
def get_latest_feedback():
    result = client.query.get(
        "Feedbacks", 
        ["text", "timestamp"]
    ).with_sort(
        {"path": ["timestamp"], "order": "desc"}
    ).with_limit(1).do()

    if result and result['data']['Get']['Feedbacks']:
        latest_feedback = result['data']['Get']['Feedbacks'][0]
        return jsonify({
            "status": 200,
            "message": latest_feedback['text'],
            "timestamp": latest_feedback['timestamp']
        })
    
    return jsonify({
        "status": 404,
        "message": "No feedback found"
    }), 404

if __name__ == '__main__':
    app.run(debug=True)