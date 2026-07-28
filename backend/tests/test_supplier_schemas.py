from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.supplier import SupplierContactInput, SupplierCreateRequest


def test_supplier_code_is_normalized_and_money_uses_decimal() -> None:
    supplier = SupplierCreateRequest(name="Safe Gear", code=" sg-01 ", credit_limit="1250.50")
    assert supplier.code == "SG-01"
    assert supplier.credit_limit == Decimal("1250.50")


def test_supplier_rejects_negative_financial_values() -> None:
    with pytest.raises(ValidationError):
        SupplierCreateRequest(name="Safe Gear", code="SG-01", minimum_order_amount="-1")


def test_supplier_allows_only_one_primary_contact() -> None:
    contacts = [
        SupplierContactInput(full_name="One", is_primary=True),
        SupplierContactInput(full_name="Two", is_primary=True),
    ]
    with pytest.raises(ValidationError, match="Only one contact may be primary"):
        SupplierCreateRequest(name="Safe Gear", code="SG-01", contacts=contacts)


def test_supplier_contact_method_is_validated() -> None:
    with pytest.raises(ValidationError):
        SupplierContactInput(full_name="One", preferred_contact_method="fax")
