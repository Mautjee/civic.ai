import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer

import weaviate

client = weaviate.Client("http://localhost:8080")

model = SentenceTransformer('all-MiniLM-L6-v2')  # You can choose other models as well

# Example review data

review_texts = [
    "Had an amazing time at ETH Global Bangkok, really well organized and informative!",
    "Great opportunity to network with talented developers at ETH Global Bangkok.",
    "Not the best experience. The event could have been better organized.",
    "I learned a lot from the workshops and the speakers were really inspiring!",
    "The venue was fantastic, perfect for such a big event. Highly recommend attending next time.",
    "Disappointed with the overall management of the event. It lacked clear communication.",
    "ETH Global Bangkok was an excellent chance to work on cool projects with great teams!",
    "Great for developers looking to build on Ethereum, but could use more diversity in topics.",
    "One of the best hackathons I’ve attended, well worth the trip to Bangkok.",
    "I didn’t find the event useful for beginners, too advanced for me.",
    "Fantastic experience, met so many amazing people from all over the world.",
    "ETH Global Bangkok exceeded my expectations. Can’t wait for the next event!",
    "I didn’t get as much out of the event as I had hoped. Too much focus on advanced topics.",
    "Such a great community at ETH Global Bangkok. Everyone was super friendly and helpful!",
    "The food and facilities were top-notch, definitely a great setting for the hackathon.",
    "Not very engaging. I expected more hands-on sessions and fewer talks.",
    "It was an awesome experience to be surrounded by so many passionate developers!",
    "The event was a bit too big, hard to connect with people in such a crowded space.",
    "ETH Global Bangkok was a great opportunity to collaborate with talented developers from around the globe.",
    "If you’re serious about blockchain development, this is the event to attend!"
]


for review_text in review_texts:
    review_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    review_embedding = model.encode(review_text).tolist()

    # Add the review to Weaviate
    client.data_object.create(
        {
            "text": review_text,
            "timestamp": review_timestamp
        },
        "Feedbacks",
        vector=review_embedding
    )
