import pytest
import hashlib
from coordinator.replication import compute_checksum, verify_checksum, replication_status


# ── Checksum Tests ──────────────────────────────────────────────────────────

def test_compute_checksum_returns_sha256():
    data = "hello distributed storage"
    result = compute_checksum(data)
    expected = hashlib.sha256(data.encode()).hexdigest()
    assert result == expected


def test_compute_checksum_different_data_gives_different_hash():
    assert compute_checksum("data_a") != compute_checksum("data_b")


def test_verify_checksum_valid():
    data = "block_data_123"
    checksum = compute_checksum(data)
    assert verify_checksum(data, checksum) is True


def test_verify_checksum_corrupted_data():
    data = "original data"
    checksum = compute_checksum(data)
    corrupted = "tampered data"
    assert verify_checksum(corrupted, checksum) is False


def test_verify_checksum_empty_string():
    data = ""
    checksum = compute_checksum(data)
    assert verify_checksum(data, checksum) is True


# ── Replication Status Tests ─────────────────────────────────────────────────

def test_replication_status_full():
    assert replication_status(3, 3) == "FULL_REPLICATION"


def test_replication_status_partial():
    assert replication_status(3, 2) == "PARTIAL_REPLICATION"


def test_replication_status_failed():
    assert replication_status(3, 0) == "REPLICATION_FAILED"


def test_replication_status_single_node():
    assert replication_status(1, 1) == "FULL_REPLICATION"


def test_replication_status_zero_total_nodes():
    assert replication_status(0, 0) == "REPLICATION_FAILED"


# ── Storage Node API Tests (using TestClient) ────────────────────────────────

from fastapi.testclient import TestClient
from storage_node.node import app

client = TestClient(app)


def test_node_health_check():
    response = client.get("/node/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "node_id" in data


def test_write_block_success():
    data = "test block data"
    checksum = compute_checksum(data)
    response = client.post("/node/write", json={
        "block_id": "blk_test_001",
        "data": data,
        "checksum": checksum,
    })
    assert response.status_code == 200
    assert response.json()["status"] == "written"


def test_write_block_invalid_checksum():
    response = client.post("/node/write", json={
        "block_id": "blk_test_002",
        "data": "some data",
        "checksum": "invalid_checksum_here",
    })
    assert response.status_code == 400


def test_read_block_after_write():
    data = "readable data block"
    checksum = compute_checksum(data)
    client.post("/node/write", json={
        "block_id": "blk_read_001",
        "data": data,
        "checksum": checksum,
    })
    response = client.get("/node/read/blk_read_001")
    assert response.status_code == 200
    assert response.json()["data"] == data
    assert response.json()["integrity"] == "verified"


def test_read_nonexistent_block():
    response = client.get("/node/read/blk_does_not_exist")
    assert response.status_code == 404


def test_delete_block():
    data = "delete me"
    checksum = compute_checksum(data)
    client.post("/node/write", json={
        "block_id": "blk_del_001",
        "data": data,
        "checksum": checksum,
    })
    response = client.delete("/node/delete/blk_del_001")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_delete_nonexistent_block():
    response = client.delete("/node/delete/blk_ghost")
    assert response.status_code == 404


def test_list_blocks():
    response = client.get("/node/list")
    assert response.status_code == 200
    assert "blocks" in response.json()
