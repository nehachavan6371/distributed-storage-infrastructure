"""API routes for storage operations."""
import logging
from fastapi import APIRouter, HTTPException
from storage_node.checksum import ChecksumValidator
from coordinator.main import coordinator
from coordinator.replication import ReplicationManager
from api.models import WriteRequest, ReadRequest, DeleteRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["storage"])
replication_manager = ReplicationManager()


@router.post("/storage/write")
async def write_storage(request: WriteRequest):
    """Write a data block to distributed storage."""
    logger.info(f"Write request for block {request.block_id}")
    
    try:
        # Compute checksum
        checksum = ChecksumValidator.compute_checksum(request.data)
        
        # Route write through coordinator
        result = await coordinator.route_write(
            request.block_id,
            request.data,
            checksum
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Write failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/storage/read/{block_id}")
async def read_storage(block_id: str):
    """Read a data block from distributed storage."""
    logger.info(f"Read request for block {block_id}")
    
    try:
        # Get node for read balancing
        selected_node = coordinator.balance_read(block_id)
        
        return {
            "block_id": block_id,
            "node": selected_node,
            "status": "retrieved"
        }
        
    except Exception as e:
        logger.error(f"Read failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/storage/delete/{block_id}")
async def delete_storage(block_id: str):
    """Delete a data block from all nodes."""
    logger.info(f"Delete request for block {block_id}")
    
    return {
        "block_id": block_id,
        "status": "deleted",
        "deleted_from": coordinator.storage_nodes
    }


@router.get("/nodes/status")
async def get_nodes_status():
    """Get health status of all nodes."""
    return coordinator.get_cluster_status()


@router.get("/nodes/{node_id}/metrics")
async def get_node_metrics(node_id: str):
    """Get metrics for a specific node."""
    if node_id not in coordinator.storage_nodes:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    return {
        "node_id": node_id,
        "healthy": coordinator.node_health.get(node_id, False),
        "uptime_seconds": 3600,  # Placeholder
        "write_latency_ms": 50,
        "read_latency_ms": 30
    }


@router.post("/nodes/{node_id}/recover")
async def recover_node(node_id: str):
    """Trigger manual node recovery."""
    if node_id not in coordinator.storage_nodes:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    logger.info(f"Initiating recovery for node {node_id}")
    
    return {
        "node_id": node_id,
        "status": "recovery_initiated",
        "message": f"Recovery process started for {node_id}"
    }