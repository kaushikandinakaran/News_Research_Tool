import streamlit as st
import time
from langchain import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env (especially openai api key)


st.title("News Research Tool")

st.sidebar.title("News Article URLs")

urls= []

for i in range(3):
    url = st.sidebar.text_input(f"URL {i+1}")
    urls.append(url)

process_url_clicked =st.sidebar.button("Process URLs")

main_placeholder = st.empty()
llm = OpenAI(temperature= 0.9 , max_tokens = 500)
embeddings = OpenAIEmbeddings()
if process_url_clicked:
    # Filter out empty URLs
    urls = [url for url in urls if url.strip() != ""]

    if not urls:
        st.warning("Please enter at least one valid URL.")
    else:
        loader = UnstructuredURLLoader(urls=urls)
        main_placeholder.text("Data Loading... Started...")
        data = loader.load()

        if not data:
            st.error("Failed to load content from the URLs.")
        else:
            text_splitter = RecursiveCharacterTextSplitter(
                separators=['\n\n','\n','.',','],
                chunk_size=1000
            )
            main_placeholder.text("Text splitting... Started...")
            docs = text_splitter.split_documents(data)

            if not docs:
                st.error("Document splitting returned no chunks.")
            else:
                vectorstore_openai = FAISS.from_documents(docs, embedding=embeddings)
                main_placeholder.text("Embedding Vector Started Building...")
                time.sleep(2)
                vectorstore_openai.save_local("faiss_store_openai")
                main_placeholder.text("Saved vector embedding.")



query = main_placeholder.text_input("Question: ")

if query:
    # ✅ Explicitly allow loading the pickle file
    vectorstore = FAISS.load_local("faiss_store_openai", embeddings, allow_dangerous_deserialization=True)
    chain =  RetrievalQAWithSourcesChain.from_llm(llm= llm, retriever = vectorstore.as_retriever())
    result = chain({"question":query},return_only_outputs = True)
    st.header("Answer")
    st.write(result["answer"])


    #display source, if avl
    sources = result.get("sources","")
    if sources:
        st.subheader("Sources: ")
        sources_list = sources.split("\n")
        for source in sources_list:
            st.write(source)








