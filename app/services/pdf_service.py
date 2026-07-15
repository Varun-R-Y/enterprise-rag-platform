import re
import logging
from pathlib import Path
from typing import cast
import fitz

from app.schemas.document import PageContent

logger = logging.getLogger(__name__)

class PDFService:
    """
    Service to handle PDF document processing and text extraction.
    """
    
    def extract_text(self, file_path: str | Path) -> list[PageContent]:
        """
        Opens a PDF file and extracts text page-by-page, returning a list of PageContent.
        Applies whitespace normalization and preserves page numbers.
        
        Raises FileNotFoundError if the file doesn't exist.
        Raises ValueError if the PDF cannot be opened or is corrupted.
        """
        path_obj = Path(file_path)
        
        # 1. Verify file existence
        if not path_obj.exists():
            error_msg = f"File not found: {file_path}"
            logger.error(f"Failed to extract PDF: {path_obj.name}\nReason: {error_msg}")
            raise FileNotFoundError(error_msg)

        # 2. Attempt to open the PDF document
        try:
            doc = fitz.open(str(path_obj))
        except Exception as e:
            error_msg = f"Could not open PDF file. It may be corrupted or invalid: {str(e)}"
            logger.error(f"Failed to extract PDF: {path_obj.name}\nReason: {error_msg}")
            raise ValueError(error_msg) from e

        pages_content = []
        try:
            # 3. Iterate page by page
            for page in doc:
                page_num = page.number + 1
                
                # Extract text using block layout grouping to respect natural paragraphs
                blocks = page.get_text("blocks")
                
                cleaned_blocks = []
                for b in blocks:
                    block_text = b[4]
                    if not block_text or not block_text.strip():
                        continue
                    
                    # Normalize whitespace within the block
                    block_clean = self._normalize_block_text(block_text)
                    if block_clean:
                        cleaned_blocks.append(block_clean)
                
                # Combine all text blocks with double newlines
                page_text = "\n\n".join(cleaned_blocks)
                
                # Fallback to standard page extraction if block extraction returned nothing
                if not page_text.strip():
                    page_text = self._normalize_block_text(cast(str, page.get_text("text")))

                pages_content.append(
                    PageContent(page=page_num, text=page_text)
                )
        except Exception as e:
            logger.error(f"Failed to extract PDF: {path_obj.name}\nReason: {str(e)}")
            raise ValueError(f"Error during PDF text extraction: {str(e)}") from e
        finally:
            doc.close()

        return pages_content

    def _normalize_block_text(self, text: str) -> str:
        """
        Normalizes whitespace by collapsing multiple spaces/tabs to a single space,
        and single newlines to a single space (while keeping paragraph boundaries).
        """
        if not text:
            return ""
            
        # Standardize line endings and collapse horizontal spaces
        cleaned = re.sub(r"\r\n?", "\n", text)
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        
        # Split into paragraphs inside the block if double newlines are present
        paragraphs = re.split(r"\n\s*\n+", cleaned)
        
        cleaned_paragraphs = []
        for p in paragraphs:
            # Replace single newlines within the paragraph with a single space
            p_clean = p.replace("\n", " ").strip()
            # Collapse any double spaces created
            p_clean = re.sub(r" +", " ", p_clean)
            if p_clean:
                cleaned_paragraphs.append(p_clean)
                
        return "\n\n".join(cleaned_paragraphs)
