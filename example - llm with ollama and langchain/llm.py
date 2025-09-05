# --- Core LangChain Component ---
# We only need the Ollama integration
from langchain_ollama import OllamaLLM as Ollama

# --- Configuration ---
# Specify the Ollama model you want to use
# Make sure you have pulled this model with 'ollama pull phi4-mini'
OLLAMA_MODEL = "phi4-mini"

print("--- Simple LLM Query Script ---")
print(f"Using Ollama model: {OLLAMA_MODEL}")

# --- 1. Initialize LLM ---
print("Initializing LLM...")
# This creates an object to interact with the specified Ollama model
# It assumes Ollama is running locally on the default port
try:
    llm = Ollama(model=OLLAMA_MODEL)
    # Optional: Do a quick test invocation to ensure connection
    # print(llm.invoke("Hello!"))
    print("LLM initialized successfully.")
except Exception as e:
    print(f"\nError initializing Ollama LLM: {e}")
    print(f"Please ensure Ollama is running and the model '{OLLAMA_MODEL}' is pulled.")
    print(
        f"You can run Ollama and then use 'ollama pull {OLLAMA_MODEL}' in your terminal."
    )
    exit()  # Stop the script if LLM initialization fails

print("\nLLM ready!")

# --- 2. Ask Questions Loop ---
while True:
    # Prompt the user for input
    query = input("\nEnter your prompt (or type 'exit' to quit): ")

    # Check if the user wants to exit
    if query.lower() == "exit":
        break

    # Make sure the input is not empty
    if not query.strip():
        continue

    print("Thinking...")
    try:
        # Send the user's query directly to the LLM
        response = llm.invoke(query)

        # Print the LLM's response
        print("\nResponse:")
        print(response)
        print("-" * 50)

    except Exception as e:
        print(f"\nAn error occurred while getting the response: {e}")
        # You might want to add more specific error handling here
        # For now, we just continue the loop
        continue

print("Goodbye!")
