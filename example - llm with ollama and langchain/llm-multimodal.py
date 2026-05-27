# --- Core LangChain Components ---
# We need ChatOllama for image+text and HumanMessage for input structure
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# --- Standard Python Libraries ---
import base64
import os
from pathlib import Path

# --- Configuration ---
# Specify the Ollama MULTIMODAL model you want to use
# Make sure you have pulled this model with 'ollama pull gemma4:e2b'
OLLAMA_MODEL = "gemma4:e2b"

print("--- Multimodal LLM Image Analysis ---")
print(f"Using Ollama model: {OLLAMA_MODEL}")

# --- 1. Initialize Multimodal LLM ---
print("Initializing Multimodal LLM...")
# This creates an object to interact with the specified Ollama model
# It assumes Ollama is running locally on the default port
try:
    # Use ChatOllama for models that accept images
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        # Optional: Adjust temperature (creativity vs. factuality)
        # temperature=0.8,
    )
    print("Multimodal LLM initialized successfully.")
except Exception as e:
    print(f"\nError initializing Ollama Multimodal LLM: {e}")
    print(f"Please ensure Ollama is running and the model '{OLLAMA_MODEL}' is pulled.")
    print(
        f"You can run Ollama and then use 'ollama pull {OLLAMA_MODEL}' in your terminal."
    )
    exit()  # Stop the script if LLM initialization fails

print("\nMultimodal LLM ready!")


# --- Helper Function to Encode Image ---
def encode_image(image_path):
    """Reads an image file and returns its base64 encoded string."""
    try:
        path = Path(image_path)
        if not path.is_file():
            print(f"Error: Image file not found at '{image_path}'")
            return None

        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")
            # Determine image type (basic check)
            # You might want more robust MIME type detection if needed
            mime_type = "image/jpeg"  # Default assumption
            if path.suffix.lower() == ".png":
                mime_type = "image/png"
            elif path.suffix.lower() in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            elif path.suffix.lower() == ".webp":
                mime_type = "image/webp"
            # Add more types if necessary (gif, etc.)

            # Format needed for ChatOllama image input
            return f"data:{mime_type};base64,{encoded}"

    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'")
        return None
    except Exception as e:
        print(f"Error encoding image '{image_path}': {e}")
        return None


# --- 2. Ask Questions Loop ---
while True:
    # Prompt the user for the image path
    image_path_input = input(
        "\nEnter the path to your image (or type 'exit' to quit): "
    )

    # Check if the user wants to exit
    if image_path_input.lower() == "exit":
        break

    # Make sure the input is not empty
    if not image_path_input.strip():
        continue

    # Encode the image
    image_base64 = encode_image(image_path_input)

    # If encoding failed (e.g., file not found), loop again
    if image_base64 is None:
        continue

    # Prompt the user for the text question about the image
    text_query = input("Enter your question about the image: ")

    # Make sure the text query is not empty (optional, depends on use case)
    if not text_query.strip():
        print("Please enter a question about the image.")
        continue

    print("\nAnalyzing image and thinking...")
    try:
        # --- Construct the Multimodal Message ---
        # Use HumanMessage with a list of content parts (text and image)
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": text_query,
                },
                {
                    "type": "image_url",
                    "image_url": {"url": image_base64},  # Use the base64 encoded string
                },
            ]
        )

        # Send the combined message to the LLM
        # Note: invoke expects the structured message
        response = llm.invoke([message])  # Pass message inside a list

        # Print the LLM's response
        print("\nResponse:")
        # The response object might be a message object, access its content
        if hasattr(response, "content"):
            print(response.content)
        else:
            # Fallback if the response structure is simpler (less common now)
            print(response)
        print("-" * 50)

    except Exception as e:
        print(f"\nAn error occurred while getting the response: {e}")
        # You might want to add more specific error handling here
        # For now, we just continue the loop
        continue

print("Goodbye!")
