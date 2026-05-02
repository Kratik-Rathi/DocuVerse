import streamlit as st
import os
import time

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Milvus, FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# -------------------------------
# 🔹 Helper: Debug Logger
# -------------------------------
def log_debug(msg):
    print(msg)
    if "debug_logs" not in st.session_state:
        st.session_state.debug_logs = []
    st.session_state.debug_logs.append(msg)


# -------------------------------
# 🔹 Text Chunking
# -------------------------------
def get_text_chunks(documents, doc_key="default", chunk_size=1000, chunk_overlap=100):
    cache_key = f"chunked_docs_{doc_key}"

    if cache_key in st.session_state:
        log_debug(f"[Cache] Using cached chunks for key: {cache_key}")
        return st.session_state[cache_key]

    log_debug(f"[Splitting] Creating chunks for key: {doc_key}...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
        length_function=len,
        add_start_index=True
    )

    chunks = splitter.split_documents(documents)
    st.session_state[cache_key] = chunks

    log_debug(f"[Done] {len(chunks)} chunks created.")
    return chunks


# -------------------------------
# 🔹 Optional Milvus Connection
# -------------------------------
def get_milvus_connection():
    try:
        from pymilvus import connections

        host = os.getenv("MILVUS_HOST", "localhost")
        port = os.getenv("MILVUS_PORT", "19530")

        connections.connect("default", host=host, port=port)
        log_debug(f"[Milvus] Connected to {host}:{port}")

        return True

    except Exception as e:
        log_debug(f"[Milvus] Connection failed: {e}")
        return False


# -------------------------------
# 🔹 Vector Store (Milvus → FAISS fallback)
# -------------------------------
def get_vectorstore(documents, doc_key="default", chunk_size=1000, chunk_overlap=100):
    cache_key = f"vector_store_{doc_key}"

    # 🔁 Cache
    if cache_key in st.session_state:
        log_debug(f"[Cache] Using cached vector store: {cache_key}")
        return st.session_state[cache_key]

    # 🔹 Step 1: Chunking
    chunks = get_text_chunks(documents, doc_key, chunk_size, chunk_overlap)

    # 🔹 Step 2: Embeddings
    log_debug("[Model] Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 🔹 Step 3: Validate chunks
    valid_docs = []
    for i, doc in enumerate(chunks):
        content = getattr(doc, "page_content", "")

        if not isinstance(content, str):
            log_debug(f"[SKIP] Chunk {i} not string")
            continue

        content = content.strip()

        if not content or "\x00" in content:
            log_debug(f"[SKIP] Chunk {i} empty/null")
            continue

        try:
            embeddings.embed_documents([content])
            valid_docs.append(doc)
        except Exception as e:
            log_debug(f"[FAIL] Chunk {i} embedding error: {e}")

    if not valid_docs:
        raise ValueError("❌ No valid chunks survived embedding.")

    # ============================
    # 🔥 Try Milvus (optional)
    # ============================
    use_milvus = os.getenv("USE_MILVUS", "false").lower() == "true"

    if use_milvus:
        try:
            if get_milvus_connection():
                collection_name = f"rag_chunks_{doc_key}"

                log_debug("[Milvus] Attempting to store vectors...")

                vector_store = Milvus.from_documents(
                    valid_docs,
                    embedding=embeddings,
                    collection_name=collection_name,
                    connection_args={
                        "host": os.getenv("MILVUS_HOST", "localhost"),
                        "port": os.getenv("MILVUS_PORT", "19530")
                    }
                )

                time.sleep(2)

                log_debug(f"[✅] Milvus collection created: {collection_name}")
                st.session_state[cache_key] = vector_store
                return vector_store

        except Exception as e:
            log_debug(f"[⚠️] Milvus failed → fallback to FAISS: {e}")

    # ============================
    # ✅ FAISS (default for Streamlit)
    # ============================
    try:
        log_debug("[FAISS] Creating FAISS vector store...")

        vector_store = FAISS.from_documents(
            valid_docs,
            embedding=embeddings
        )

        st.session_state[cache_key] = vector_store

        log_debug("[✅] FAISS vector store ready")
        return vector_store

    except Exception as e:
        log_debug(f"[❌] FAISS failed: {e}")
        raise RuntimeError("Both Milvus and FAISS failed.") from e