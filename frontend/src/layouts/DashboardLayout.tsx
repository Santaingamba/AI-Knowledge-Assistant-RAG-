import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, FileText, MessageSquare, Settings, LogOut, Brain } from 'lucide-react'
import { cn } from '@/lib/utils'
import api from '@/lib/api'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function DashboardLayout() {
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout')
    } catch {
      // Even if the backend call fails, clear local state
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col border-r bg-card">
        <div className="flex h-16 shrink-0 items-center px-6 border-b">
          <Brain className="h-6 w-6 text-primary mr-2" />
          <span className="text-lg font-semibold">Knowledgify</span>
        </div>
        <div className="flex flex-1 flex-col overflow-y-auto">
          <nav className="flex-1 space-y-1 px-4 py-4">
            {navigation.map((item) => {
              const isActive = location.pathname.startsWith(item.href)
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    isActive
                      ? 'bg-primary/10 text-primary'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors'
                  )}
                >
                  <item.icon
                    className={cn(
                      isActive ? 'text-primary' : 'text-muted-foreground group-hover:text-accent-foreground',
                      'mr-3 flex-shrink-0 h-5 w-5'
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </div>
        <div className="flex flex-shrink-0 border-t p-4">
          <button
            onClick={handleLogout}
            className="flex w-full items-center text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-3 py-2"
          >
            <LogOut className="mr-3 h-5 w-5" />
            Logout
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <main className="flex-1 overflow-y-auto bg-muted/20 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
