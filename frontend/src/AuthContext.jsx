import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [token, setToken] = useState(localStorage.getItem('smartflow_token'))
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (token) {
            fetchCurrentUser()
        } else {
            setLoading(false)
        }
    }, [token])

    const fetchCurrentUser = async () => {
        try {
            const res = await fetch('/api/auth/me', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const userData = await res.json()
                setUser(userData)
            } else {
                // Token invalid, clear it
                logout()
            }
        } catch (err) {
            console.error('Auth error:', err)
            logout()
        }
        setLoading(false)
    }

    const login = async (email, password) => {
        const formData = new URLSearchParams()
        formData.append('username', email)
        formData.append('password', password)

        const res = await fetch('/api/auth/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        })

        if (res.ok) {
            const data = await res.json()
            localStorage.setItem('smartflow_token', data.access_token)
            setToken(data.access_token)
            return { success: true }
        } else {
            const error = await res.json()
            return { success: false, error: error.detail || 'Login failed' }
        }
    }

    const register = async (email, password, fullName) => {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name: fullName })
        })

        if (res.ok) {
            // Auto-login after registration
            return login(email, password)
        } else {
            const error = await res.json()
            return { success: false, error: error.detail || 'Registration failed' }
        }
    }

    const logout = () => {
        localStorage.removeItem('smartflow_token')
        setToken(null)
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
