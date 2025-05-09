import chromadb

# Create a persistent ChromaDB client
chroma_client = chromadb.PersistentClient(path="chroma_db")


# Function to get or create a collection for a lecture
def get_chroma_collection(lecture_id: int):
    return chroma_client.get_or_create_collection(f"lecture_{lecture_id}")
