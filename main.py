"""
This script demonstrates how to use LlamaIndex and OpenAI to extract structured data
from a PDF invoice. It defines a Pydantic model for the invoice data, reads a PDF
file, and uses a structured LLM to parse the content into the defined model. The
extracted data is then printed in both JSON format and as a raw Pydantic object.
"""

import os
import sys
from datetime import date
from pathlib import Path
from typing import Any, List, Optional

from dotenv import load_dotenv
from llama_index.core.base.llms.types import CompletionResponse
from llama_index.core.llms.structured_llm import StructuredLLM
from llama_index.core.schema import Document
from llama_index.llms.openai import OpenAI
from llama_index.readers.file import PDFReader
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


# Structured single line item model
class LineItem(BaseModel):
    """A Pydantic model for a single line item in an invoice."""

    description: str = Field(..., description="Description of the item or service.")
    quantity: float = Field(..., description="Quantity of the item.")
    unit_price: float = Field(..., description="Price per unit of the item.")
    discount: Optional[float] = Field(
        None, description="Discount amount for the line item."
    )
    sub_total: Optional[float] = Field(
        description="Sub total for the line item ((quantity * unit_price) - discount)."
    )
    tax_rate: float = Field(..., description="Tax amount for the line item.")
    total_price: float = Field(
        ..., description="Total price for the line item (sub_total + tax_rate)."
    )


# Structured invoice data model
class InvoiceData(BaseModel):
    """A Pydantic model to represent structured data from an invoice."""

    vendor: str = Field(..., description="Vendor name.")
    vendor_address: str = Field(..., description="Vendor address.")
    vendor_email: Optional[str] = Field(None, description="Vendor email.")
    vendor_phone: Optional[str] = Field(None, description="Vendor phone.")
    invoice_number: str = Field(..., description="Invoice number.")
    order_number: Optional[str] = Field(None, description="Order number.")
    invoice_date: date = Field(..., description="Invoice date in YYYY-MM-DD format.")
    due_date: Optional[date] = Field(None, description="Due date in YYYY-MM-DD format.")
    total_due: float = Field(..., description="Total amount due.")
    currency: str = Field(
        ..., description="Currency of the total amount (e.g., USD, EUR)."
    )
    customer: str = Field(..., description="Customer name.")
    customer_address: str = Field(..., description="Customer address.")
    customer_email: Optional[str] = Field(None, description="Customer email.")
    customer_phone: Optional[str] = Field(None, description="Customer phone.")
    billing_address: str = Field(..., description="Billing address.")
    billing_email: Optional[str] = Field(None, description="Billing email.")
    billing_phone: Optional[str] = Field(None, description="Billing phone.")
    items: List[LineItem] = Field(
        ..., description="A list of all line items from the invoice."
    )


# Entry point
def main() -> None:
    """
    Entry point of the script.

    Loads a PDF, extracts text, and uses a structured LLM to parse invoice data,
    then prints the results.
    """
    dir_path: Path = Path(__file__).parent
    pdf_path: Path = dir_path / "invoice/invoice.pdf"

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
