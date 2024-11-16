import weaviate
from sentence_transformers import SentenceTransformer

client = weaviate.Client("http://localhost:8080")
model = SentenceTransformer('all-MiniLM-L6-v2')  # You can choose other models as well
query_text = "I love this product, it's amazing!"

query_embedding = model.encode(query_text).tolist()
result = client.query.get("Feedbacks", ["text", "timestamp"]).with_near_vector({
    "vector": query_embedding,
    "certainty": 0.7  # Adjust certainty as needed
}).with_limit(1).do()

# Print the closest review
if result and result['data']['Get']['Feedbacks']:
    closest_review = result['data']['Get']['Feedbacks'][0]
    print("Closest Review:")
    print("Text:", closest_review['text'])
    print("Timestamp:", closest_review['timestamp'])
else:
    print("No similar reviews found.")