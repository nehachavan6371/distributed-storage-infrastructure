# 🗄️ Distributed Storage Infrastructure & Reliability System

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![AWS](https://img.shields.io/badge/AWS_S3-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)

A production-inspired distributed block-storage system simulating multi-node data replication, fault tolerance, and real-time reliability monitoring — built to mirror the engineering challenges at scale (Apple Cloud, AWS, GCP).

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Monitoring](#-monitoring)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Screenshots](#-screenshots)

---

## 🧠 Overview

This project simulates a **distributed block-storage infrastructure** across multiple nodes — replicating real-world patterns used in production storage systems at companies like Apple, Google, and Amazon.

Key engineering goals:
- Simulate geographically-distributed data center topologies
- Enforce data consistency and replication across nodes
- Detect and recover from node failures automatically
- Expose storage operations via a REST API
- Monitor system health with real-time metrics

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
│              FastAPI REST Interface (:8000)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    COORDINATOR NODE                          │
│         Write Router │ Read Balancer │ Health Checker        │
└──────┬───────────────┬───────────────┬───────────────────────┘
       │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  STORAGE    │ │  STORAGE    │ │  STORAGE    │
│  NODE - 1   │ │  NODE - 2   │ │  NODE - 3   │
│  (Primary)  │ │ (Replica 1) │ │ (Replica 2) │
│  Port 8001  │ │  Port 8002  │ │  Port 8003  │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
┌──────▼───────────────▼───────────────▼───────┐
│              PostgreSQL + AWS S3              │
│         Persistent Storage & Metadata         │
└───────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  MONITORING LAYER                            │
│           Prometheus Metrics + Alert Manager                 │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. Client sends write request → Coordinator Node
2. Coordinator routes write to Primary Node
3. Primary replicates data to Replica 1 and Replica 2
4. Consistency check confirms all 3 nodes acknowledged
5. Read requests load-balanced across healthy nodes
6. Prometheus scrapes metrics every 15s; alerts fire on node failure

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔁 **Multi-node Replication** | Data written to primary is automatically replicated to 2 replica nodes |
| 🛡️ **Fault Tolerance** | Failed nodes detected within 30s; reads rerouted to healthy replicas |
| ✅ **Data Integrity Checks** | SHA-256 checksums validated on every read/write operation |
| 🐳 **Fully Containerized** | All nodes run as Docker containers; orchestrated via Docker Compose |
| 📊 **Real-time Monitoring** | Prometheus tracks uptime, latency, error rates per node |
| 🔔 **Auto Alerting** | Alerts fire when node uptime drops below 99% or error rate exceeds threshold |
| 🚀 **CI/CD Pipeline** | GitHub Actions automates build, test, and deployment on every push |
| 🐧 **Linux Automation** | Bash scripts handle provisioning, log rotation, and health checks |
| 🌐 **REST API** | FastAPI interface for all storage operations with Swagger docs |

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Language** | Python 3.10+ |
| **API Framework** | FastAPI |
| **Containerization** | Docker, Docker Compose |
| **Database** | PostgreSQL (metadata), AWS S3 (object storage) |
| **Monitoring** | Prometheus |
| **CI/CD** | GitHub Actions |
| **OS / Scripting** | Linux (Ubuntu), Bash |
| **Version Control** | Git, GitHub |

---

## 📁 Project Structure

```
distributed-storage-infrastructure/
│
├── coordinator/
│   ├── main.py              # Write router & read balancer
│   ├── health_checker.py    # Node health monitoring
│   └── replication.py       # Replication logic
│
├── storage_node/
│   ├── node.py              # Storage node service
│   ├── checksum.py          # SHA-256 integrity validation
│   └── recovery.py          # Fault recovery handler
│
├── api/
│   ├── routes.py            # FastAPI REST endpoints
│   ├── models.py            # Pydantic request/response models
│   └── auth.py              # API key authentication
│
├── monitoring/
│   ├── prometheus.yml       # Prometheus scrape config
│   └── alerts.yml           # Alert rules
│
├── scripts/
│   ├── provision.sh         # Linux system setup script
│   ├── health_check.sh      # Node health check script
│   └── log_rotation.sh      # Log management
│
├── tests/
│   ├── test_replication.py  # Replication unit tests
│   ├── test_api.py          # API integration tests
│   └── test_recovery.py     # Fault tolerance tests
│
├── docker-compose.yml       # Multi-container orchestration
├── Dockerfile               # Container image definition
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose installed
- Python 3.10+
- AWS account (for S3) or use local MinIO for testing

### 1. Clone the repository
```bash
git clone https://github.com/nehachavan6371/distributed-storage-infrastructure.git
cd distributed-storage-infrastructure
```

### 2. Set environment variables
```bash
cp .env.example .env
# Edit .env with your AWS credentials and config
```

### 3. Start all nodes with Docker Compose
```bash
docker-compose up --build
```

This spins up:
- 1 Coordinator Node (port 8000)
- 3 Storage Nodes (ports 8001, 8002, 8003)
- PostgreSQL (port 5432)
- Prometheus (port 9090)

### 4. Verify all nodes are healthy
```bash
bash scripts/health_check.sh
```

### 5. Open API docs
```
http://localhost:8000/docs
```

---

## 🌐 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/storage/write` | Write data block to distributed nodes |
| `GET` | `/storage/read/{block_id}` | Read data block from healthy node |
| `DELETE` | `/storage/delete/{block_id}` | Delete block from all nodes |
| `GET` | `/nodes/status` | Get health status of all nodes |
| `GET` | `/nodes/{node_id}/metrics` | Get metrics for a specific node |
| `POST` | `/nodes/{node_id}/recover` | Trigger manual node recovery |

### Example — Write a data block
```bash
curl -X POST http://localhost:8000/storage/write \
  -H "Content-Type: application/json" \
  -d '{"block_id": "blk_001", "data": "Hello, distributed world!", "replication_factor": 3}'
```

### Example Response
```json
{
  "block_id": "blk_001",
  "status": "success",
  "replicated_to": ["node-1", "node-2", "node-3"],
  "checksum": "a3f5c2...",
  "timestamp": "2024-11-01T10:30:00Z"
}
```

---

## 📊 Monitoring

Prometheus metrics available at `http://localhost:9090`

| Metric | Description |
|---|---|
| `storage_node_uptime_seconds` | Uptime per node |
| `storage_write_latency_ms` | Write operation latency |
| `storage_read_latency_ms` | Read operation latency |
| `storage_replication_errors_total` | Replication failure count |
| `storage_node_health_status` | 1 = healthy, 0 = degraded |

**Alert Rules:**
- 🔴 Node down for > 30 seconds → Critical alert
- 🟡 Error rate > 1% → Warning alert
- 🟡 Write latency > 500ms → Warning alert

---

## ⚙️ CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):

```
Push to main
     │
     ▼
┌─────────────┐
│  Run Tests  │  pytest - unit + integration tests
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Docker Build   │  Build & tag container image
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│  Security Scan       │  Trivy vulnerability scan
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Deploy to Staging   │  Docker Compose up on staging
└──────────────────────┘
```

---

## 🖥️ Screenshots

> Node health dashboard, API swagger UI, and Prometheus metrics screenshots — coming soon.

---

## 📄 License

MIT License — feel free to use, fork, and build on this project.

---

## 👩‍💻 Author

**Neha Chavhan**
[LinkedIn](https://www.linkedin.com/in/neha-chavan-1a32781a6/) • [GitHub](https://github.com/nehachavan6371)
