# Lab: Modify and Extend the RAG Chatbot with Ollama, Langchain, and Gradio

These exercises will help you understand the [provided Python script with LLMs & RAG](https://github.com/andijakl/MachineLearning/tree/main/example%20-%20llm%20with%20rag) by making small, manageable changes. You'll get a feel for how the different parts work together without needing deep ML theory.

For each of the exercise sets, summarize your main findings and any challenges you faced (~ 1 paragraph per set). Upload your modified script and your document to the course repository when you're done.

**Prerequisites:**

1. **Python Installed:** You need Python 3 installed on your system.
2. **Libraries Installed:** You need to install the libraries mentioned in the script. Open your terminal or command prompt and run:

    ```bash
    pip install gradio langchain-community langchain-text-splitters langchain-huggingface langchain-core langchain faiss-cpu ollama langchain-ollama pypdf sentence-transformers
    ```

    *(Note: `faiss-cpu` is for CPU usage. If you have a compatible GPU and C++ build tools, you might use `faiss-gpu`, but `faiss-cpu` is easier to start with.)*
3. **Ollama Running:** You need Ollama installed and running in the background with the model specified in the script (default: `phi4-mini`) pulled.
    * Install Ollama from [https://ollama.com/](https://ollama.com/)
    * Run `ollama pull phi4-mini` in your terminal (or whichever model you intend to use).
    * Make sure the Ollama application or background service is running.
4. **Source Documents:** Create a folder named `source_docs` in the same directory as the Python script and place at least one PDF file inside it.
5. **The Script:** Have the `rag_script_ui.py` file saved and ready to edit.

**General Instructions:**

* **Backup First:** Before making changes, save a copy of the original `rag_script_ui.py` file so you can always go back!
* **Read the Comments:** The script has comments (`#`) explaining what each section does. Read them carefully.
* **Small Changes:** Make one change at a time and test it. This makes it easier to find errors.
* **Observe the Output:** Pay attention to the messages printed in the terminal when you run the script. They tell you what's happening.
* **Experiment:** Don't be afraid to try things! The worst that usually happens is you get an error message, which is part of learning.

---

## Exercise Set 1: Configuration Tweaks (Easy)

These tasks involve changing predefined settings.

1. **Adjust Text Chunking:**
    * **Goal:** Experiment with how the PDF text is split into smaller pieces. Larger chunks might keep more context together but could be too big for the model. Smaller chunks are faster to process but might lose context.
    * **How:**
        * Find the lines: `CHUNK_SIZE = 500` and `CHUNK_OVERLAP = 50`.
        * Try changing `CHUNK_SIZE` (e.g., to `700` or `300`).
        * Try changing `CHUNK_OVERLAP` (e.g., to `100` or `25`). Overlap helps keep context between chunks.
    * **Test:** Run the script. Observe the printed message "Split into X chunks." Does the number of chunks change as you expect? Does changing these values affect the quality or relevance of the answers you get in the Gradio app (this might be subtle)?

2. **Use a Different Ollama Model:**
    * **Goal:** See how a different language model affects the answers.
    * **Prerequisites:** You need to have another model pulled in Ollama (e.g., `ollama pull gemma3:1b`).
    * **How:**
        * Find the line: `OLLAMA_MODEL = "gemma3:1b"`
        * Change `"phi4-mini"` to the name of another model you have pulled (e.g., `"gemma3:1b"`).
    * **Test:** Run the script. Does it initialize the new model? Ask the same question you asked before. Is the answer different in style, length, or accuracy? Does the Gradio interface description update?

---

## Exercise Set 2: User Interface Customization (Easy)

These tasks involve changing how the Gradio web interface looks and feels.

1. **Change the Title and Description:**
    * **Goal:** Make the web page title and description more specific or user-friendly.
    * **How:**
        * Find the `gr.Interface(...)` block near the end of the script.
        * Modify the `title="..."` argument.
        * Modify the `description="..."` argument.
    * **Test:** Run the script and open the Gradio interface in your browser. Do you see your new title and description?

2. **Customize Input/Output Labels:**
    * **Goal:** Change the text labels displayed above the question input box and the answer output box.
    * **How:**
        * Inside `gr.Interface(...)`, find the `inputs=gr.Textbox(...)` and `outputs=gr.Textbox(...)` lines.
        * Change the `label="..."` argument within each `gr.Textbox`. For example, change `label="Your Question"` to `label="Ask me about the documents:"`.
    * **Test:** Run the script and check the Gradio interface. Are the labels updated?

3. **Adjust Text Box Sizes:**
    * **Goal:** Make the input or output boxes taller or shorter.
    * **How:**
        * Inside the `gr.Textbox` definitions for `inputs` and `outputs`, find the `lines=...` argument.
        * Change the number (e.g., make the input `lines=2` or the output `lines=10`).
    * **Test:** Run the script. Are the text boxes resized in the Gradio interface?

---

## Exercise Set 3: Modifying the Prompt (Easy-Medium)

This involves changing the instructions given to the LLM.

1. **Change the LLM's Instructions:**
    * **Goal:** Tell the LLM to answer in a specific way (e.g., be more concise, or act like an expert).
    * **How:**
        * Find the multi-line string variable `prompt_template = """..."""`.
        * Modify the text *before* the `Context:` section. For example, change `Answer the following question based only on the provided context:` to `Be very brief and answer the following question using only the provided context:`.
        * You could also change the text *after* the `Question:` section, before `Answer:`.
    * **Test:** Run the script. Ask a question. Does the LLM's answer style change based on your new instructions? (e.g., Does it become shorter if you asked it to be brief?)

---

## Exercise Set 4: Adding Simple Code Logic (Medium)

These tasks require adding or modifying small amounts of Python code.

1. **Add More Print Statements for Debugging:**
    * **Goal:** Understand the data flow better by printing intermediate results to the terminal.
    * **How:**
        * *Print Number of PDFs Found:* Add `print(f"Found {len(os.listdir(SOURCE_DIRECTORY))} items in source directory.")` before the `for` loop in Step 1. Does it show the correct count? (This counts all items, not just PDFs). Modify it to count only PDFs if you like!
        * *Print First Chunk:* After the line `split_chunks = text_splitter.split_documents(all_docs)`, add `print("--- First Chunk Example ---")` and `print(split_chunks[0].page_content)` to see what the first piece of text looks like.
        * *Print Retrieved Context:* Inside the `ask_rag_system` function, before the `answer = response.get(...)` line, add `print(f"Retrieved Context: {response.get('context')}")`. This shows you exactly what information the LLM is using to answer the question. *Note: This might print a lot of text!*
    * **Test:** Run the script and observe the terminal output. Do the new print statements appear? Do they help you understand what's happening?

---

## Exercise Set 5: Simple Extension (Medium-Hard)

This requires understanding the loading process a bit more.

1. **Add Support for `.txt` Files:**
    * **Goal:** Allow the script to load text from `.txt` files in addition to `.pdf` files.
    * **How:**
        * You'll need a new loader. Add this import at the top: `from langchain_community.document_loaders import TextLoader`
        * Modify the `for` loop in Step 1 (Load Documents). Change the `if` condition and add an `elif` (else if):

            ```python
            # --- 1. Load Documents ---
            all_docs = []
            # Find and load all PDF and TXT files in the source directory
            for filename in os.listdir(SOURCE_DIRECTORY):
                file_path = os.path.join(SOURCE_DIRECTORY, filename)
                if filename.lower().endswith(".pdf"):
                    print(f"  Loading PDF: {filename}...")
                    loader = PyPDFLoader(file_path)
                    docs_from_file = loader.load()
                    all_docs.extend(docs_from_file)
                elif filename.lower().endswith(".txt"): # <-- ADD THIS PART
                    print(f"  Loading TXT: {filename}...")
                    loader = TextLoader(file_path) # Use TextLoader
                    docs_from_file = loader.load()
                    all_docs.extend(docs_from_file) # <-- ADD THIS PART

            print(f"Loaded {len(all_docs)} pages/documents total from PDF(s)/TXT(s).") # Update print message
            ```

    * **Test:** Add a `.txt` file with some text into your `source_docs` folder. Run the script. Does it print that it's loading the `.txt` file? Can you ask questions about the content of the `.txt` file in the Gradio app?

Okay, here are additional exercise tasks building upon the previous ones, designed for students new to ML and Python but ready to explore a bit more.

## Exercise Set 6: Exploring the RAG Components

1. **Try a Different Embedding Model:**
    * **Goal:** See how using a different model for turning text into numbers (embeddings) might affect the search results. Some models are better for specific tasks (like question answering).
    * **How:**
        * Find the line: `EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"`
        * Replace the model name string with another one from the Hugging Face Hub that's compatible with `HuggingFaceEmbeddings`. Good options to try:
            * `"sentence-transformers/paraphrase-MiniLM-L3-v2"` (often good for finding similar meanings)
            * `"sentence-transformers/multi-qa-MiniLM-L6-cos-v1"` (trained specifically for question answering retrieval)
        * You can browse more models here: [https://huggingface.co/models?library=sentence-transformers](https://huggingface.co/models?library=sentence-transformers)
    * **Test:** Run the script. The first time you use a new model, the script will need to download it (this might take a minute or two, watch the terminal). After it starts, ask the same few questions you used before. Do the answers seem more or less relevant? Does the "Creating embeddings and vector store" step take a different amount of time? *Note: The difference in answer quality might be subtle!*

2. **See Retrieved Document Sources:**
    * **Goal:** Print out exactly which parts of your documents (source file and page number) the system retrieved to use as context for answering your question. This helps understand *why* you got a particular answer.
    * **How:** Modify the `ask_rag_system` function to access the `context` part of the response from the `retrieval_chain`.
        * Inside the `ask_rag_system` function, find the `try...except` block.
        * *After* the line `response = retrieval_chain.invoke({"input": question})`, change the code to the following:

        ```python
        # Extract context and answer from the response
        context_docs = response.get("context", [])
        answer = response.get("answer", "Sorry, I couldn't generate an answer.")

        print(f"Generated answer: {answer[:100]}...") # Log snippet to console

        # --- Now print the sources using the extracted 'context_docs' ---
        sources_info = set() # Use a set to store unique source strings
        if context_docs:
            print("\n--- Sources Used by the RAG System ---")
            for doc in context_docs:
                source_file = doc.metadata.get('source', 'Unknown Source')
                page_number = doc.metadata.get('page', 'N/A')
                # Page numbers are often 0-indexed, so add 1 for human readability
                display_page = page_number + 1 if isinstance(page_number, int) else 'N/A'
                sources_info.add(f"  - File: {source_file}, Page: {display_page}")

            # Print the unique sources, sorted for consistency
            for info_line in sorted(list(sources_info)):
                print(info_line)
        else:
            print("--- No specific sources were retrieved ---")
        # --- End of sources printing ---

        return answer # Return the extracted answer
        ```

    * **Test:** Run the script and ask a question in the Gradio interface. Now, look at the **terminal window** where you ran the script. Below the "Generated answer..." log, you should see a list starting with "--- Sources Used...", showing the file(s) and page number(s) that provided the context. Does this help you verify if the system is looking at the right parts of your documents?

3. **Adjust Number of Retrieved Chunks (`k`):**
    * **Goal:** Control how many text chunks (pieces of your documents) are retrieved from the vector database to be fed to the language model. Retrieving more chunks gives the LLM more context, but might also include irrelevant information or slow things down.
    * **How:**
        * Find the line where the `retriever` is created (in Step 5):
            `retriever = vector_store.as_retriever()`
        * Modify this line to include `search_kwargs`. For example, to retrieve the top 3 most relevant chunks:
            `retriever = vector_store.as_retriever(search_kwargs={"k": 3})`
        * Try changing the value of `k` (e.g., to `2`, `5`, or maybe even `1`).
    * **Test:** Run the script with a specific `k` value. Ask a question. Observe the answer. Now, change `k` to a different value, restart the script, and ask the same question. Does the answer change? If you also completed Exercise 2 (See Retrieved Document Sources), does the number of sources printed in the terminal match the `k` value you set?

---

## Exercise Set 7: Improving Robustness and User Experience

1. **Add Basic Ollama Connection Check on Startup:**
    * **Goal:** Make the script give a friendly error message and exit cleanly if it can't connect to the Ollama service when it starts, instead of crashing later.
    * **How:** Wrap the LLM initialization (Step 4) in a `try...except` block to catch potential connection errors. We'll also add a quick test call to the LLM.
        * Add this import near the top of the script: `import sys` (to allow exiting the script). You might also need `requests` library's exceptions if you want to be more specific, but a general `Exception` catch works too. Let's try a general one first.
        * Replace the entire "Initialize LLM" section (Step 4) with this:

        ```python
        # --- 4. Initialize LLM ---
        print(f"Initializing LLM: {OLLAMA_MODEL}...")
        llm = None # Initialize llm variable to None
        try:
            # Assumes Ollama is running and the model is pulled
            llm_instance = OllamaLLM(model=OLLAMA_MODEL)
            # Try a quick test interaction to verify connection and model access
            print("Verifying LLM connection...")
            llm_instance.invoke("Respond with only 'ok'") # Simple test prompt
            llm = llm_instance # Assign to the main llm variable if successful
            print("LLM initialized and connection verified.")
        except Exception as e:
            print(f"\n--- FATAL ERROR ---")
            print(f"Failed to initialize or connect to the Ollama LLM ({OLLAMA_MODEL}).")
            print(f"Error details: {e}")
            # Provide common troubleshooting tips
            print("\nTroubleshooting:")
            print(f"1. Ensure the Ollama application or service is running.")
            print(f"2. Check if the model '{OLLAMA_MODEL}' is pulled (e.g., run 'ollama list' in terminal).")
            print(f"3. If the model is not pulled, run: ollama pull {OLLAMA_MODEL}")
            print("Exiting script.")
            sys.exit(1) # Exit the script with an error code

        # Ensure llm is assigned before proceeding (should be caught by sys.exit otherwise)
        if llm is None:
             print("LLM initialization failed unexpectedly. Exiting.")
             sys.exit(1)

        # --- 5. Create RAG Chain --- (Script continues from here)
        ```

    * **Test:**
        * Run the script while Ollama *is* running. It should print the verification message and continue normally.
        * Stop the Ollama application/service. Run the Python script again. Does it print the "FATAL ERROR" message with troubleshooting tips and exit, instead of showing a more confusing error later?
        * If you have Ollama running but try a model name in the script that you *haven't* pulled (e.g., `OLLAMA_MODEL = "no_such_model_here"`), run the script. Does the error message give you a hint that the model might not be found?

2. **Add a Clear Button to the UI**

   * **Goal:** Add a button to the Gradio web interface that lets the user easily clear the question and answer text boxes, using a built-in feature of `gr.Interface`.
   * **How:** You just need to add one parameter to the `gr.Interface` call.
     * Find the line where the Gradio interface is created (Step 7):

        ```python
        iface = gr.Interface(
            fn=ask_rag_system,
            inputs=gr.Textbox(...),
            outputs=gr.Textbox(...),
            title="Chat with Your Documents (RAG)",
            description=f"...",
            allow_flagging="never",
        )
        ```

     * Add the `clear_btn` parameter inside the `gr.Interface(...)` call. Set its value to the text you want on the button, for example `"Clear Inputs"`.

        ```python
        iface = gr.Interface(
            fn=ask_rag_system,
            inputs=gr.Textbox(...),
            outputs=gr.Textbox(...),
            title="Chat with Your Documents (RAG)",
            description=f"...",
            allow_flagging="never",
            clear_btn="Clear Inputs" # <-- ADD THIS LINE
        )
        ```

   * **Test:** Run the script. The Gradio interface should now have an extra button (likely below the input/output components) labelled "Clear Inputs".
     * Type something in the question box and get an answer.
     * Click the "Clear Inputs" button. Do both the question and answer boxes become empty?

3. **Change the UI Theme**

   * **Goal:** Modify the visual appearance (colors, fonts, layout style) of the Gradio web interface using built-in themes.
   * **How:** Add the `theme` parameter to the `gr.Interface` call and assign a theme object to it. Gradio comes with several pre-built themes.
     * Find the line where the Gradio interface is created (Step 7):

        ```python
        iface = gr.Interface(
            fn=ask_rag_system,
            inputs=gr.Textbox(...),
            outputs=gr.Textbox(...),
            title="Chat with Your Documents (RAG)",
            description=f"...",
            # You might have added clear_btn here
            clear_btn="Clear Inputs",
            allow_flagging="never",
        )
        ```

     * Add the `theme=` parameter inside the `gr.Interface(...)` call. Set its value to one of Gradio's built-in theme objects. You'll need to use `gr.themes` followed by the theme name. Examples:
       * `theme=gr.themes.Soft()`
       * `theme=gr.themes.Glass()`
       * `theme=gr.themes.Monochrome()`
       * `theme=gr.themes.Default()` (This is the standard look if you don't specify a theme)

        Your code might look like this:

        ```python
        import gradio as gr # Make sure gradio is imported

        # ... other code ...

        iface = gr.Interface(
            fn=ask_rag_system,
            inputs=gr.Textbox(...),
            outputs=gr.Textbox(...),
            title="Chat with Your Documents (RAG)",
            description=f"...",
            clear_btn="Clear Inputs",
            allow_flagging="never",
            theme=gr.themes.Soft()  # <-- ADD THIS LINE (choose your theme)
        )
        ```

     * **Test:** Run the script. Open the Gradio interface in your browser. Does the appearance change according to the theme you selected? Try changing `gr.themes.Soft()` to `gr.themes.Glass()` or `gr.themes.Monochrome()` and restart the script to see the difference.

---
