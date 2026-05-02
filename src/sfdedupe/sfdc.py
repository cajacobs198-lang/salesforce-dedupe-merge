import os


class MockSFDC:
    def __init__(self):
        self.merges: list[tuple[str, list[str]]] = []

    def merge_accounts(self, master_id: str, duplicate_ids: list[str]) -> dict:
        self.merges.append((master_id, list(duplicate_ids)))
        return {"master": master_id, "merged": duplicate_ids, "status": "ok"}


def get_client():
    if os.environ.get("USE_MOCK_SFDC", "true").lower() == "true":
        return MockSFDC()
    from simple_salesforce import Salesforce  # noqa: WPS433
    return Salesforce(
        username=os.environ["SFDC_USERNAME"],
        password=os.environ["SFDC_PASSWORD"],
        security_token=os.environ["SFDC_TOKEN"],
    )
