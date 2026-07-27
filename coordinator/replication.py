import hashlib


def compute_checksum(data: str) -> str:
    """
    Compute SHA-256 checksum of the data block.
    Used to verify data integrity across all nodes.
    """
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def verify_checksum(data: str, expected_checksum: str) -> bool:
    """
    Verify that stored data matches the original checksum.
    Returns True if data is intact, False if corrupted.
    """
    actual = compute_checksum(data)
    if actual != expected_checksum:
        print(f"[INTEGRITY] Checksum mismatch! Expected: {expected_checksum}, Got: {actual}")
        return False
    return True


def replication_status(total_nodes: int, successful_writes: int) -> str:
    """
    Determine the replication health status.
    """
    ratio = successful_writes / total_nodes if total_nodes > 0 else 0
    if ratio == 1.0:
        return "FULL_REPLICATION"
    elif ratio >= 0.67:
        return "PARTIAL_REPLICATION"
    else:
        return "REPLICATION_FAILED"
