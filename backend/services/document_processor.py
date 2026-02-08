import os
from typing import List, Dict, Any
import PyPDF2
from docx import Document

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        content = ""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif ext == '.pdf':
            with open(file_path, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                for page in pdf.pages:
                    content += page.extract_text()
        elif ext == '.docx':
            doc = Document(file_path)
            for para in doc.paragraphs:
                content += para.text + "\n"
        
        return self.chunk_text(content, os.path.basename(file_path))

    def chunk_text(self, text: str, filename: str) -> List[Dict[str, Any]]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append({
                "content": chunk,
                "metadata": {
                    "source": filename,
                    "start_char": start,
                    "end_char": min(end, len(text))
                }
            })
            start += self.chunk_size - self.chunk_overlap
        return chunks

# Global instance
document_processor = DocumentProcessor()
