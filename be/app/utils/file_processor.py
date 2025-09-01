import os
from typing import Dict, Optional
import docx
import csv
import chardet

class FileProcessor:
    @staticmethod
    def process_file(file_path: str) -> Optional[Dict[str, str]]:
        """
        Process different types of files and return their content
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.docx':
                return FileProcessor._process_docx(file_path)
            elif file_ext == '.txt':
                return FileProcessor._process_txt(file_path)
            elif file_ext == '.csv':
                return FileProcessor._process_csv(file_path)
            else:
                return None
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return None

    @staticmethod
    def _process_docx(file_path: str) -> Dict[str, str]:
        doc = docx.Document(file_path)
        content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return {
            'content': content,
            'type': 'docx',
            'prompt': 'This is a Word document. Please analyze its content:'
        }

    @staticmethod
    def _process_txt(file_path: str) -> Dict[str, str]:
        # Detect encoding
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
            return {
                'content': content,
                'type': 'txt',
                'prompt': 'This is a text file. Please analyze its content:'
            }

    @staticmethod
    def _process_csv(file_path: str) -> Dict[str, str]:
        rows = []
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                rows.append(','.join(row))
        
        content = '\n'.join(rows)
        return {
            'content': content,
            'type': 'csv',
            'prompt': 'This is a CSV file. Please analyze its content:'
        }
