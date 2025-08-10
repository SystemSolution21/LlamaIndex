# models.py
"""Models for representing structured data from an invoice."""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


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
