import os
import hashlib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

app = FastAPI(title="Storage Node Service")

NODE_ID = os.getenv("NODE_ID", "node-1")

# In-memory store (replace with PostgreSQL or disk in production)
data_store: dict = {}

# Prometheus metrics
write_counter = Counter("storage_writes_total", "Total write operations", ["node_id"])
read_counter = Counter("storage_reads_total", "Total read operations", ["node_id"])
error_counter = Counter("storage_errors_total", "Total errors", ["node_id", "operation"])
write_latency = Histogram("storage_write_latency_seconds", "Write latency", ["node_id"])
read_latency = Histogram("storage_read_latency_seconds", "Read latency", ["node_id"])


class WriteRequest(BaseModel):
    block_id: str
    data: str
    checksum: str


@app.get("/node/health")
def health_check():
    return {"node_id": NODE_ID, "status": "healthy", "blocks_stored": len(data_store)}


@app.post("/node/write")
def write_block(req: WriteRequest):
    """Write a data block and validate checksum before storing."""
    with write_latency.labels(node_id=NODE_ID).time():
        actual_checksum = hashlib.sha256(req.data.encode()).hexdigest()
        if actual_checksum != req.checksum:
            error_counter.labels(node_id=NODE_ID, operation="write").inc()
            raise HTTPException(status_code=400, detail="Checksum mismatch — data integrity failure")

        data_store[req.block_id] = {
            "data": req.data,
            "checksum": req.checksum,
        }
        write_counter.labels(node_id=NODE_ID).inc()

    return {"node_id": NODE_ID, "block_id": req.block_id, "status": "written"}


@app.get("/node/read/{block_id}")
def read_block(block_id: str):
    """Read a data block and verify its integrity."""
    with read_latency.labels(node_id=NODE_ID).time():
        block = data_store.get(block_id)
        if not block:
            error_counter.labels(node_id=NODE_ID, operation="read").inc()
            raise HTTPException(status_code=404, detail=f"Block {block_id} not found on {NODE_ID}")

        actual_checksum = hashlib.sha256(block["data"].encode()).hexdigest()
        if actual_checksum != block["checksum"]:
            error_counter.labels(node_id=NODE_ID, operation="integrity").inc()
            raise HTTPException(status_code=500, detail="Data corruption detected on read")

        read_counter.labels(node_id=NODE_ID).inc()

    return {
        "node_id": NODE_ID,
        "block_id": block_id,
        "data": block["data"],
        "checksum": block["checksum"],
        "integrity": "verified",
    }


@app.delete("/node/delete/{block_id}")
def delete_block(block_id: str):
    """Delete a data block from this node."""
    if block_id not in data_store:
        raise HTTPException(status_code=404, detail=f"Block {block_id} not found")
    del data_store[block_id]
    return {"node_id": NODE_ID, "block_id": block_id, "status": "deleted"}


@app.get("/node/metrics")
def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/node/list")
def list_blocks():
    """List all block IDs stored on this node."""
    return {"node_id": NODE_ID, "blocks": list(data_store.keys()), "total": len(data_store)}
