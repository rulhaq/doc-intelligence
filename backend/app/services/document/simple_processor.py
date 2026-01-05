"""Simple Document Processor - PDF, DOCX, TXT support"""
import io
from typing import Dict, Any
from pathlib import Path
from pypdf import PdfReader
from docx import Document
import structlog
from app.services.inference.ollama_service import OllamaService

logger = structlog.get_logger()


class SimpleDocumentProcessor:
    """Process documents directly - supports PDF, DOCX, TXT"""
    
    def __init__(self):
        self.ollama = OllamaService()
    
    async def process_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process document based on file type"""
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == '.pdf':
            return await self.process_pdf(file_content, filename)
        elif file_ext == '.docx':
            return await self.process_docx(file_content, filename)
        elif file_ext == '.txt':
            return await self.process_txt(file_content, filename)
        else:
            return {
                "success": False,
                "error": f"Unsupported file type: {file_ext}",
                "filename": filename
            }
    
    async def process_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from PDF and use LLM to clean/format it"""
        try:
            # Extract text using pypdf
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)
            
            total_pages = len(pdf_reader.pages)
            all_text = []
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                raw_text = page.extract_text()
                
                if raw_text.strip():
                    # Use LLM to clean and format the extracted text
                    cleaned_text = await self._clean_text_with_llm(raw_text, page_num)
                    all_text.append({
                        "page": page_num,
                        "raw_text": raw_text,
                        "cleaned_text": cleaned_text
                    })
                    
                    logger.info(f"Processed PDF page {page_num}/{total_pages}", filename=filename)
            
            # Combine all text
            full_text = "\n\n".join([p["cleaned_text"] for p in all_text])
            
            return {
                "success": True,
                "total_pages": total_pages,
                "pages": all_text,
                "full_text": full_text,
                "filename": filename,
                "file_type": "pdf"
            }
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}", filename=filename)
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    async def process_docx(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from Word document"""
        try:
            # Extract text using python-docx
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            
            all_text = []
            page_num = 1
            current_page_text = []
            char_count = 0
            
            # Process paragraphs (simulate pages by character count ~3000 chars per page)
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    current_page_text.append(text)
                    char_count += len(text)
                    
                    # Create artificial "pages" every ~3000 characters
                    if char_count > 3000:
                        page_text = "\n".join(current_page_text)
                        cleaned_text = await self._clean_text_with_llm(page_text, page_num)
                        
                        all_text.append({
                            "page": page_num,
                            "raw_text": page_text,
                            "cleaned_text": cleaned_text
                        })
                        
                        logger.info(f"Processed DOCX section {page_num}", filename=filename)
                        page_num += 1
                        current_page_text = []
                        char_count = 0
            
            # Process remaining text
            if current_page_text:
                page_text = "\n".join(current_page_text)
                cleaned_text = await self._clean_text_with_llm(page_text, page_num)
                
                all_text.append({
                    "page": page_num,
                    "raw_text": page_text,
                    "cleaned_text": cleaned_text
                })
                logger.info(f"Processed DOCX section {page_num}", filename=filename)
            
            # Combine all text
            full_text = "\n\n".join([p["cleaned_text"] for p in all_text])
            
            return {
                "success": True,
                "total_pages": len(all_text),
                "pages": all_text,
                "full_text": full_text,
                "filename": filename,
                "file_type": "docx"
            }
            
        except Exception as e:
            logger.error(f"DOCX processing failed: {e}", filename=filename)
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    async def process_txt(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from plain text file"""
        try:
            # Decode text (try UTF-8, fallback to latin-1)
            try:
                raw_text = file_content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    raw_text = file_content.decode('latin-1')
                except:
                    raw_text = file_content.decode('utf-8', errors='ignore')
            
            # Split into pages (~3000 chars each)
            all_text = []
            lines = raw_text.split('\n')
            
            page_num = 1
            current_page_lines = []
            char_count = 0
            
            for line in lines:
                current_page_lines.append(line)
                char_count += len(line)
                
                if char_count > 3000:
                    page_text = "\n".join(current_page_lines)
                    cleaned_text = await self._clean_text_with_llm(page_text, page_num)
                    
                    all_text.append({
                        "page": page_num,
                        "raw_text": page_text,
                        "cleaned_text": cleaned_text
                    })
                    
                    logger.info(f"Processed TXT section {page_num}", filename=filename)
                    page_num += 1
                    current_page_lines = []
                    char_count = 0
            
            # Process remaining text
            if current_page_lines:
                page_text = "\n".join(current_page_lines)
                cleaned_text = await self._clean_text_with_llm(page_text, page_num)
                
                all_text.append({
                    "page": page_num,
                    "raw_text": page_text,
                    "cleaned_text": cleaned_text
                })
                logger.info(f"Processed TXT section {page_num}", filename=filename)
            
            # Combine all text
            full_text = "\n\n".join([p["cleaned_text"] for p in all_text])
            
            return {
                "success": True,
                "total_pages": len(all_text),
                "pages": all_text,
                "full_text": full_text,
                "filename": filename,
                "file_type": "txt"
            }
            
        except Exception as e:
            logger.error(f"TXT processing failed: {e}", filename=filename)
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    async def _clean_text_with_llm(self, raw_text: str, page_num: int) -> str:
        """Use LLM to clean and format extracted text (DISABLED for speed)"""
        # Skip LLM cleaning for faster processing - just use basic cleanup
        return self._basic_cleanup(raw_text)
    
    def _basic_cleanup(self, text: str) -> str:
        """Basic text cleanup without LLM"""
        # Remove extra whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
