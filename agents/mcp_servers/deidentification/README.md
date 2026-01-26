# JSL MCP Servers (Deidentification)

© John Snow Labs 2026

Model Context Protocol (MCP) servers for Spark NLP Healthcare. Connect AI agents and IDEs to clinical NLP pipelines.

## 🚀 Quick Start

### Deidentification MCP Server

```bash
cd jsl-deid-mcp-server-v2
pip install -e .
python -m src.server
```

**Configure in Cursor/Claude/VS Code:**
- **URL**: `http://localhost:8001/mcp`
- **Transport**: `streamable-http`

See [jsl-deid-mcp-server-v2/README.md](jsl-deid-mcp-server-v2/README.md) for detailed setup instructions.

## 📦 Available Servers

| Server | Description | Port | Status |
|--------|-------------|------|--------|
| `jsl-deid-mcp-server-v2` | Clinical text deidentification (lightweight) | 8001 | ✅ Production |
| `jsl-deid-mcp-server-v1` | Clinical text deidentification (monolithic) | 8000 | ✅ Production |
| `deid-service` | REST API for deidentification | 9000 | ✅ Production |

## 🔧 Requirements

- Python 3.10+
- Docker (for `deid-service` and `jsl-deid-mcp-server-v1`)
- John Snow Labs Healthcare license

## 📚 Documentation

- [Deidentification MCP Server v2](jsl-deid-mcp-server-v2/README.md) - Lightweight server using deid-service
- [Deidentification MCP Server v1](jsl-deid-mcp-server-v1/README.md) - Monolithic server with embedded pipeline
- [REST API Service](deid-service/README.md) - FastAPI service for deidentification
- [MCP Protocol](https://modelcontextprotocol.io) - Model Context Protocol specification

## 🏗️ Architecture

### v2 Architecture (Recommended)

```
┌─────────────────┐     HTTP      ┌─────────────────┐
│  Client/Agent   │ ────────────► │  MCP Server v2  │
│  (Cursor, etc.) │   port 8001   │  (lightweight)  │
└─────────────────┘               └────────┬────────┘
                                           │ HTTP POST
                                           ▼
                                  ┌─────────────────┐
                                  │  deid-service   │
                                  │   port 9000     │
                                  │   [Pipeline]    │
                                  └─────────────────┘
```

**Recommended**: Use `jsl-deid-mcp-server-v2` + `deid-service` for instant startup and low memory footprint.

### v1 Architecture (Monolithic)

```
┌─────────────────┐     HTTP      ┌─────────────────────────┐
│  Client/Agent   │ ────────────► │     MCP Server v1       │
│  (Cursor, etc.) │   port 8000   │  ┌───────────────────┐  │
└─────────────────┘               │  │  Embedded Pipeline │  │
                                  │  │  (Spark NLP)       │  │
                                  │  └───────────────────┘  │
                                  │      [Docker Container] │
                                  └─────────────────────────┘
```

**Use case**: Self-contained deployment when running a separate `deid-service` is not desired.

## 🤝 Contributing

This repository contains official John Snow Labs MCP servers. For issues and feature requests, please open a GitHub issue.

## 📄 License

Requires John Snow Labs Healthcare NLP license. [Contact us](https://www.johnsnowlabs.com/contact/) for licensing.

---

**© John Snow Labs 2026**
