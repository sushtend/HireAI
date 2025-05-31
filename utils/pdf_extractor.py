from PyPDF2 import PdfReader
import io

def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_file: FileStorage object from Flask request.files
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        # Read the PDF file
        pdf_reader = PdfReader(io.BytesIO(pdf_file.read()))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
            
        return text.strip()
        
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return None 