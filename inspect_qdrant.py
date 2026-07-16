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
    # 1. Connect to Qdrant
    if not settings.QDRANT_URL or not settings.QDRANT_API_KEY:
        print("Error: QDRANT_URL or QDRANT_API_KEY is not set in settings or .env file.")
        sys.exit(1)

    print("Connecting to Qdrant...")
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY
    )

    collection_name = "enterprise_documents"

    # Verify if collection exists
    try:
        if not client.collection_exists(collection_name=collection_name):
            print(f"Collection '{collection_name}' does not exist.")
            sys.exit(0)
    except AttributeError:
        # Fallback for older client versions
        try:
            client.get_collection(collection_name=collection_name)
        except Exception:
            print(f"Collection '{collection_name}' does not exist.")
            sys.exit(0)

    # 2. Read all points from the collection
    print(f"Fetching points from collection '{collection_name}'...")
    try:
        # Scroll through points (limit=100 for safety, can page if needed)
        response = client.scroll(
            collection_name=collection_name,
            limit=100,
            with_payload=True,
            with_vectors=False
        )
        points, _ = response
    except Exception as e:
        print(f"Error fetching points: {e}")
        sys.exit(1)

    if not points:
        print("No points found in collection.")
        sys.exit(0)

    print(f"Found {len(points)} points. Displaying details:\n")

    # 3. Print details for every point
    for point in points:
        payload = point.payload or {}
        text = payload.get("text", "")
        # First 80 characters of text
        preview = text[:80]

        print("---------------------------------")
        print(f"Point ID: {point.id}")
        print(f"tenant_id: {payload.get('tenant_id')}")
        print(f"document_id: {payload.get('document_id')}")
        print(f"page: {payload.get('page')}")
        print(f"chunk_number: {payload.get('chunk_number')}")
        print(f"original_filename: {payload.get('original_filename')}")
        print(f"First 80 characters of text: {preview}")

    print("---------------------------------")

if __name__ == "__main__":
    main()
