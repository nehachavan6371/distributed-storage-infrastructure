import os
import httpx
import asyncio
from typing import List, Dict

NODE_URLS = [
    os.getenv("NODE_1_URL", "http://localhost:8001"),
    os.getenv("NODE_2_URL", "http://localhost:8002"),
    os.getenv("NODE_3_URL", "http://localhost:8003"),
]

# Track which nodes are currently healthy
healthy_nodes: List[str] = list(NODE_URLS)


async def write_to_nodes(block_id: str, data: str, checksum: str) -> Dict:
    """
    Write data block to all healthy nodes (replication).
    Returns list of nodes that successfully acknowledged the write.
    """
    successful_nodes = []
    failed_nodes = []

    async with httpx.AsyncClient(timeout=5.0) as client:
        tasks = [
            _write_to_single_node(client, url, block_id, data, checksum)
            for url in healthy_nodes
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for url, result in zip(healthy_nodes, results):
        node_id = _url_to_node_id(url)
        if isinstance(result, Exception):
            failed_nodes.append(node_id)
            print(f"[COORDINATOR] Write failed on {node_id}: {result}")
        else:
            successful_nodes.append(node_id)

    return {
        "successful_nodes": successful_nodes,
        "failed_nodes": failed_nodes,
        "replication_achieved": len(successful_nodes),
    }


async def read_from_node(block_id: str) -> Dict:
    """
    Read data block from the first available healthy node (load balancing).
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        for url in healthy_nodes:
            try:
                response = await client.get(f"{url}/node/read/{block_id}")
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"[COORDINATOR] Read failed on {url}: {e}")
                continue
    return None


async def delete_from_nodes(block_id: str) -> Dict:
    """
    Delete data block from all nodes.
    """
    successful_nodes = []

    async with httpx.AsyncClient(timeout=5.0) as client:
        tasks = [
            client.delete(f"{url}/node/delete/{block_id}")
            for url in healthy_nodes
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for url, result in zip(healthy_nodes, results):
        node_id = _url_to_node_id(url)
        if not isinstance(result, Exception):
            successful_nodes.append(node_id)

    return {"deleted_from": successful_nodes}


async def check_all_nodes_health() -> List[Dict]:
    """
    Ping all nodes and update the healthy_nodes list.
    """
    global healthy_nodes
    statuses = []

    async with httpx.AsyncClient(timeout=3.0) as client:
        for url in NODE_URLS:
            node_id = _url_to_node_id(url)
            try:
                response = await client.get(f"{url}/node/health")
                is_healthy = response.status_code == 200
            except Exception:
                is_healthy = False

            statuses.append({
                "node_id": node_id,
                "url": url,
                "status": "healthy" if is_healthy else "degraded",
            })

            if is_healthy and url not in healthy_nodes:
                healthy_nodes.append(url)
                print(f"[COORDINATOR] Node recovered: {node_id}")
            elif not is_healthy and url in healthy_nodes:
                healthy_nodes.remove(url)
                print(f"[COORDINATOR] Node marked degraded: {node_id}")

    return statuses


async def _write_to_single_node(
    client: httpx.AsyncClient, url: str, block_id: str, data: str, checksum: str
):
    response = await client.post(
        f"{url}/node/write",
        json={"block_id": block_id, "data": data, "checksum": checksum},
    )
    response.raise_for_status()
    return response.json()


def _url_to_node_id(url: str) -> str:
    parts = url.rstrip("/").split(":")
    port = parts[-1]
    mapping = {"8001": "node-1", "8002": "node-2", "8003": "node-3"}
    return mapping.get(port, url)
