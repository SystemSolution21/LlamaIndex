# models.py
"""
Defines data models for representing and storing invoice information.

Module contains the Pydantic models used for structured data extraction
from invoices, the corresponding SQLAlchemy ORM model for database persistence,
and the logic for saving the extracted data to a database.

It includes:
- `LineItem`: A Pydantic model for a single line item in an invoice.
- `InvoiceData`: A Pydantic model for the overall invoice data.
- `InvoiceORM`: A SQLAlchemy ORM model that maps to the 'invoices' table.
- `save_invoice_to_db`: A function to persist an `InvoiceData` object to the database.
- Database engine and session setup, configured via a .env file.

"""

import os
import sys
from datetime import date
from typing import Any, List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from sqlalchemy import JSON, Column, Date, Engine, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL: str | None = os.getenv(key="DATABASE_URL")
if not DATABASE_URL:
    print("Error:DATABASE_URL environment variables not set.", file=sys.stderr)
    sys.exit(1)


# SQLAlchemy ORM base class
class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


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
        None,
        description="Sub total for the line item ((quantity * unit_price) - discount).",
    )
    tax_rate: float = Field(..., description="Tax amount for the line item.")
    total_price: float = Field(
        ..., description="Total price for the line item (sub_total + tax_rate)."
    )


# Structured invoice data model
class InvoiceData(BaseModel):
    """A Pydantic model to represent structured data extracted from an invoice."""

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


class InvoiceORM(Base):
    """An ORM model to represent structured invoice data in the database."""

    __tablename__: str = "invoices"
    id: Column[int] = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number: Column[str] = Column(String)
    invoice_date: Column[date] = Column(Date)
    vendor: Column[str] = Column(String)
    vendor_address: Column[str] = Column(String)
    vendor_email: Column[str] = Column(String)
    vendor_phone: Column[str] = Column(String)
    order_number: Column[str] = Column(String)
    due_date: Column[date] = Column(Date)
    total_due: Column[float] = Column(Float)
    currency: Column[str] = Column(String)
    customer: Column[str] = Column(String)
    customer_address: Column[str] = Column(String)
    customer_email: Column[str] = Column(String)
    customer_phone: Column[str] = Column(String)
    billing_address: Column[str] = Column(String)
    billing_email: Column[str] = Column(String)
    billing_phone: Column[str] = Column(String)
    items: Column[Any] = Column(JSON)


# Database engine and session setup
engine: Engine = create_engine(url=DATABASE_URL if DATABASE_URL else "")
Session: sessionmaker = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def save_invoice_to_db(invoice_data: InvoiceData) -> None:
    """Saves the structured invoice data to the database.

    Creates a new session, maps the `InvoiceData` Pydantic model
    to the `InvoiceORM` SQLAlchemy model, adds it to the session, commits the
    transaction, and closes the session.

    Args:
        invoice_data: An `InvoiceData` object containing the structured data
            extracted from the invoice.
    """

    # Create a new session
    with Session() as session:
        invoice = InvoiceORM(
            invoice_number=invoice_data.invoice_number,
            invoice_date=invoice_data.invoice_date,
            vendor=invoice_data.vendor,
            vendor_address=invoice_data.vendor_address,
            vendor_email=invoice_data.vendor_email,
            vendor_phone=invoice_data.vendor_phone,
            order_number=invoice_data.order_number,
            due_date=invoice_data.due_date,
            total_due=invoice_data.total_due,
            currency=invoice_data.currency,
            customer=invoice_data.customer,
            customer_address=invoice_data.customer_address,
            customer_email=invoice_data.customer_email,
            customer_phone=invoice_data.customer_phone,
            billing_address=invoice_data.billing_address,
            billing_email=invoice_data.billing_email,
            billing_phone=invoice_data.billing_phone,
            items=[item.model_dump() for item in invoice_data.items],
        )
        session.add(instance=invoice)
        session.commit()
