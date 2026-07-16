import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup basic logging configuration to suppress info noise from httpx
logging.basicConfig(level=logging.WARNING)

# Ensure app modules can be imported by adding the project root to sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load .env variables
load_dotenv()

from qdrant_client import QdrantClient
from app.core.config import settings

def main():
    # 1. Connect to Qdrant using settings
    if not settings.QDRANT_URL or not settings.QDRANT_API_KEY:
        print("Error: QDRANT_URL or QDRANT_API_KEY is not set in settings or .env file.")
        sys.exit(1)

    print("Connecting to Qdrant...")
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY
    )

    # 2. List all collections
    try:
        collections_response = client.get_collections()
    except Exception as e:
        print(f"Error listing collections: {e}")
        sys.exit(1)

    # 3. Print the collection names
    print("\nCollections found in Qdrant:")
    collections = collections_response.collections
    if not collections:
        print("No collections found.")
    else:
        for col in collections:
            print(f"- {col.name}")

    # 4. For the enterprise_documents collection, print:
    #    - Number of points
    #    - Vector size
    #    - Distance metric
    collection_name = "enterprise_documents"
    print(f"\nDetails for collection '{collection_name}':")
    try:
        info = client.get_collection(collection_name=collection_name)
        print(f"  Number of points: {info.points_count}")
        
        # Extract vector config details
        vectors_config = info.config.params.vectors
        if hasattr(vectors_config, 'size'):
            # Single vector configuration
            vector_size = vectors_config.size
            distance = vectors_config.distance
        elif isinstance(vectors_config, dict):
            # Named vectors configuration
            vector_size = {k: v.size for k, v in vectors_config.items()}
            distance = {k: v.distance for k, v in vectors_config.items()}
        else:
            vector_size = getattr(vectors_config, 'size', 'Unknown')
            distance = getattr(vectors_config, 'distance', 'Unknown')

        print(f"  Vector size: {vector_size}")
        print(f"  Distance metric: {distance}")

    except Exception as e:
        print(f"  Error: Could not retrieve info for '{collection_name}': {e}")

if __name__ == "__main__":
    main()
