import re
from pathlib import Path
import pypdf
import chromadb
from chromadb.utils import embedding_functions

# Configuration settings
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
MANUALS_DIR = ROOT_DIR / "frontend" / "public" / "manuals"
CHROMA_FOLDER = ROOT_DIR / "backend" / "rag" / "chroma_db"
COLLECTION_NAME = "product_manuals"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
HEADINGS = ["How to Use", "Troubleshooting", "Warranty"]

# 1. Read every PDF manual from the directory using pypdf
def load_manuals(manuals_dir: Path) -> list[dict]:
    documents = []
    pdf_files = sorted(list(manuals_dir.glob("*.pdf")))
    for pdf_path in pdf_files:
        reader = pypdf.PdfReader(str(pdf_path))
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
        documents.append({
            "file_name": pdf_path.name,
            "raw_text": full_text,
        })
    return documents

# 2. Remove extra whitespaces, line breaks, and formatting noise from text
def clean_text(raw_text: str) -> str:
    cleaned = raw_text.replace("Synthetic manual for learning", "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

# 3. Cut document text into chunks by section headings observing size and overlap limits
def split_into_chunks(documents: list[dict]) -> list[dict]:
    chunks = []
    
    # Mapping of filenames to clean product names
    product_names = {
        "classic-white-t-shirt.pdf": "Classic White T-Shirt",
        "wireless-bluetooth-headphones.pdf": "Wireless Bluetooth Headphones",
        "stainless-steel-water-bottle.pdf": "Stainless Steel Water Bottle",
        "canvas-everyday-backpack.pdf": "Canvas Everyday Backpack",
        "ceramic-coffee-mug.pdf": "Ceramic Coffee Mug",
    }

    for doc in documents:
        file_name = doc["file_name"]
        product_name = product_names.get(
            file_name,
            file_name.replace(".pdf", "").replace("-", " ").title()
        )
        cleaned = clean_text(doc["raw_text"])

        # Extract text under each heading
        # Regex captures content between headings
        sections = {}
        for i, heading in enumerate(HEADINGS):
            start_pattern = re.escape(heading)
            if i < len(HEADINGS) - 1:
                end_pattern = re.escape(HEADINGS[i + 1])
                match = re.search(f"{start_pattern}\\s*(.*?)\\s*(?={end_pattern}|$)", cleaned, re.IGNORECASE)
            else:
                match = re.search(f"{start_pattern}\\s*(.*)", cleaned, re.IGNORECASE)

            if match:
                sections[heading] = match.group(1).strip()
            else:
                sections[heading] = ""

        # Chunk each section
        for section, content in sections.items():
            if not content:
                continue

            if len(content) <= CHUNK_SIZE:
                chunk_text = f"Product: {product_name} | Section: {section}\n{content}"
                chunks.append({
                    "product": product_name,
                    "section": section,
                    "file_name": file_name,
                    "text": chunk_text,
                    "part": 1,
                })
            else:
                # Sliding window split if section exceeds chunk_size
                start = 0
                part = 1
                while start < len(content):
                    end = start + CHUNK_SIZE
                    slice_text = content[start:end].strip()
                    chunk_text = f"Product: {product_name} | Section: {section}\n{slice_text}"
                    chunks.append({
                        "product": product_name,
                        "section": section,
                        "file_name": file_name,
                        "text": chunk_text,
                        "part": part,
                    })
                    part += 1
                    start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks

# 4. Save the product, section and file name with each chunk, and its id
def build_metadata(chunks: list[dict]) -> tuple[list[str], list[str], list[dict]]:
    ids = []
    texts = []
    metadatas = []

    for item in chunks:
        base_name = item["file_name"].replace(".pdf", "")
        section_slug = item["section"].lower().replace(" ", "-")
        chunk_id = f"{base_name}-{section_slug}-{item['part']}"

        ids.append(chunk_id)
        texts.append(item["text"])
        metadatas.append({
            "product": item["product"],
            "section": item["section"],
            "file_name": item["file_name"],
        })

    return ids, texts, metadatas

# 5. Store the chunks in Chroma DB
def store_in_chroma(ids: list[str], texts: list[str], metadatas: list[dict]):
    CHROMA_FOLDER.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_FOLDER))
    # all-MiniLM-L6-v2 default embedding function
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )
    # Upsert ensures duplicate-free execution
    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
    )
    return collection

# 6. Search one sample question and print the best result
def run_sample_search(collection, query: str = "How do I pair wireless bluetooth headphones?"):
    results = collection.query(
        query_texts=[query],
        n_results=1,
    )
    print("\n--- Sample Search Verification ---")
    print(f"Query: {query}")
    if results["documents"] and results["documents"][0]:
        print(f"Best Match (ID: {results['ids'][0][0]}):")
        print(results["documents"][0][0])
        print(f"Metadata: {results['metadatas'][0][0]}")
    print("----------------------------------\n")

# 7. Run them in order and print how many chunks were stored
def main():
    print("Starting Knowledge Base pipeline...")
    docs = load_manuals(MANUALS_DIR)
    print(f"Loaded {len(docs)} manual PDFs from {MANUALS_DIR}")

    chunks = split_into_chunks(docs)
    print(f"Split text into {len(chunks)} heading-based chunks.")

    ids, texts, metadatas = build_metadata(chunks)
    collection = store_in_chroma(ids, texts, metadatas)
    print(f"Successfully stored {len(ids)} chunks in Chroma DB collection '{COLLECTION_NAME}' at {CHROMA_FOLDER}")

    run_sample_search(collection)

if __name__ == "__main__":
    main()

