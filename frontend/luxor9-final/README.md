# LUXOR9 - The Autonomous AI Company Operating System

<p align="center">
  <img src="https://img.shields.io/badge/AI%20Agents-179-blueviolet" alt="179 Agents">
  <img src="https://img.shields.io/badge/Income%20Streams-100-success" alt="100 Streams">
  <img src="https://img.shields.io/badge/For-Solo%20Founders-orange" alt="Solo Founders">
</p>

## What is LUXOR9?

**LUXOR9** is the autonomous AI company operating system that enables solo founders to build and scale their businesses using 179 intelligent AI agents managing 100 income streams.

### Key Features

- **179 AI Agents** across 5 tiers (Commander → C-Suite → VPs → Managers → Workers)
- **100 Income Streams** across 10 categories (AI Agency, SaaS, Creative, Finance, E-commerce, etc.)
- **Real-time Dashboard** with live metrics and monitoring
- **Parallel Execution** - all streams run simultaneously
- **Enterprise-Grade Security** with multi-layer validation

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Docker (for backend services)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/luxor9.git
cd luxor9

# Install dependencies
npm install

# Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the marketing site.

### Backend Setup

```bash
cd backend

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up -d

# Install Python dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload
```

API documentation available at [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

```
luxor9/
├── app/                    # Next.js App Router
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Homepage
│   └── globals.css         # Global styles + design tokens
├── components/
│   ├── ui/                 # Base UI components (Button, Card, Badge, etc.)
│   └── marketing/          # Marketing components (Navbar, Hero, Pricing, etc.)
├── lib/
│   └── utils.ts            # Utility functions
├── packages/
│   └── design-system/      # Design tokens (in progress)
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── agents/         # Agent implementations
│   │   ├── api/            # API routes
│   │   └── orchestrator.py # Main orchestrator
│   └── requirements.txt
└── docs/                   # Documentation
```

## Design System

The design system is built with Tailwind CSS and includes:

### Colors
- **Primary**: `#00d4ff` (Electric Cyan)
- **Secondary**: `#8b5cf6` (Purple)
- **Accent Colors**: Success, Warning, Error, Info

### Typography
- **Headings**: Inter (700, 800)
- **Body**: Inter (400, 500)
- **Code**: JetBrains Mono

### Components
- Button (variants: default, secondary, outline, ghost, success)
- Card (Header, Title, Description, Content, Footer)
- Badge (variants: default, secondary, success, warning, error, info)
- Input

## Marketing Site Pages

- `/` - Homepage with Hero, Features, How It Works, Pricing, CTA
- `/docs` - Documentation (coming soon)
- `/pricing` - Pricing page
- `/about` - About page

## API Endpoints

### System
- `GET /api/system/health` - Health check
- `POST /api/system/boot` - Boot all agents
- `POST /api/system/shutdown` - Shutdown
- `GET /api/system/state` - Get system state
- `GET /api/system/hierarchy` - Get agent hierarchy

### Agents
- `GET /api/agents` - List all agents
- `GET /api/agents/{id}` - Get agent details
- `POST /api/agents/{id}/start` - Start agent
- `POST /api/agents/{id}/stop` - Stop agent

### Streams
- `GET /api/streams` - List all streams
- `POST /api/streams/{id}/deploy` - Deploy stream
- `POST /api/streams/{id}/stop` - Stop stream

### Metrics
- `GET /api/metrics/live` - Live metrics
- `GET /api/metrics/revenue` - Revenue metrics

## Deployment

### Vercel (Frontend)

```bash
npm run build
vercel deploy
```

### Docker (Backend)

```bash
cd backend
docker-compose up -d
```

## Environment Variables

```env
# Backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/luxor9
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

---

**Built with love for solo founders and indie hackers.**
