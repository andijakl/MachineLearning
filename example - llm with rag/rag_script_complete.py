# --- Imports ---
# Used for exiting the script cleanly
import sys

# Used for interacting with the file system (listing directories)
import os

# For loading PDFs
from langchain_community.document_loaders import PyPDFLoader

# For splitting text into smaller chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter

# For creating numerical representations (embeddings) of text chunks
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

# For storing text chunks and their embeddings, allowing efficient search
from langchain_community.vectorstores import FAISS

# The Ollama language model
from langchain_ollama import OllamaLLM

# The prompt template structures how we ask the LLM
from langchain_core.prompts import ChatPromptTemplate

# Helper functions to create the RAG chain easily
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# --- Configuration ---
SOURCE_DIRECTORY = "source_docs"
CHUNK_SIZE = 500  # How many characters per text chunk
CHUNK_OVERLAP = 50  # How much overlap between chunks
EMBEDDING_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"  # Good default embedding model
)
OLLAMA_MODEL = "phi4-mini"

print(f"Using Ollama model: {OLLAMA_MODEL}")
print(f"Make sure Ollama is running and the model '{OLLAMA_MODEL}' is available.")


# --- 1. Load Documents from Directory ---
print(f"Looking for PDF documents in: {SOURCE_DIRECTORY}")
# Check if the source directory exists
if not os.path.isdir(SOURCE_DIRECTORY):
    print(f"Error: Source directory '{SOURCE_DIRECTORY}' not found.")
    print("Please create the directory and add your PDF files.")
    sys.exit(1)

all_docs = []  # Initialize an empty list to hold pages from all PDFs
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
        loader = PyPDFLoader(pdf_path)
        # Load the PDF pages into memory
        loaded_pdf_docs = loader.load()
        if not loaded_pdf_docs:
            print(
                f"  Warning: No content loaded from '{os.path.basename(pdf_path)}'. Skipping."
            )
            continue
        # Add the loaded pages to our main list
        all_docs.extend(loaded_pdf_docs)
        print(f"    -> Loaded {len(loaded_pdf_docs)} page(s).")
    except FileNotFoundError:
        # This shouldn't happen if os.listdir worked, but good practice
        print(f"  Error: File not found at '{pdf_path}'. Skipping.")
    except Exception as e:
        # Catch errors during loading/parsing of a specific PDF
        print(f"  Error loading PDF '{os.path.basename(pdf_path)}': {e}. Skipping.")

# Check if any documents were loaded successfully overall
if not all_docs:
    print("\nError: No documents were successfully loaded from any PDF files.")
    sys.exit(1)

print(
    f"\nSuccessfully loaded content from {len(pdf_files_found)} PDF(s), total pages: {len(all_docs)}."
)

# --- 2. Split the Document into Chunks ---
print(
    f"Splitting {len(all_docs)} pages into chunks (size: {CHUNK_SIZE}, overlap: {CHUNK_OVERLAP})..."
)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
)
# Create smaller pieces of text from the loaded pages
split_chunks = text_splitter.split_documents(all_docs)
if not split_chunks:
    print("Error: Failed to split the documents into chunks.")
    sys.exit(1)
print(f"Documents split into {len(split_chunks)} chunks.")

# --- 3. Create Embeddings and Vector Store ---
# Embeddings turn text into numbers (vectors) so we can find similar chunks
print(f"Initializing embedding model: {EMBEDDING_MODEL_NAME}...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

print("Creating vector store (this might take a moment)...")
# FAISS is an efficient library for similarity search.
# We'll create an in-memory index from the document chunks and embeddings.
vector_store = FAISS.from_documents(documents=split_chunks, embedding=embeddings)
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

# --- 5. Create the RAG Chain ---

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

# Create the "Stuff Documents" Chain:
# This chain takes the user's question and the retrieved documents
# and formats them into the prompt template, then sends it to the LLM.
combine_docs_chain = create_stuff_documents_chain(llm, prompt)

# Create the Retriever:
# This object knows how to fetch relevant chunks from the vector store.
retriever = vector_store.as_retriever()

# Create the main Retrieval Chain:
# This chain ties everything together:
# 1. It takes the user's question ('input').
# 2. It uses the 'retriever' to get relevant document chunks.
# 3. It uses the 'combine_docs_chain' to generate an answer using the LLM and the chunks.
retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

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

        # Invoke the RAG chain: Pass the question in a dictionary
        # The key 'input' matches the variable name in our prompt template
        response = retrieval_chain.invoke({"input": query})

        # Print the LLM's answer
        print("\nAnswer:", response["answer"])

        # Optional: Print the source chunks used (for debugging/understanding)
        # print("\nSources used:")
        # for i, doc in enumerate(response.get("context", [])):
        #     source_name = doc.metadata.get('source', 'Unknown')
        #     page_num = doc.metadata.get('page', 'N/A')
        #     print(f"  {i+1}. File: {os.path.basename(source_name)}, Page: {page_num}")
        #     # print(f"     Content: {doc.page_content[:150]}...") # Print start of chunk content

        print("-" * 50)  # Add a separator line

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    except KeyboardInterrupt:  # Allow Ctrl+C to exit gracefully
        print("\nExiting...")
        break

print("Goodbye!")
