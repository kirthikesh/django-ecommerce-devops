"""A mock/test-mode payment gateway.

No real money moves and no external API is called. This stands in for a
provider like Stripe's test mode so the checkout flow is fully demonstrable
without payment credentials. Swap `MockPaymentGateway` for a real
integration (e.g. Stripe) behind the same `charge()` interface when going
to production.
"""

import uuid
from dataclasses import dataclass


@dataclass
class ChargeResult:
    success: bool
    reference: str
    message: str


class MockPaymentGateway:
    @staticmethod
    def charge(card_number: str, amount) -> ChargeResult:
        card_number = (card_number or "").replace(" ", "")
        reference = f"MOCK-{uuid.uuid4().hex[:12].upper()}"

        # Mimic test-card conventions: a card ending in 0000 is a simulated decline.
        if card_number.endswith("0000"):
            return ChargeResult(success=False, reference=reference, message="Card declined (test mode).")

        return ChargeResult(success=True, reference=reference, message="Payment approved (test mode).")
