from weaviate import Client

client = Client("http://localhost:8080")

# Define the schema
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

# Create the schema in Weaviate
client.schema.create(schema)
