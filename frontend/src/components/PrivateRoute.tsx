import { Navigate, Outlet } from 'react-router-dom'

/**
 * Auth guard component. Checks for an access token in localStorage.
 * If absent, redirects to /login. Otherwise renders child routes via <Outlet />.
 *
 * NOTE: localStorage for JWT storage is a known XSS risk. For production,
 * switch to httpOnly cookies with the backend setting Set-Cookie headers.
 */
export function PrivateRoute() {
  const token = localStorage.getItem('access_token')

  if (!token) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
