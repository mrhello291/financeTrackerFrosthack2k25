import pathway as pw
from pathway.xpacks.llm.vector_store import VectorStoreServer
from pathway.xpacks.llm import llms, parsers
import os
# from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# local = pw.io.fs.read(
#     "./data/",  # Pathway listens to this data folder
#     format="binary",  # Change from 'binary' to 'text'
#     # mode="streaming",
#     with_metadata=True,
# )

def run_server():
    object_id = os.environ.get("GDRIVEFOLDERID")


    gdrive = pw.io.gdrive.read(
        object_id=object_id,
        service_user_credentials_file="credentials.json",
        file_name_pattern="*.txt",
    )

    files = gdrive

    # model_name = "BAAI/bge-small-en"
    # model_kwargs = {"device": "cpu"}
    # encode_kwargs = {"normalize_embeddings": True}


    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    splitter = CharacterTextSplitter()

    # parser = parsers.DoclingParser()

    host = "127.0.0.1"
    port = 8666

    server = VectorStoreServer.from_langchain_components(
        gdrive, embedder=embeddings, splitter=splitter
    )

    server.run_server(
        host=host,
        port=port,
        with_cache=True,
        cache_backend=pw.persistence.Backend.filesystem("./Cache"),
        # threaded=True
    )

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------
