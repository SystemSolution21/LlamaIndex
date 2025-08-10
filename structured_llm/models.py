# models.py
import os
from datetime import date
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from sqlalchemy import JSON, Column, Date, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()


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


class InvoiceORM(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String)
    invoice_date = Column(Date)
    vendor = Column(String)
    vendor_address = Column(String)
    vendor_email = Column(String)
    vendor_phone = Column(String)
    order_number = Column(String)
    due_date = Column(Date)
    total_due = Column(Float)
    currency = Column(String)
    customer = Column(String)
    customer_address = Column(String)
    customer_email = Column(String)
    customer_phone = Column(String)
    billing_address = Column(String)
    billing_email = Column(String)
    billing_phone = Column(String)
    items = Column(JSON)


engine = create_engine(DATABASE_URL if DATABASE_URL else "")
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def save_invoice_to_db(invoice_data: InvoiceData):
    session = Session()
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
    session.add(invoice)
    session.commit()
    session.close()
