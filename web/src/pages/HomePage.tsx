import { Link } from 'react-router-dom'

export function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] text-center">
      <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
        Welcome to FinmateAI
      </h1>
      <p className="mt-6 text-lg leading-8 text-muted-foreground max-w-2xl">
        Your AI-powered financial companion. Get insights, track expenses, and make smarter financial decisions.
      </p>
      <div className="mt-10 flex items-center justify-center gap-x-6">
        <Link
          to="/dashboard"
          className="rounded-md bg-primary px-3.5 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm hover:bg-primary/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
        >
          Get Started
        </Link>
        <Link
          to="/login"
          className="text-sm font-semibold leading-6 text-foreground"
        >
          Sign in <span aria-hidden="true">→</span>
        </Link>
      </div>
    </div>
  )
} 