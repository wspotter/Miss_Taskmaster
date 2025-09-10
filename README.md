# Miss_TaskMaster

![Miss_TaskMaster Logo](https://img.shields.io/badge/Miss_TaskMaster-Multi--Agent-Dev-blue?style=for-the-badge&logo=github)

**A sophisticated multi-agent system for LLM-driven development** that implements the **Multi-Context Protocol** to manage and execute complex software development projects with high fidelity.

[![Docker](https://img.shields.io/badge/Docker-Ready-green?style=flat-square&logo=docker)](docker-compose.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](requirements.txt)
[![FastAPI](https://img.shields.io/badge/FastAPI-Modern-green?style=flat-square&logo=fastapi)](mcp_server/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-blue?style=flat-square&logo=openai)](src/supermanus)

## 🌟 Key Features

### Multi-Agent Architecture
- **Gatekeeper Agent**: Strategic planner managing complete project context
- **Coding Agent**: Tactical executor focused on single tasks with LLM capabilities
- **MCP Server**: Standardized API endpoints for external integrations
- **VSCode Extension**: Rich IDE integration with project management tools

### Advanced Capabilities
- **Structured JSON Logging**: Machine-readable logs with performance metrics
- **Real-time Monitoring**: Task completion tracking and agent performance analytics
- **Docker Containerization**: Full containerized deployment with Docker Compose
- **Health Monitoring**: Built-in health checks and error reporting
- **API Gateway**: Comprehensive REST API with CORS support

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/wspotter/Miss_Taskmaster.git
cd miss_taskmaster

# Copy environment configuration
cp .env.example .env
# Edit .env with your API keys and settings

# Start the full system
docker-compose up --build

# Access the MCP Server
curl http://localhost:8000/health
```

### Manual Installation
```bash
# Install Python dependencies
pip install -r requirements.txt
pip install -r mcp_server/requirements.txt

# Start MCP Server
cd mcp_server
python main.py

# Or start Main Application
cd ..
python main.py run
```

## 📋 Core Architecture

### Multi-Context Protocol Design
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Human User    │───▶│ Gatekeeper Agent │───▶│ Coding Agent    │
│                 │    │  (Full Context) │    │ (Task Context)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                      │
                                ▼                      ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   MCP Server     │    │ VSCode Extension │
                       │  (REST APIs)     │    │  (Rich UI)       │
                       └─────────────────┘    └─────────────────┘
```

### Key Components

#### 🎯 Gatekeeper Agent
- **Location**: `src/supermanus/gatekeeper_agent.py`
- **Purpose**: Manages complete project context, dispenses tasks to Coding Agent
- **Features**: Plan parsing, progress monitoring, validation, human interaction

#### 🤖 Coding Agent
- **Location**: `src/supermanus/coding_agent.py`
- **Purpose**: Executes individual tasks with LLM capabilities
- **Features**: Task interpretation, tool usage, progress reporting, enforced compliance

#### 🌐 MCP Server
- **Location**: `mcp_server/`
- **Purpose**: Standardized API interface for external integrations
- **Features**: REST endpoints, health monitoring, metrics collection, CORS support

#### 🔧 VSCode Extension
- **Location**: `vscode_extension/`
- **Purpose**: Provides rich IDE integration for project management
- **Features**: Tree views, project plans, task status, logs viewer

## 📚 API Documentation

### MCP Server Endpoints

#### Health & Monitoring
- `GET /health` - System health check
- `GET /logs` - Retrieve system logs
- `GET /metrics` - Get performance metrics

#### Project Management
- `POST /project/init` - Initialize new project
- `GET /project/status` - Get current project status
- `GET /tasks` - List all project tasks

#### Agent Control
- `POST /orchestration/run` - Trigger agent orchestration
- `POST /task/report` - Report task completion/failure

### Python Client Example

```python
# mcp_server/client_example.py
from client_example import MCPServerClient

client = MCPServerClient("http://localhost:8000")

# Initialize project
client.init_project("project_plan_template.json")

# Check status
status = client.get_project_status()

# Run orchestration
client.run_orchestration()

# Monitor progress
tasks = client.get_task_list()
```

## 🐳 Docker Compose Setup

The system includes a comprehensive Docker Compose setup:

```yaml
# docker-compose.yml
version: '3.8'
services:
  mcp-server:    # Main API server
  redis:         # Optional caching
  prometheus:    # Metrics collection (monitoring profile)
  grafana:       # Metrics visualization (monitoring profile)
```

### Available Profiles
- **Default**: MCP Server with Redis caching
- **Monitoring**: Full monitoring stack with Prometheus + Grafana
- **Development**: Reloading and debug capabilities

## 📊 Monitoring & Metrics

### Built-in Metrics Collectors
- **TaskMetricsCollector**: Task completion times, success rates, agent performance
- **SystemHealthCollector**: API metrics, error rates, health monitoring

### Logs & Alerting
- **Structured JSON Logs**: Machine-readable logs with contextual data
- **Health Checks**: Automatic health monitoring with Docker healthcheck
- **Performance Monitoring**: Timing decorators for function performance tracking

## 🔒 Security & Production

### Production Deployment Checklist
- [ ] Set secure `SECRET_KEY` in environment
- [ ] Enable authentication/authorization for API endpoints
- [ ] Use production-grade database (PostgreSQL instead of JSON files)
- [ ] Implement rate limiting for API endpoints
- [ ] Configure proper CORS policies
- [ ] Set up SSL/TLS encryption
- [ ] Implement log rotation and archival

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here

# Optional (with defaults)
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
METRICS_ENABLED=true
```

## 🎛️ Advanced Configuration

### Custom Task Handlers
Extend the Coding Agent with custom task handlers:

```python
# In src/supermanus/coding_agent.py
def custom_task_handler(self, task: Dict[str, Any]) -> Dict[str, Any]:
    """Handle custom task types"""
    return {
        "status": "completed",
        "output": f"Custom handling for task: {task['id']}",
        "custom_data": "..."
    }
```

### Integration Hooks
The system provides several integration points:
- **Pre-task hooks**: Validate task requirements
- **Post-task hooks**: Process completion results
- **Error handlers**: Custom error processing
- **Metrics collectors**: Custom monitoring points

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Implement** your changes with tests
4. **Commit** with clear messages: `git commit -m "Add feature X"`
5. **Push** to your fork: `git push origin feature/your-feature`
6. **Create** a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
pytest

# Start development server with reloading
python -m uvicorn mcp_server.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Testing

### Running Tests
```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=src --cov-report=html
```

### Test Coverage Goals
- **Unit Tests**: 85%+ coverage for core modules
- **Integration Tests**: Full API endpoint testing
- **Performance Tests**: Load testing for high-throughput scenarios

## 📈 Performance Benchmarks

### Average Task Completion Times
- **Low Risk Tasks**: 2-5 minutes
- **Medium Risk Tasks**: 5-15 minutes
- **High Risk Tasks**: 30-60 minutes (with human review)

### API Performance
- **Health Check**: <100ms
- **Status Query**: <500ms
- **Task Report**: <200ms
- **Orchestration Trigger**: <300ms

## 🐛 Troubleshooting

### Common Issues

#### MCP Server Won't Start
```bash
# Check Python dependencies
pip install -r mcp_server/requirements.txt

# Check port availability
lsof -i :8000

# Check logs
tail -f mcp_server.log
```

#### Docker Build Failures
```bash
# Clean Docker cache
docker system prune -f

# Rebuild without cache
docker-compose build --no-cache
```

#### Task Execution Timeouts
- Check OpenAI API key configuration
- Verify network connectivity
- Monitor system resources during execution

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI**: For providing the GPT-4 API capabilities
- **FastAPI**: For the exceptional web framework
- **VSCode Team**: For the extensible IDE platform
- **Docker**: For containerization technology

## 🚧 Roadmap

### Version 1.1.0 (Upcoming)
- [ ] PostgreSQL integration for persistent state
- [ ] Real-time WebSocket support
- [ ] Advanced error recovery mechanisms
- [ ] Plugin system for custom task handlers

### Future Releases
- [ ] Multi-project support
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard
- [ ] CI/CD pipeline integration

---

**⭐ Star this repo if you find Miss_TaskMaster useful!**

For more information, visit our [GitHub Repository](https://github.com/wspotter/Miss_Taskmaster) or check the detailed [Design Document](multi_agent_system_design.md).