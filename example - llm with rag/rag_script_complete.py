# --- Imports ---
# Used for exiting the script cleanly
import sys

# Used for interacting with the file system (listing directories)
import os

# For splitting text into smaller chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from langchain_huggingface import HuggingFaceEmbeddings

# For storing text chunks and their embeddings, allowing efficient search

# The Ollama language model
from langchain_ollama import OllamaLLM

# The prompt template structures how we ask the LLM
from langchain_core.prompts import ChatPromptTemplate

# Native PDF parsing
from pypdf import PdfReader

# --- Configuration ---
SOURCE_DIRECTORY = "source_docs"
CHUNK_SIZE = 500  # How many characters per text chunk
CHUNK_OVERLAP = 50  # How much overlap between chunks
RETRIEVAL_K = 5
EMBEDDING_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"  # Good default embedding model
)
OLLAMA_MODEL = "phi4-mini"

print(f"Using Ollama model: {OLLAMA_MODEL}")
print(f"Make sure Ollama is running and the model '{OLLAMA_MODEL}' is available.")


def load_pdf_text(pdf_path):
    pdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(pdf_path).pages)
    return pdf_text.strip()


def format_context(documents):
    formatted_chunks = []
    for doc in documents:
        source_name = os.path.basename(doc.metadata.get("source", "Unknown"))
        formatted_chunks.append(f"Source: {source_name}\n{doc.page_content}")

    return "\n\n".join(formatted_chunks)


# --- 1. Load Documents from Directory ---
print(f"Looking for PDF documents in: {SOURCE_DIRECTORY}")
# Check if the source directory exists
if not os.path.isdir(SOURCE_DIRECTORY):
    print(f"Error: Source directory '{SOURCE_DIRECTORY}' not found.")
    print("Please create the directory and add your PDF files.")
    sys.exit(1)

pdf_texts = []  # Initialize an empty list to hold the text from each PDF
pdf_metadatas = []
pdf_files_found = []  # Keep track of files to be processed

# Find all PDF files in the specified directory
try:
    for filename in os.listdir(SOURCE_DIRECTORY):
        if filename.lower().endswith(".pdf"):
            full_path = os.path.join(SOURCE_DIRECTORY, filename)
            pdf_files_found.append(full_path)
except Exception as e:
    print(f"Error reading source directory '{SOURCE_DIRECTORY}': {e}")
    sys.exit(1)

if not pdf_files_found:
    print(f"No PDF files found in '{SOURCE_DIRECTORY}'.")
    sys.exit(1)

print(f"Found {len(pdf_files_found)} PDF file(s). Loading...")

# Load each PDF file found
for pdf_path in pdf_files_found:
    try:
        print(f"  Loading: {os.path.basename(pdf_path)}")  # Show which file is loading
        pdf_text = load_pdf_text(pdf_path)
        if not pdf_text:
            print(
                f"  Warning: No content loaded from '{os.path.basename(pdf_path)}'. Skipping."
            )
            continue
        pdf_texts.append(pdf_text)
        pdf_metadatas.append({"source": pdf_path})
        print("    -> Loaded text successfully.")
    except FileNotFoundError:
        # This shouldn't happen if os.listdir worked, but good practice
        print(f"  Error: File not found at '{pdf_path}'. Skipping.")
    except Exception as e:
        # Catch errors during loading/parsing of a specific PDF
        print(f"  Error loading PDF '{os.path.basename(pdf_path)}': {e}. Skipping.")

# Check if any documents were loaded successfully overall
if not pdf_texts:
    print("\nError: No documents were successfully loaded from any PDF files.")
    sys.exit(1)

print(
    f"\nSuccessfully loaded content from {len(pdf_texts)} PDF(s)."
)

# --- 2. Split the Document into Chunks ---
print(
    f"Splitting {len(pdf_texts)} PDF(s) into chunks (size: {CHUNK_SIZE}, overlap: {CHUNK_OVERLAP})..."
)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
)
# Create smaller pieces of text from the loaded PDFs
split_chunks = text_splitter.create_documents(pdf_texts, metadatas=pdf_metadatas)
if not split_chunks:
    print("Error: Failed to split the documents into chunks.")
    sys.exit(1)
print(f"Documents split into {len(split_chunks)} chunks.")

# --- 3. Create Embeddings and Vector Store ---
# Embeddings turn text into numbers (vectors) so we can find similar chunks
print(f"Initializing embedding model: {EMBEDDING_MODEL_NAME}...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

print("Creating vector store (this might take a moment)...")
# Chroma is a vector store.
vector_store = Chroma.from_documents(
    documents=split_chunks, embedding=embeddings
)
print("Vector store created.")

# --- 4. Initialize the LLM ---
print(f"Initializing Ollama LLM ('{OLLAMA_MODEL}')...")
try:
    llm = OllamaLLM(model=OLLAMA_MODEL)
    # Optional: A quick test to see if Ollama connection works
    # llm.invoke("hello")
except Exception as e:
    print(f"\nError initializing Ollama: {e}")
    print("Is the Ollama application running? Is the model '{OLLAMA_MODEL}' pulled?")
    sys.exit(1)
print("LLM initialized.")

# --- 5. Configure Retrieval and Prompting ---

# Define the Prompt Template:
# This tells the LLM how to structure its answer using the retrieved context.
# '{context}' will be filled with relevant text chunks.
# '{input}' will be the user's question.
prompt_template = """
You are an assistant answering questions based *only* on the provided context.
If the answer is not in the context, say you don't know. Be concise.

Context:
{context}

Question:
{input}

Answer:
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

# Create the Retriever:
# This object knows how to fetch relevant chunks from the vector store.
retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": RETRIEVAL_K},
)

print("\nRAG system ready!")

# --- 6. Ask Questions ---
while True:
    try:
        # Get input from the user
        query = input("\nEnter your question (or type 'exit' to quit): ")

        # Allow the user to exit
        if query.lower() == "exit":
            break
        if not query.strip():  # Handle empty input
            print("Please enter a question.")
            continue

        print("Thinking...")

        retrieved_docs = retriever.invoke(query)
        context = format_context(retrieved_docs)
        prompt_value = prompt.invoke(
            {
                "context": context or "No relevant context was retrieved.",
                "input": query,
            }
        )
        answer = llm.invoke(prompt_value)

        # Print the LLM's answer
        print("\nAnswer:", answer)

        # Optional: Print the source chunks used (for debugging/understanding)
        # print("\nSources used:")
        # for i, doc in enumerate(retrieved_docs):
        #     source_name = doc.metadata.get('source', 'Unknown')
        #     print(f"  {i+1}. File: {os.path.basename(source_name)}")
        #     # print(f"     Content: {doc.page_content[:150]}...") # Print start of chunk content

        print("-" * 50)  # Add a separator line

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    except KeyboardInterrupt:  # Allow Ctrl+C to exit gracefully
        print("\nExiting...")
        break

print("Goodbye!")
