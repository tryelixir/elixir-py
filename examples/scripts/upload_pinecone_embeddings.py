import openai
from pinecone import Pinecone
import os

# Set your OpenAI API key and Pinecone API key
openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")

# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))


def main():
    # Define the text to be uploaded
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "assets/insurance.txt")
    with open(file_path, "r") as file:
        text = file.read()

    # Split the text into sections for better granularity
    sections = text.split("\n\n")

    # Generate embeddings for each section using OpenAI
    embeddings = []
    for section in sections:
        response = openai.embeddings.create(
            model="text-embedding-ada-002", input=section
        )
        embeddings.append(response.data[0].embedding)

    # Connect to Pinecone and create a new index
    index_name = "insurance-embeddings"

    # Connect to the index
    index = pc.Index(index_name)

    # Upload the embeddings to Pinecone
    for i, embedding in enumerate(embeddings):
        index.upsert([(str(i), embedding, {"text": sections[i]})])

    print("Embeddings uploaded successfully!")


if __name__ == "__main__":
    main()
