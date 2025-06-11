import { ReactNode } from 'react'
import { Link } from 'react-router-dom'

interface MainLayoutProps {
  children: ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container flex h-16 items-center px-4">
          <Link to="/" className="font-bold">
            FinmateAI
          </Link>
          <nav className="ml-auto flex gap-4">
            <Link to="/dashboard" className="text-sm font-medium">
              Dashboard
            </Link>
            <Link to="/transactions" className="text-sm font-medium">
              Transactions
            </Link>
          </nav>
        </div>
      </header>
      <main className="container py-6 px-4">
        {children}
      </main>
    </div>
  )
} 