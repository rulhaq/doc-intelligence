# QPP Legal Intelligence Platform

A state-of-the-art Retrieval-Augmented Generation (RAG) application for legal intelligence, built with React, FastAPI, vLLM (Llama 3.2:1b), and Qdrant.

## Features

- **Intelligence & Insights**: Automated executive summaries and risk signal extraction.
- **Case Comparison**: Side-by-side analysis of legal cases with similarity scoring.
- **Conversational Chat**: Q&A assistant with real-time document citations.
- **Source Inspector**: Deep dive into document evidence with provenance tracking.

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS (via custom design tokens), Framer Motion.
- **Internationalization**: react-i18next with Arabic/English bilingual support and RTL layout.
- **Backend**: FastAPI, vLLM, Qdrant Vector DB, LangChain.
- **Model**: Llama 3.2:1b (via vLLM).
- **Deployment**: Docker, Docker Compose, OpenShift AI.

## Language Support

The platform supports **bilingual operation** in Arabic and English:
- Full UI translation for both languages
- Right-to-Left (RTL) layout support for Arabic
- Language switcher in header and login page
- Automatic language detection
- Persistent language preference

See [BILINGUAL_SETUP.md](BILINGUAL_SETUP.md) for detailed information.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local backend development)
- Node.js 18+ (for local frontend development)
- Hugging Face API Token (for Llama model access)

### Quick Start with Docker

1. Clone the repository.
2. Create a `.env` file from `.env.example` and add your `HUGGING_FACE_HUB_TOKEN`.
3. Run the application:
   ```bash
   docker-compose up -d
   ```
4. Access the frontend at `http://localhost:3000`.
5. Access the API documentation at `http://localhost:8000/docs`.

### Local Development Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Development Tools

This project includes several development tools to maintain code quality:

#### Backend
- **Black**: Code formatting (`black .`)
- **isort**: Import sorting (`isort .`)
- **flake8**: Linting (`flake8 .`)
- **pytest**: Testing (`pytest`)

#### Frontend
- **ESLint**: Code linting (`npm run lint`)
- **Prettier**: Code formatting (`npm run format`)

#### Makefile Commands

For convenience, use the Makefile for common tasks:

```bash
make install          # Install all dependencies
make dev              # Start development servers
make test             # Run all tests
make lint             # Run all linters
make format           # Format all code
make docker-build     # Build Docker images
make docker-up        # Start Docker containers
```

See `make help` for all available commands.

## Testing

### Backend Tests

```bash
cd backend
pytest                    # Run all tests
pytest --cov=.           # Run with coverage
pytest tests/test_auth.py  # Run specific test file
```

### Frontend Tests

```bash
cd frontend
npm test                  # Run tests (when configured)
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Security

For security concerns, please see [SECURITY.md](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Deployment to OpenShift AI

Use the OpenShift template in `openshift/template.yaml` (builds images from your Git repo and deploys frontend + backend).

- Instructions: `openshift/README.md`
- You will still need reachable services for PostgreSQL, Qdrant, and vLLM (configure via template parameters).
