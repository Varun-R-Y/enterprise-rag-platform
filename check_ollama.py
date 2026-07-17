import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure app modules can be imported
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

load_dotenv()

# Setup logging to output INFO
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

from app.services.llm.ollama_service import OllamaService


async def main():
    print("Initializing OllamaService...")
    ollama_service = OllamaService()

    prompt = (
        "You are an enterprise knowledge assistant.\n\n"
        "Context:\n"
        "Employees receive 12 casual leave days annually.\n\n"
        "Question:\n"
        "How many casual leave days do employees receive?"
    )

    print("\n--- Sending Prompt to Ollama ---")
    print(prompt)
    print("--------------------------------\n")

    try:
        response = await ollama_service.generate(prompt)
        print("\n--- Received Response ---")
        print(response)
        print("-------------------------\n")
    except Exception as e:
        print(f"\nError occurred during Ollama generation: {e}")
        print("Please ensure that Ollama is running locally and the model is downloaded.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
