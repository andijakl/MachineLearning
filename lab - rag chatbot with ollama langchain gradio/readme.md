# Lab: Modify and Extend the RAG Chatbot with Ollama, LangChain, and Gradio

These exercises will help you understand the [provided Python script with LLMs & RAG](https://github.com/andijakl/MachineLearning/tree/main/example%20-%20llm%20with%20rag) by making small, manageable changes. You'll get a feel for how the different parts work together without needing deep ML theory.

For each exercise set, summarize your main findings and any challenges you faced in about one paragraph. Upload your modified script and summary document to the course repository when you are done.

**Prerequisites**

1. **Python 3 installed:** You need a working Python 3 installation.
2. **Dependencies installed:** Use the project dependency file instead of typing package names manually.

    ```bash
    python -m pip install -r requirements.txt
    ```

    If your system uses `python3` instead of `python`, run:

    ```bash
    python3 -m pip install -r requirements.txt
    ```

3. **Ollama running:** Ollama must be installed and running in the background, and the model used in the script must be pulled.
    * Install Ollama from [https://ollama.com/](https://ollama.com/)
    * Run `ollama pull phi4-mini`
    * Make sure the Ollama app or background service is running before you start the Python script
4. **Source documents:** Create a folder named `source_docs` in the same directory as the Python script and place at least one PDF inside it.
5. **Starter script:** Use `rag_script_ui.py` as your starting point.

**General Instructions**

* **Backup first:** Save a copy of the original `rag_script_ui.py` before editing.
* **Change one thing at a time:** Small steps are easier to test and debug.
* **Watch the terminal output:** The script prints useful progress information while loading files, chunking text, and answering questions.
* **Test often:** Run the script after each exercise and check both the terminal and the Gradio UI.
* **Experiment:** Don't be afraid to try things! The worst that usually happens is you get an error message, which is part of learning.

---

## Exercise Set 1: Configuration Tweaks (Easy)

These tasks focus on changing existing settings.

1. **Adjust text chunking**
    * **Goal:** Experiment with how the document text is split into smaller pieces. Larger chunks preserve more context, while smaller chunks are more focused.
    * **How:**
        * Find `CHUNK_SIZE = 500` and `CHUNK_OVERLAP = 50`.
        * Try a larger chunk size such as `700`.
        * Try a smaller chunk size such as `300`.
        * Also experiment with overlap values like `100` or `25`.
    * **Test:** Run the script and compare the printed `Split into X chunks.` message. Then ask the same question in the Gradio UI and observe whether the answer changes.

2. **Use a different Ollama model**
    * **Goal:** Compare how different local models answer the same question.
    * **How:**
        * Find `OLLAMA_MODEL = "phi4-mini"`.
        * Replace it with another model you have already pulled, for example `gemma3:1b`.
    * **Test:** Run the script again. Does the new model initialize correctly? Does the style or quality of the answer change? Does the UI description update?

---

## Exercise Set 2: User Interface Customization (Easy)

These tasks change the Gradio interface.

1. **Change the title and description**
    * **Goal:** Make the interface feel more specific or user-friendly.
    * **How:**
        * Find the `gr.Interface(...)` block near the end of the script.
        * Edit `title="..."`.
        * Edit `description="..."`.
    * **Test:** Run the script and open the Gradio app. Are your changes visible?

2. **Customize the input and output labels**
    * **Goal:** Rename the text boxes in the UI.
    * **How:**
        * In `inputs=gr.Textbox(...)`, change the `label` value.
        * In `outputs=gr.Textbox(...)`, change the `label` value.
    * **Test:** Run the script and confirm the labels have changed.

3. **Adjust textbox sizes**
    * **Goal:** Make the question box or answer box taller or shorter.
    * **How:**
        * Change the `lines=...` values inside the two `gr.Textbox(...)` definitions.
    * **Test:** Run the script and check whether the text boxes resize as expected.

---

## Exercise Set 3: Modifying the Prompt (Easy-Medium)

This set changes the instructions sent to the LLM.

1. **Change the LLM instructions**
    * **Goal:** Make the model answer in a different style, for example more briefly or more formally.
    * **How:**
        * Find the multi-line string stored in `prompt_template`.
        * Change the text before `Context:`.
        * For example, replace `Answer the following question based only on the provided context:` with `Be very brief and answer the question using only the provided context:`.
    * **Test:** Run the script and ask the same question as before. Does the answer style change?

---

## Exercise Set 4: Adding Simple Code Logic (Medium)

These tasks add small debugging or inspection features.

1. **Add more print statements for debugging**
    * **Goal:** Understand the flow of data through the system.
    * **How:**
        * **Print number of PDFs found:** inside `load_pdf_texts(...)`, add a print statement that counts only `.pdf` files in the folder.
        * **Print the first chunk:** after this line:

            ```python
            split_chunks = text_splitter.create_documents(pdf_texts, metadatas=pdf_metadatas)
            ```

            add:

            ```python
            print("--- First Chunk Example ---")
            print(split_chunks[0].page_content)
            ```

        * **Print the retrieved context:** inside `ask_rag_system(...)`, right after `retrieved_docs = retriever.invoke(question)`, add:

            ```python
            print("--- Retrieved Context ---")
            print(format_context(retrieved_docs))
            ```

    * **Test:** Run the script and inspect the terminal output. Do these extra prints help you understand what is happening?

---

## Exercise Set 5: Simple Extension (Medium)

This set extends the file loading step.

1. **Add support for `.txt` files**
    * **Goal:** Load plain text files from `source_docs` in addition to PDFs.
    * **How:**
        * Rename `load_pdf_texts(...)` to something like `load_source_texts(...)`.
        * Update the loop so it handles both `.pdf` and `.txt` files.
        * For `.txt` files, read the file directly with Python instead of using a deprecated LangChain community loader.

        One possible approach is:

        ```python
        def load_source_texts(source_directory):
            texts = []
            metadatas = []

            for filename in os.listdir(source_directory):
                file_path = os.path.join(source_directory, filename)

                if filename.lower().endswith(".pdf"):
                    print(f"  Loading PDF: {filename}...")
                    text = "\n".join(
                        page.extract_text() or "" for page in PdfReader(file_path).pages
                    )
                elif filename.lower().endswith(".txt"):
                    print(f"  Loading TXT: {filename}...")
                    with open(file_path, "r", encoding="utf-8") as file:
                        text = file.read()
                else:
                    continue

                text = text.strip()
                if not text:
                    continue

                texts.append(text)
                metadatas.append({"source": file_path})

            return texts, metadatas
        ```

    * **Test:** Add a `.txt` file to `source_docs`, run the script, and confirm you can ask questions about its contents.

---

## Exercise Set 6: Exploring the RAG Components (Medium-Hard)

These tasks focus on retrieval behavior.

1. **Try a different embedding model**
    * **Goal:** Compare how different embedding models affect retrieval quality.
    * **How:**
        * Find `EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"`.
        * Replace it with another sentence-transformer model, for example:
            * `"sentence-transformers/paraphrase-MiniLM-L3-v2"`
            * `"sentence-transformers/multi-qa-MiniLM-L6-cos-v1"`
    * **Test:** Run the script and ask the same questions as before. Do the retrieved answers feel more or less relevant? Does startup time change?

2. **See which source files were retrieved**
    * **Goal:** Print the source files of the retrieved chunks so you can better understand why the model answered the way it did.
    * **How:**
        * Inside `ask_rag_system(...)`, after `retrieved_docs = retriever.invoke(question)`, add code similar to this:

        ```python
        print("\n--- Sources Used by the RAG System ---")
        seen_sources = set()

        for doc in retrieved_docs:
            source_file = doc.metadata.get("source", "Unknown Source")
            if source_file not in seen_sources:
                print(f"- {source_file}")
                seen_sources.add(source_file)
        ```

    * **Test:** Run the script, ask a question, and inspect the terminal output. Do the listed source files make sense?

3. **Adjust the number of retrieved chunks (`k`)**
    * **Goal:** Control how many chunks are retrieved before the prompt is built.
    * **How:**
        * Add a new configuration value near the top of the file:

            ```python
            RETRIEVAL_K = 3
            ```

        * Change the retriever creation from:

            ```python
            retriever = vector_store.as_retriever()
            ```

            to:

            ```python
            retriever = vector_store.as_retriever(search_kwargs={"k": RETRIEVAL_K})
            ```

        * Try values like `1`, `2`, `3`, or `5`.
    * **Test:** Run the script, ask the same question multiple times with different `k` values, and compare the answers.

---

## Exercise Set 7: Improving Robustness and User Experience (Medium)

1. **Add a basic Ollama startup check**
    * **Goal:** Show a helpful error message if Ollama is not reachable or the model is missing.
    * **How:**
        * Add `import sys` near the top of the file.
        * Wrap the LLM initialization section in a `try...except` block.
        * Keep using `validate_model_on_init=True`, because that already checks the model on startup.

        Example:

        ```python
        print(f"Initializing LLM: {OLLAMA_MODEL}...")
        try:
            llm = OllamaLLM(model=OLLAMA_MODEL, validate_model_on_init=True)
            print("LLM initialized.")
        except Exception as error:
            print("\n--- Startup Error ---")
            print(error)
            print("\nTroubleshooting:")
            print("1. Make sure Ollama is running.")
            print(f"2. Make sure the model exists: ollama pull {OLLAMA_MODEL}")
            sys.exit(1)
        ```

    * **Test:** Stop Ollama and run the script again. Does the error message help you understand what went wrong?

2. **Add a clear button to the UI**
    * **Goal:** Add a button that clears both the question and answer boxes.
    * **How:**
        * Inside `gr.Interface(...)`, add:

        ```python
        clear_btn="Clear Inputs"
        ```

    * **Test:** Run the script, ask a question, then click the clear button. Do both text boxes clear?

3. **Change the UI theme**
    * **Goal:** Experiment with Gradio's built-in themes.
    * **How:**
        * In this Gradio version, pass the theme when calling `launch(...)`.
        * Change the launch call from:

            ```python
            iface.launch()
            ```

            to something like:

            ```python
            iface.launch(theme=gr.themes.Soft())
            ```

        * Other built-in options include:
            * `theme=gr.themes.Soft()`
            * `theme=gr.themes.Glass()`
            * `theme=gr.themes.Monochrome()`
    * **Test:** Run the script and compare how the interface looks with different themes.
