import os  # To interact with the file system (list files)
import gradio as gr

# --- Core LangChain Components ---
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from pypdf import PdfReader

# --- Configuration ---
SOURCE_DIRECTORY = "source_docs"  # Folder with your PDF files
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "phi4-mini"

print("--- Simple RAG Demo with Gradio UI ---")
print(f"Using Ollama model: {OLLAMA_MODEL}")
print(f"Looking for PDFs in: '{SOURCE_DIRECTORY}'")


def load_pdf_texts(source_directory):
    pdf_texts = []
    pdf_metadatas = []

    for filename in os.listdir(source_directory):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(source_directory, filename)
        print(f"  Loading {filename}...")
        pdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(pdf_path).pages)
        pdf_text = pdf_text.strip()
        if not pdf_text:
            continue

        pdf_texts.append(pdf_text)
        pdf_metadatas.append({"source": pdf_path})

    return pdf_texts, pdf_metadatas


def format_context(documents):
    formatted_chunks = []
    for doc in documents:
        source_name = os.path.basename(doc.metadata.get("source", "Unknown"))
        formatted_chunks.append(f"Source: {source_name}\n{doc.page_content}")

    return "\n\n".join(formatted_chunks)

# --- 1. Load Documents ---
pdf_texts, pdf_metadatas = load_pdf_texts(SOURCE_DIRECTORY)

print(f"Loaded {len(pdf_texts)} PDF(s).")

# --- 2. Split Documents ---
print("Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
)
split_chunks = text_splitter.create_documents(pdf_texts, metadatas=pdf_metadatas)
print(f"Split into {len(split_chunks)} chunks.")

# --- 3. Create Embeddings & Vector Store ---
# Embeddings turn text chunks into numerical vectors
print("Creating embeddings and vector store (may take a moment)...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
# InMemoryVectorStore keeps the example dependency-light and easy to run.
vector_store = InMemoryVectorStore.from_documents(
    documents=split_chunks, embedding=embeddings
)
print("Vector store created.")

# --- 4. Initialize LLM ---
print(f"Initializing LLM: {OLLAMA_MODEL}...")
# Assumes Ollama is running and the model is pulled
llm = OllamaLLM(model=OLLAMA_MODEL, validate_model_on_init=True)
print("LLM initialized.")

# --- 5. Configure Retrieval and Prompting ---
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

    try:
        retrieved_docs = retriever.invoke(question)
        context = format_context(retrieved_docs)
        prompt_value = prompt.invoke(
            {
                "context": context or "No relevant context was retrieved.",
                "input": question,
            }
        )
        answer = llm.invoke(prompt_value)
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
