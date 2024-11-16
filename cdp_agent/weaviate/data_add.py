import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer

import weaviate

client = weaviate.Client("http://localhost:8080")

model = SentenceTransformer('all-MiniLM-L6-v2')  # You can choose other models as well

# Example review data

review_texts = [
    "Great product, highly recommend!",
    "not good, stupid!"
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
