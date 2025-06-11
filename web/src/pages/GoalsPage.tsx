import { useState } from 'react'
import { Plus } from 'lucide-react'

interface Goal {
  id: string
  title: string
  targetAmount: number
  currentAmount: number
  deadline: Date
  category: string
}

export function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([
    {
      id: '1',
      title: 'Emergency Fund',
      targetAmount: 10000,
      currentAmount: 5000,
      deadline: new Date('2024-12-31'),
      category: 'Savings',
    },
    {
      id: '2',
      title: 'New Car',
      targetAmount: 25000,
      currentAmount: 15000,
      deadline: new Date('2025-06-30'),
      category: 'Vehicle',
    },
  ])

  const getProgress = (current: number, target: number) => {
    return (current / target) * 100
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Financial Goals</h2>
          <p className="text-muted-foreground">
            Track and manage your financial goals
          </p>
        </div>
        <button className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          <Plus className="mr-2 h-4 w-4" />
          Add Goal
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {goals.map((goal) => (
          <div
            key={goal.id}
            className="rounded-lg border bg-card p-6 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">{goal.title}</h3>
              <span className="text-sm text-muted-foreground">
                {goal.category}
              </span>
            </div>
            <div className="mt-4">
              <div className="flex justify-between text-sm">
                <span>Progress</span>
                <span>
                  ${goal.currentAmount.toLocaleString()} / $
                  {goal.targetAmount.toLocaleString()}
                </span>
              </div>
              <div className="mt-2 h-2 w-full rounded-full bg-muted">
                <div
                  className="h-2 rounded-full bg-primary"
                  style={{
                    width: `${getProgress(
                      goal.currentAmount,
                      goal.targetAmount
                    )}%`,
                  }}
                />
              </div>
            </div>
            <div className="mt-4 text-sm text-muted-foreground">
              Target: {goal.deadline.toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 