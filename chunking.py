from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def create_chunks(docpath, chunk_size, chunk_overlap):
    reader = PdfReader(docpath)

    fulltext = ''
    for page in reader.pages:
        text = page.extract_text()
        if text: 
            fulltext += text + '\n'

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(fulltext)

    filename = os.path.basename(docpath).replace('.pdf','')

    chunkid = 1
    ids = []
    metadata = []
    for chunk in chunks:
        ids.append(f"{filename}_chunk_{chunkid}")
        metadata.append({'source' : filename, 'version' : 'v1', 'chunkid' : chunkid})
        chunkid += 1

    return ids, chunks, metadata
