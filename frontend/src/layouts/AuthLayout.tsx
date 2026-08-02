import { Outlet } from 'react-router-dom'
import { Brain } from 'lucide-react'

export function AuthLayout() {
  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md flex flex-col items-center">
        <div className="flex items-center space-x-2 text-primary mb-6">
          <Brain className="h-10 w-10" />
          <span className="text-3xl font-bold tracking-tight">Knowledgify</span>
        </div>
        <h2 className="mt-2 text-center text-3xl font-bold tracking-tight text-foreground">
          Welcome back
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-card py-8 px-4 shadow sm:rounded-lg sm:px-10 border">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
