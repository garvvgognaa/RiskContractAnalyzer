   

import io
from typing import Optional
import PyPDF2


def extract_text_from_upload(uploaded_file) -> Optional[str]:
           
    if uploaded_file is None:
        return None

    filename: str = uploaded_file.name.lower()

    if filename.endswith(".txt"):
        return _read_txt(uploaded_file)
    elif filename.endswith(".pdf"):
        return _read_pdf(uploaded_file)
    else:
        raise ValueError(
            f"Unsupported file type: '{uploaded_file.name}'. "
            "Please upload a .pdf or .txt file."
        )


def _read_txt(uploaded_file) -> str:
                                             
    raw_bytes: bytes = uploaded_file.read()
                                                                
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
                                                     
    return raw_bytes.decode("utf-8", errors="replace")


def _read_pdf(uploaded_file) -> str:
                                                          
    raw_bytes: bytes = uploaded_file.read()
    pdf_buffer = io.BytesIO(raw_bytes)

    text_parts = []
    try:
        reader = PyPDF2.PdfReader(pdf_buffer)
        for page_num, page in enumerate(reader.pages):
            extracted = page.extract_text()
            if extracted:
                text_parts.append(extracted)
    except Exception as e:
                                               
        if not text_parts:
            raise ValueError(f"Could not parse PDF: {e}") from e

    return "\n\n".join(text_parts)


def get_file_metadata(uploaded_file) -> dict:
           
    size_kb = round(uploaded_file.size / 1024, 2)
    ext = uploaded_file.name.rsplit(".", 1)[-1].upper() if "." in uploaded_file.name else "UNKNOWN"
    return {
        "name": uploaded_file.name,
        "size_kb": size_kb,
        "file_type": ext,
    }
