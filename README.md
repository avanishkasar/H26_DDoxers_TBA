# H26_DDoxers_TBA

> Team **DDoxers** at Hacktoberfest Hack Day Mumbai × ISTE KJSSE (15 Oct 2026).
> Project name and problem statement are announced at 10:30 AM; this README is updated as we build.

## Project description

_TBA after the problem statement reveal._ What it does, who it's for, and the demo flow go here.

## Tech stack

| Layer    | Tech                                                                  |
| -------- | --------------------------------------------------------------------- |
| Backend  | Python 3.12, FastAPI, Pydantic v2, pydantic-settings, httpx (async)   |
| Frontend | React 19, TypeScript (strict), Vite, Tailwind CSS v4, lucide-react    |
| AI       | Gemma 4 (open-weight) served locally by [Ollama](https://ollama.com)  |
| Infra    | Docker Compose, nginx (SSE-friendly reverse proxy), GitHub Actions CI |

## AI usage

- **Runtime model:** Gemma 4 running locally through Ollama. No cloud or paid APIs are called (event rule).
  The backend talks to Ollama's `/api/chat` endpoint and streams tokens to the UI over Server-Sent Events.
- **Development tools:** AI coding assistants were used to generate the starter scaffold (see below) and
  may be used for debugging and documentation during the event. All AI output is reviewed by the team.

## Pre-existing work disclosure

The following boilerplate was prepared **before** the hackathon and contains no problem-specific logic:

- FastAPI app skeleton with `/api/health`, `/api/chat`, `/api/chat/stream` (Ollama proxy) and tests
- React + Tailwind chat shell with model status badge
- Docker Compose, `.env.example`, CI workflow, PowerShell setup scripts

Everything built on top of this after 10:30 AM on 15 Oct 2026 is original hackathon work; see the commit history.

## Local setup (Windows, PowerShell 7)

### Prerequisites

```powershell
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS
winget install Git.Git
winget install Ollama.Ollama
```

### 1. Pull the model

```powershell
ollama pull gemma4
ollama list   # confirm the exact tag and put it in OLLAMA_MODEL in .env
```

### 2. Install dependencies and create `.env`

```powershell
pwsh ./scripts/setup.ps1
```

### 3. Run

```powershell
pwsh ./scripts/dev.ps1
```

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

Or run each side manually in two terminals:

```powershell
# Terminal 1
Set-Location backend
./.venv/Scripts/Activate.ps1
uvicorn app.main:app --reload --port 8000

# Terminal 2
Set-Location frontend
npm run dev
```

### Docker (alternative)

Uses an Ollama running on the host by default:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

UI at http://localhost:8080. To run Ollama in a container instead, set
`OLLAMA_BASE_URL_DOCKER=http://ollama:11434` in `.env`, then:

```powershell
docker compose --profile ollama up --build
docker compose exec ollama ollama pull gemma4
```

## Checks

```powershell
# Backend
Set-Location backend
ruff check . ; ruff format --check . ; mypy app ; pytest -q

# Frontend
Set-Location ../frontend
npm run lint ; npm run build
```

## Project structure

```
backend/   FastAPI app (app/), tests, Dockerfile
frontend/  React + Vite + Tailwind app, nginx config, Dockerfile
scripts/   PowerShell setup and dev runner
```

## Contributing

Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:` ...), small commits, branch per feature,
PR into `main`. Never commit `.env` or any credentials.

## License

[Apache-2.0](LICENSE)
