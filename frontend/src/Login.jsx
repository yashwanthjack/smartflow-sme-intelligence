import { useState } from 'react'
import { useAuth } from './AuthContext'
import { Zap, Mail, Lock, User, AlertCircle, CheckCircle } from 'lucide-react'

export default function Login() {
    const { login, register } = useAuth()
    const [isRegister, setIsRegister] = useState(false)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [fullName, setFullName] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setSuccess('')
        setLoading(true)

        let result
        if (isRegister) {
            result = await register(email, password, fullName)
        } else {
            result = await login(email, password)
        }

        if (result.success) {
            setSuccess(isRegister ? 'Account created!' : 'Welcome back!')
        } else {
            setError(result.error)
        }
        setLoading(false)
    }

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--bg-primary)',
            padding: 20
        }}>
            <div className="card" style={{
                width: '100%',
                maxWidth: 400,
                padding: 40,
                textAlign: 'center'
            }}>
                {/* Logo */}
                <div style={{ marginBottom: 24 }}>
                    <div style={{
                        width: 60, height: 60,
                        background: 'linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%)',
                        borderRadius: 16,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 16px'
                    }}>
                        <Zap size={32} color="white" />
                    </div>
                    <h1 style={{ fontSize: 24, marginBottom: 4 }}>SmartFlow OS</h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
                        {isRegister ? 'Create your account' : 'Sign in to continue'}
                    </p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit}>
                    {isRegister && (
                        <div style={{ position: 'relative', marginBottom: 16 }}>
                            <User size={18} style={{ position: 'absolute', left: 14, top: 14, color: 'var(--text-muted)' }} />
                            <input
                                type="text"
                                placeholder="Full Name"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '14px 14px 14px 44px',
                                    background: 'var(--bg-secondary)',
                                    border: '1px solid var(--glass-border)',
                                    borderRadius: 8,
                                    color: 'white',
                                    fontSize: 14
                                }}
                            />
                        </div>
                    )}

                    <div style={{ position: 'relative', marginBottom: 16 }}>
                        <Mail size={18} style={{ position: 'absolute', left: 14, top: 14, color: 'var(--text-muted)' }} />
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                padding: '14px 14px 14px 44px',
                                background: 'var(--bg-secondary)',
                                border: '1px solid var(--glass-border)',
                                borderRadius: 8,
                                color: 'white',
                                fontSize: 14
                            }}
                        />
                    </div>

                    <div style={{ position: 'relative', marginBottom: 24 }}>
                        <Lock size={18} style={{ position: 'absolute', left: 14, top: 14, color: 'var(--text-muted)' }} />
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                padding: '14px 14px 14px 44px',
                                background: 'var(--bg-secondary)',
                                border: '1px solid var(--glass-border)',
                                borderRadius: 8,
                                color: 'white',
                                fontSize: 14
                            }}
                        />
                    </div>

                    {error && (
                        <div style={{
                            padding: 12,
                            background: 'rgba(239, 68, 68, 0.1)',
                            border: '1px solid rgba(239, 68, 68, 0.2)',
                            borderRadius: 8,
                            color: 'var(--danger)',
                            fontSize: 13,
                            marginBottom: 16,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8
                        }}>
                            <AlertCircle size={16} /> {error}
                        </div>
                    )}

                    {success && (
                        <div style={{
                            padding: 12,
                            background: 'rgba(16, 185, 129, 0.1)',
                            border: '1px solid rgba(16, 185, 129, 0.2)',
                            borderRadius: 8,
                            color: 'var(--success)',
                            fontSize: 13,
                            marginBottom: 16,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8
                        }}>
                            <CheckCircle size={16} /> {success}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={loading}
                        style={{ width: '100%', padding: 14, fontSize: 15 }}
                    >
                        {loading ? 'Please wait...' : (isRegister ? 'Create Account' : 'Sign In')}
                    </button>
                </form>

                {/* Toggle */}
                <div style={{ marginTop: 24, color: 'var(--text-muted)', fontSize: 13 }}>
                    {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
                    <button
                        onClick={() => { setIsRegister(!isRegister); setError(''); setSuccess('') }}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: 'var(--accent-primary)',
                            cursor: 'pointer',
                            textDecoration: 'underline'
                        }}
                    >
                        {isRegister ? 'Sign In' : 'Register'}
                    </button>
                </div>
            </div>
        </div>
    )
}
