# Macro Chef Frontend

React + TypeScript frontend for Macro Chef meal planning application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   │   └── layout/      # Layout components (Header, Sidebar)
│   ├── pages/           # Route pages
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API client functions
│   ├── types/           # TypeScript type definitions
│   └── lib/             # Utilities
├── public/
└── package.json
```

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS
- **React Router** - Client-side routing
- **React Query** - Server state management
- **Axios** - HTTP client
- **Lucide React** - Icons

## Development

The frontend connects to the FastAPI backend running on port 8000 by default. Make sure the backend is running before starting the frontend.
