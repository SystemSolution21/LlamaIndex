# Structured Data Extraction

This project demonstrates an end-to-end pipeline for extracting structured data from PDF invoices. It leverages LlamaIndex and OpenAI's `StructuredLLM` to parse unstructured text from a PDF and map it to a predefined `InvoiceData` Pydantic model. The script then displays the extracted data in both JSON and Pydantic object formats for verification before persisting it to a database using SQLAlchemy.

## Running relative import scripts from parent directory

```pwsh
python -m structured_llm.main
```

## PDF Structured Data Extraction Output

Loading PDF from: C:\Users\path_to_the_parent_directory\LlamaIndex\invoice\invoice.pdf</br>
Initializing LLM and parsing invoice data...

### ===== Invoice Data (JSON) ====

```json
{
  "vendor": "DEMO - Sliced Invoices",
  "vendor_address": "Suite 5A-1204\n123 Somewhere Street\nYour City AZ 12345",
  "vendor_email": "<admin@slicedinvoices.com>",
  "vendor_phone": null,
  "invoice_number": "INV-3337",
  "order_number": "12345",
  "invoice_date": "2016-01-25",
  "due_date": "2016-01-31",
  "total_due": 93.5,
  "currency": "USD",
  "customer": "Test Business",
  "customer_address": "123 Somewhere St\nMelbourne, VIC 3000",
  "customer_email": "<test@test.com>",
  "customer_phone": null,
  "billing_address": "123 Somewhere St\nMelbourne, VIC 3000",
  "billing_email": null,
  "billing_phone": null,
  "items": [
    {
      "description": "Web Design\nThis is a sample description...",
      "quantity": 1.0,
      "unit_price": 85.0,
      "discount": null,
      "sub_total": 85.0,
      "tax_rate": 8.5,
      "total_price": 93.5
    }
  ]
}
```

### ===== Invoice Data (Pydantic Object) ====

```python
InvoiceData(
vendor='DEMO - Sliced Invoices' vendor_address='Suite 5A-1204\n123 Somewhere Street\nYour City AZ 12345' vendor_email='<admin@slicedinvoices.com>' vendor_phone=None invoice_number='INV-3337' order_number='12345' invoice_date=datetime.date(2016, 1, 25) due_date=datetime.date(2016, 1, 31) total_due=93.5 currency='USD' customer='Test Business' customer_address='123 Somewhere St\nMelbourne, VIC 3000' customer_email='<test@test.com>' customer_phone=None billing_address='123 Somewhere St\nMelbourne, VIC 3000' billing_email=None billing_phone=None items=[LineItem(description='Web Design\nThis is a sample description...', quantity=1.0, unit_price=85.0, discount=None, sub_total=85.0, tax_rate=8.5, total_price=93.5)]
```

### ===== Persisting to Database =====

Invoice data persisted to the database.
