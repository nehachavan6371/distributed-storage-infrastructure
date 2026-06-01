"""Replication logic for distributed data consistency."""
import logging
from typing import List, Dict
import asyncio

logger = logging.getLogger(__name__)

class ReplicationManager:
    """Manages data replication across storage nodes."""
    
    def __init__(self, replication_factor: int = 3):
        self.replication_factor = replication_factor
        self.pending_replications: Dict[str, List[str]] = {}
        
    async def replicate_to_nodes(self, block_id: str, data: str, target_nodes: List[str]) -> bool:
        """Replicate data block to target nodes."""
        logger.info(f"Replicating block {block_id} to {len(target_nodes)} nodes")
        
        if len(target_nodes) < self.replication_factor:
            logger.warning(f"Insufficient nodes: {len(target_nodes)} < {self.replication_factor}")
            return False
        
        self.pending_replications[block_id] = target_nodes[:self.replication_factor]
        
        # Simulate parallel replication
        tasks = []
        for node in target_nodes[:self.replication_factor]:
            tasks.append(self._replicate_to_node(block_id, data, node))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for r in results if r is True)
        
        logger.info(f"Replication completed: {success_count}/{self.replication_factor} nodes confirmed")
        return success_count == self.replication_factor
    
    async def _replicate_to_node(self, block_id: str, data: str, node_id: str) -> bool:
        """Replicate data to a single node."""
        try:
            # Simulate network delay
            await asyncio.sleep(0.1)
            logger.debug(f"Data replicated to node {node_id}")
            return True
        except Exception as e:
            logger.error(f"Replication to {node_id} failed: {e}")
            return False
    
    def get_replication_status(self, block_id: str) -> Dict:
        """Get replication status for a block."""
        if block_id in self.pending_replications:
            return {
                "block_id": block_id,
                "replicated_to": self.pending_replications[block_id],
                "replication_factor": self.replication_factor
            }
        return {"block_id": block_id, "status": "not_found"}