# FinmateAI Web Frontend

This is the web frontend for FinmateAI, built with Vite, React, TypeScript, and modern web technologies.

## Tech Stack

- Vite
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Router DOM
- Axios
- Recharts
- React Hook Form
- Zustand

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env` file in the root directory with the following content:
   ```
   VITE_API_URL=http://localhost:8000
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Project Structure

```
src/
  ├── components/     # Reusable UI components
  ├── lib/           # Utility functions and configurations
  ├── pages/         # Page components
  ├── store/         # Zustand store
  ├── types/         # TypeScript type definitions
  └── utils/         # Helper functions
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking
