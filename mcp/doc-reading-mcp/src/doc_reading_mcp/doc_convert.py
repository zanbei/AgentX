from pathlib import Path
import csv
from typing import Literal, Union
from fastmcp import FastMCP
import pypandoc
import sys

# Create FastMCP server instance
mcp = FastMCP("doc-reading-mcp")

# Supported formats
FileFormat = Literal["pdf", "docx", "md", "txt", "csv"]

def validate_file_exists(file_path: str) -> Union[None, dict]:
    """Validate that a file exists and is readable"""
    path = Path(file_path)
    if not path.exists():
        return {
            "content": [{"type": "text", "text": f"File does not exist {file_path}"}],
            "isError": True,
        }
    if not path.is_file():
        return {
            "content": [{"type": "text", "text": f"Path is not a file {file_path}"}],
            "isError": True,
        }
    if not path.is_absolute():
        return {
            "content": [
                {"type": "text", "text": f"File path must be absolute {file_path}"}
            ],
            "isError": True,
        }
    return None

def read_text_file(file_path: str) -> str:
    """Read a text file and return its contents"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_csv_file(file_path: str) -> str:
    """Read a CSV file and return its contents as formatted text"""
    result = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            result.append(" | ".join(row))
    return "\n".join(result)

def read_pdf_file(file_path: str) -> str:
    """Read a PDF file and return its contents as text using pdftotext"""
    try:
        import subprocess
        result = subprocess.run(['pdftotext', file_path, '-'], capture_output=True, text=True, check=True)
        if result.stderr:
            return f"Error reading PDF file: {result.stderr}"
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error reading PDF file: {str(e)}"
    except Exception as e:
        return f"Error reading PDF file: {str(e)}"

def read_docx_file(file_path: str) -> str:
    """Read a DOCX file and return its contents as text"""
    try:
        return pypandoc.convert_file(file_path, 'plain', format='docx')
    except Exception as e:
        return f"Error reading DOCX file: {str(e)}"

@mcp.tool()
def read_document(input_path: str) -> str:
    """Read a document and return its contents as text

    Args:
        input_path (str): Absolute path to the input document

    Returns:
        str: The contents of the document as text, or an error message if reading fails

    Notes:
        This tool directly reads various document formats and returns their contents as text.
        Supported formats: PDF, DOCX, MD, TXT, CSV
        
        For CSV files, the contents are formatted with | as column separators
        For PDF and DOCX files, the contents are extracted as plain text
        For MD and TXT files, the raw contents are returned as-is
    """
    print(f"[doc-reading-mcp] Starting to read {input_path}")
    try:
        # Validate input file
        if error := validate_file_exists(input_path):
            return error["content"][0]["text"]

        # Get input format from file extension
        input_format = Path(input_path).suffix[1:].lower()
        if input_format not in ["pdf", "docx", "md", "txt", "csv"]:
            return f"Unsupported file format: {input_format}"

        # Read file based on format
        if input_format == "pdf":
            return read_pdf_file(input_path)
        elif input_format == "docx":
            return read_docx_file(input_path)
        elif input_format == "csv":
            return read_csv_file(input_path)
        else:  # md or txt
            return read_text_file(input_path)

    except Exception as e:
        return f"Error reading file: {str(e)}"
