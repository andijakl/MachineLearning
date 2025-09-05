import os  # To interact with the file system (list files)
import gradio as gr

# --- Core LangChain Components ---
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM as Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# --- Configuration ---
SOURCE_DIRECTORY = "source_docs"  # Folder with your PDF files
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "phi4-mini"

print(f"--- Simple RAG Demo with Gradio UI ---")
print(f"Using Ollama model: {OLLAMA_MODEL}")
print(f"Looking for PDFs in: '{SOURCE_DIRECTORY}'")

# --- 1. Load Documents ---
all_docs = []
# Find and load all PDF files in the source directory
for filename in os.listdir(SOURCE_DIRECTORY):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(SOURCE_DIRECTORY, filename)
        print(f"  Loading {filename}...")
        loader = PyPDFLoader(pdf_path)
        docs_from_pdf = loader.load()
        all_docs.extend(docs_from_pdf)  # Add pages from this PDF to the list

print(f"Loaded {len(all_docs)} pages total from PDF(s).")

# --- 2. Split Documents ---
print("Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
)
split_chunks = text_splitter.split_documents(all_docs)
print(f"Split into {len(split_chunks)} chunks.")

# --- 3. Create Embeddings & Vector Store ---
# Embeddings turn text chunks into numerical vectors
print("Creating embeddings and vector store (may take a moment)...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
# FAISS stores the chunks and their embeddings for fast searching
vector_store = FAISS.from_documents(documents=split_chunks, embedding=embeddings)
print("Vector store created.")

# --- 4. Initialize LLM ---
print(f"Initializing LLM: {OLLAMA_MODEL}...")
# Assumes Ollama is running and the model is pulled
llm = Ollama(model=OLLAMA_MODEL)
print("LLM initialized.")

# --- 5. Create RAG Chain ---
# Prompt Template: How we ask the LLM, using retrieved context
prompt_template = """
Answer the following question based only on the provided context:

Context:
{context}

Question:
{input}

Answer:"""
prompt = ChatPromptTemplate.from_template(prompt_template)

# Retriever: Gets relevant chunks from the vector store
retriever = vector_store.as_retriever()

# Combine Documents Chain: Formats prompt + docs for the LLM
combine_docs_chain = create_stuff_documents_chain(llm, prompt)

# Retrieval Chain: Ties retriever and combine_docs_chain together
retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)


print("\nRAG system ready!")


# --- 6. Setup function to ask RAG system ---
def ask_rag_system(question):
    """
    This function takes a user's question, uses the RAG chain to get an answer,
    and returns the answer.
    """
    if not question or not question.strip():
        return "Please enter a question."

    print(f"\nReceived question: {question}")  # Log to console
    print("Thinking...")

    # Use the RAG chain (already created) to get an answer
    try:
        response = retrieval_chain.invoke({"input": question})
        answer = response.get("answer", "Sorry, I couldn't generate an answer.")
        print(f"Generated answer: {answer[:100]}...")  # Log snippet to console
        return answer
    except Exception as e:
        print(f"Error during RAG chain invocation: {e}")
        return "An error occurred while processing your question."


# --- 7. Create and launch the Gradio interface ---
iface = gr.Interface(
    fn=ask_rag_system,  # The Python function to call
    inputs=gr.Textbox(
        label="Your Question",
        lines=3,
        placeholder="Ask something about the documents...",
    ),  # Input field
    outputs=gr.Textbox(label="Answer", lines=5),  # Output field
    title="Chat with Your Documents (RAG)",
    description=f"Ask questions about the PDF documents loaded from '{SOURCE_DIRECTORY}'. Uses Ollama model '{OLLAMA_MODEL}'.",
    flagging_mode="never",  # Disables the flagging feature
)

# --- 8. Launch the web server ---
print("\nLaunching Gradio Interface...")
iface.launch()

print("Gradio interface closed. Goodbye!")
