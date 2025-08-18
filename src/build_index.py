import os
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from config import PERSIST_DIR, EMBED_MODEL, DATA_DIR
from preprocess import load_docs_raw, token_chunks

def build_or_load_vectorstore() -> Chroma:
    # Always initialize embeddings the same way used later by retriever
    embeddings = OpenAIEmbeddings(model=EMBED_MODEL)

    # If collection exists, just connect
    if os.path.isdir(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        return Chroma(
            collection_name="sec_filings",
            persist_directory=PERSIST_DIR,
            embedding_function=embeddings,
        )

    # Else, (re)build the vector store
    raw = load_docs_raw(DATA_DIR)
    docs: List[Document] = []
    for fn, pages in raw.items():
        # filename pattern: TICKER_YEAR.ext
        try:
            stem = os.path.splitext(fn)[0]
            ticker, year = stem.split("_")
        except Exception:
            ticker, year = "UNK", "UNK"

        for page_no, page_text in pages:
            if not page_text:
                continue
            for chunk in token_chunks(page_text, chunk_tokens=500, overlap_tokens=100):
                if not chunk.strip():
                    continue
                meta = {
                    "file": fn,
                    "ticker": ticker,
                    "year": year,
                    "page": page_no,
                }
                docs.append(Document(page_content=chunk, metadata=meta))

    # Process documents in smaller batches to avoid token limits
    print(f"Processing {len(docs)} document chunks...")
    
    # Create empty vector store first
    vs = Chroma(
        collection_name="sec_filings",
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR,
    )
    
    # Add documents in batches of 20 to avoid API limits
    batch_size = 20
    total_batches = (len(docs) + batch_size - 1) // batch_size
    
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i+batch_size]
        batch_num = i//batch_size + 1
        print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} docs)...")
        
        try:
            vs.add_documents(batch)
            print(f"✅ Batch {batch_num} completed")
            
            # Add delay to be respectful to API
            if batch_num < total_batches:
                import time
                time.sleep(0.5)
                
        except Exception as e:
            print(f"❌ Batch {batch_num} failed: {e}")
            # Continue with next batch
            continue
    
    print("Vector store built successfully!")
    return vs
