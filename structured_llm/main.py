# main.py
"""
This script demonstrates how to use LlamaIndex and OpenAI to extract structured data
from a PDF invoice. It defines a Pydantic model for the invoice data, reads a PDF
file, and uses a structured LLM to parse the content into the defined model. The
extracted data is then printed in both JSON format and as a raw Pydantic object.
"""

import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Any, List, Optional

from dotenv import load_dotenv
from llama_index.core.base.llms.types import CompletionResponse
from llama_index.core.llms.structured_llm import StructuredLLM
from llama_index.core.schema import Document
from llama_index.llms.openai import OpenAI
from llama_index.readers.file import PDFReader

from .models import InvoiceData

# Load environment variables from .env file
load_dotenv()


# Entry point
def main() -> None:
    """
    Entry point of the script.

    Loads a PDF, extracts text, and uses a structured LLM to parse invoice data,
    then prints the results.
    """
    dir_path: Path = Path(__file__).parent

    # Open a file dialog window to select the PDF file
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    pdf_path_str = filedialog.askopenfilename(
        title="Select Invoice PDF",
        filetypes=[("PDF files", "*.pdf")],
        initialdir=str(dir_path / "invoice"),
    )
    root.destroy()

    if not pdf_path_str:
        print("Error: No PDF file selected.", file=sys.stderr)
        sys.exit(1)

    pdf_path: Path = Path(pdf_path_str)

    if not pdf_path.is_file():
        print(f"Error: Invoice file not found at {pdf_path}", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"Loading PDF from: {pdf_path}")
        pdf_reader = PDFReader()
        documents: List[Document] = pdf_reader.load_data(file=pdf_path)
        text: str = documents[0].text.strip()
        if not text:
            print("Error: Failed to extract text from the PDF.", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error loading or reading PDF: {e}", file=sys.stderr)
        sys.exit(1)

    response: Optional[CompletionResponse] = None
    try:
        print("Initializing LLM and parsing invoice data...")
        MODEL_NAME: str = os.getenv(key="MODEL_NAME", default="gpt-4o-mini")
        llm = OpenAI(model=MODEL_NAME, temperature=0.0)
        sllm: StructuredLLM = llm.as_structured_llm(output_cls=InvoiceData)

        response = sllm.complete(prompt=text)
        invoice_data: InvoiceData | Any | None = response.raw

    except Exception as e:
        print(f"Error during LLM processing: {e}", file=sys.stderr)
        # LLM call success but fail parsing.
        if response:
            print("LLM raw text response:", response.text, file=sys.stderr)
        sys.exit(1)

    if invoice_data:
        print("\n===== Invoice Data (JSON) ====")
        print(invoice_data.model_dump_json(indent=2))

        print("\n===== Invoice Data (Pydantic Object) ====")
        print(invoice_data)


if __name__ == "__main__":
    main()
