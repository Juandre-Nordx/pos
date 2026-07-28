import pytest
from pydantic import ValidationError

from app.schemas.inventory import StockAdditionRequest


def test_stock_addition_requires_positive_quantity() -> None:
    with pytest.raises(ValidationError):
        StockAdditionRequest(quantity=0, reason="Stock received")


def test_stock_addition_accepts_auditable_details() -> None:
    request = StockAdditionRequest(
        quantity=12,
        reason="Supplier delivery received",
        reference="PO-1042",
    )

    assert request.quantity == 12
    assert request.reference == "PO-1042"
