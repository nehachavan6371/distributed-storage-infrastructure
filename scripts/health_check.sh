#!/bin/bash
# health_check.sh — Check health of all storage nodes
# Usage: bash scripts/health_check.sh

set -e

COORDINATOR="http://localhost:8000"
NODES=("http://localhost:8001" "http://localhost:8002" "http://localhost:8003")
NODE_NAMES=("node-1" "node-2" "node-3")

echo "============================================"
echo " Storage Infrastructure Health Check"
echo " $(date)"
echo "============================================"

# Check Coordinator
echo ""
echo "[ COORDINATOR ]"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$COORDINATOR/nodes/status" 2>/dev/null || echo "000")
if [ "$STATUS" == "200" ]; then
    echo "  ✅ Coordinator is HEALTHY (port 8000)"
    curl -s "$COORDINATOR/nodes/status" | python3 -m json.tool 2>/dev/null || true
else
    echo "  ❌ Coordinator is UNREACHABLE (HTTP $STATUS)"
fi

# Check each Storage Node
echo ""
echo "[ STORAGE NODES ]"
HEALTHY=0
for i in "${!NODES[@]}"; do
    URL="${NODES[$i]}"
    NAME="${NODE_NAMES[$i]}"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL/node/health" 2>/dev/null || echo "000")
    if [ "$STATUS" == "200" ]; then
        echo "  ✅ $NAME is HEALTHY ($URL)"
        HEALTHY=$((HEALTHY + 1))
    else
        echo "  ❌ $NAME is DEGRADED or UNREACHABLE (HTTP $STATUS)"
    fi
done

# Check Prometheus
echo ""
echo "[ PROMETHEUS ]"
PROM_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:9090/-/healthy" 2>/dev/null || echo "000")
if [ "$PROM_STATUS" == "200" ]; then
    echo "  ✅ Prometheus is running (port 9090)"
else
    echo "  ⚠️  Prometheus not reachable"
fi

# Summary
echo ""
echo "============================================"
echo " Summary: $HEALTHY/3 storage nodes healthy"
if [ "$HEALTHY" -ge 2 ]; then
    echo " Status: ✅ SYSTEM OPERATIONAL"
else
    echo " Status: ❌ SYSTEM DEGRADED — check node logs"
    echo " Run: docker-compose logs storage-node-X"
fi
echo "============================================"
