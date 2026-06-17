class WalrusStoreError(Exception):
    """Raised when storing memory to Walrus fails with a non-2xx status."""

    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"Walrus store failed with status {status_code}: {body}")


class WalrusReadError(Exception):
    """Raised when reading memory from Walrus fails — invalid blob_id, bad JSON, or HTTP error."""

    def __init__(self, blob_id: str, detail: str = "") -> None:
        self.blob_id = blob_id
        self.detail = detail
        super().__init__(f"Walrus read failed for blob '{blob_id}': {detail}")


class WalrusTimeoutError(Exception):
    """Raised when a Walrus HTTP request times out."""

    def __init__(self, operation: str, timeout_seconds: int) -> None:
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        super().__init__(f"Walrus {operation} timed out after {timeout_seconds}s")


class TopicExtractionError(Exception):
    """Raised when topic extraction from a statement fails."""

    def __init__(self, statement: str, detail: str = "") -> None:
        self.statement = statement
        self.detail = detail
        super().__init__(f"Topic extraction failed for '{statement[:60]}': {detail}")


class MemoryPersistenceWarning(Exception):
    """Raised (but caught by caller) when saving memory fails — not fatal, but must be logged."""

    def __init__(self, user_id: str, detail: str = "") -> None:
        self.user_id = user_id
        self.detail = detail
        super().__init__(f"Memory persistence failed for user '{user_id}': {detail}")
