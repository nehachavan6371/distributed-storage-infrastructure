import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from coordinator.main import (
    write_to_nodes,
    read_from_node,
    delete_from_nodes,
    check_all_nodes_health,
    healthy_nodes,
    NODE_URLS,
)
from coordinator.replication import compute_checksum, replication_status

app = FastAPI(
    title="Distributed Storage Infrastructure API",
    description="A distributed block-storage system with replication, fault tolerance, and real-time monitoring.",
    version="1.0.0",
)


class WriteRequest(BaseModel):
    block_id: str
    data: str
    replication_factor: int = 3


class WriteResponse(BaseModel):
    block_id: str
    status: str
    replicated_to: list
    failed_nodes: list
    replication_status: str
    checksum: str
    timestamp: str


@app.get("/", tags=["Root"])
def root():
    return {
        "service": "Distributed Storage Infrastructure",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/nodes/status",
    }


@app.post("/storage/write", response_model=WriteResponse, tags=["Storage"])
async def write_block(req: WriteRequest, background_tasks: BackgroundTasks):
    """
    Write a data block to all distributed storage nodes.
    Data is replicated across all healthy nodes with checksum validation.
    """
    if not healthy_nodes:
        raise HTTPException(status_code=503, detail="No healthy storage nodes available")

    checksum = compute_checksum(req.data)
    result = await write_to_nodes(req.block_id, req.data, checksum)

    rep_status = replication_status(len(NODE_URLS), len(result["successful_nodes"]))

    if len(result["successful_nodes"]) == 0:
        raise HTTPException(status_code=500, detail="Write failed on all nodes")

    return WriteResponse(
        block_id=req.block_id,
        status="success",
        replicated_to=result["successful_nodes"],
        failed_nodes=result["failed_nodes"],
        replication_status=rep_status,
        checksum=checksum,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@app.get("/storage/read/{block_id}", tags=["Storage"])
async def read_block(block_id: str):
    """
    Read a data block from the nearest healthy storage node.
    Automatically load-balances across healthy nodes.
    """
    result = await read_from_node(block_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Block '{block_id}' not found on any node")
    return result


@app.delete("/storage/delete/{block_id}", tags=["Storage"])
async def delete_block(block_id: str):
    """
    Delete a data block from all storage nodes.
    """
    result = await delete_from_nodes(block_id)
    return {"block_id": block_id, "status": "deleted", **result}


@app.get("/nodes/status", tags=["Nodes"])
async def get_nodes_status():
    """
    Get real-time health status of all storage nodes.
    """
    statuses = await check_all_nodes_health()
    return {
        "total_nodes": len(NODE_URLS),
        "healthy_count": len(healthy_nodes),
        "degraded_count": len(NODE_URLS) - len(healthy_nodes),
        "nodes": statuses,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/nodes/healthcheck", tags=["Nodes"])
async def trigger_health_check():
    """
    Manually trigger a health check across all nodes.
    """
    statuses = await check_all_nodes_health()
    return {"status": "health_check_complete", "nodes": statuses}
