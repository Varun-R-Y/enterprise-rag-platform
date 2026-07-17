import pytest
import logging
from pathlib import Path
import fitz

from app.services.pdf_service import PDFService

def test_pdf_extraction_success(tmp_path):
    # 1. Create a dummy PDF with multiple pages and text
    pdf_path = tmp_path / "test_doc.pdf"
    doc = fitz.open()
    
    # Page 1
    page1 = doc.new_page()
    page1.insert_text((50, 50), "Leave\nPolicy")
    
    # Page 2
    page2 = doc.new_page()
    page2.insert_text((50, 50), "Employees are entitled to 20 days off.\nHappy working!")
    
    doc.save(str(pdf_path))
    doc.close()
    
    # 2. Run PDFService extraction
    service = PDFService()
    results = service.extract_text(pdf_path)
    
    # 3. Assertions
    assert len(results) == 2
    
    # Page 1 checks
    assert results[0].page == 1
    assert "Leave Policy" in results[0].text
    
    # Page 2 checks
    assert results[1].page == 2
    assert "Employees are entitled to 20 days off." in results[1].text
    assert "Happy working!" in results[1].text

def test_pdf_extraction_file_not_found(caplog):
    service = PDFService()
    non_existent_path = Path("this_file_does_not_exist_anywhere.pdf")
    
    caplog.clear()
    with pytest.raises(FileNotFoundError):
        service.extract_text(non_existent_path)
            
    # Verify the error log is present with the correct format
    assert any(
        "Failed to extract PDF: this_file_does_not_exist_anywhere.pdf" in record.message
        and "Reason: File not found" in record.message
        for record in caplog.records
    )

def test_pdf_extraction_invalid_file(tmp_path, caplog):
    # Create a corrupted/invalid PDF (plain text instead of binary PDF)
    bad_pdf_path = tmp_path / "corrupted.pdf"
    bad_pdf_path.write_text("Not a real PDF file content")
    
    service = PDFService()
    caplog.clear()
    with pytest.raises(ValueError) as exc_info:
        service.extract_text(bad_pdf_path)
            
    assert "Could not open PDF file" in str(exc_info.value)
    
    # Verify the log format
    assert any(
        "Failed to extract PDF: corrupted.pdf" in record.message
        and "Reason: Could not open PDF file" in record.message
        for record in caplog.records
    )

