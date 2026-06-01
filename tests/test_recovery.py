"""Tests for fault tolerance and recovery mechanisms."""
import pytest
import asyncio
from storage_node.recovery import RecoveryManager


@pytest.fixture
def recovery_manager():
    return RecoveryManager()


@pytest.mark.asyncio
async def test_recover_node(recovery_manager):
    """Test node recovery process."""
    node_id = "node_1"
    replica_nodes = ["node_2", "node_3"]
    
    result = await recovery_manager.recover_node(node_id, replica_nodes)
    assert result is True


@pytest.mark.asyncio
async def test_full_sync(recovery_manager):
    """Test full data synchronization."""
    node_id = "node_2"
    source_node = "node_1"
    
    sync_result = await recovery_manager.perform_full_sync(node_id, source_node)
    assert sync_result["status"] == "completed"
    assert sync_result["node_id"] == node_id


def test_get_recovery_status(recovery_manager):
    """Test getting recovery status."""
    # Test non-recovered node
    status = recovery_manager.get_recovery_status("node_999")
    assert status["status"] == "never_recovered"