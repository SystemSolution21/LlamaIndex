# main.py
"""
Main execution script for the invoice processing application.

This script orchestrates the process of extracting structured data from an
invoice PDF file. It performs the following steps:
1.  Prompts the user to select a PDF invoice file using a graphical file dialog.
2.  Reads the selected PDF and extracts its text content using `llama-index-readers-file`.
3.  Initializes an OpenAI LLM (e.g., "gpt-4o-mini") and wraps it with
    `StructuredLLM` to enforce output matching the `InvoiceData` Pydantic model.
4.  Sends the extracted text to the LLM for parsing.
5.  Prints the structured invoice data in both JSON and Pydantic object formats.
6.  Persists the extracted data to a database using the `save_invoice_to_db` function.

The script handles user cancellation, file errors, and LLM processing errors
gracefully by printing informative messages to stderr and exiting.
"""

import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Any, List, Optional

from llama_index.core.base.llms.types import CompletionResponse
from llama_index.core.llms.structured_llm import StructuredLLM
from llama_index.core.schema import Document
from llama_index.llms.openai import OpenAI
from llama_index.readers.file import PDFReader

from .models import InvoiceData, save_invoice_to_db


# Entry point
def main() -> None:
    """
    Main function to run the invoice extraction and processing pipeline.

    This function serves as the entry point for the script. It guides the user
    through selecting a PDF file, processes the file to extract structured invoice
    data using an LLM, displays the results, and saves them to a database.

    The process includes:
    - Using a Tkinter file dialog to get the path to an invoice PDF.
    - Reading the PDF content with `PDFReader`.
    - Using an OpenAI model via `StructuredLLM` to parse the text into an
      `InvoiceData` object.
    - Printing the parsed data for verification.
    - Calling `save_invoice_to_db` to store the results.

    Exits with a non-zero status code if any step fails.
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

        # Persist to database
        try:
            print("\n===== Saving to database ====")
            save_invoice_to_db(invoice_data=invoice_data)
        except Exception as e:
            print(f"Error saving to database: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
