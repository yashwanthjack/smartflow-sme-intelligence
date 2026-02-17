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
        <div className="flex items-center justify-center min-h-screen" style={{
            background: 'radial-gradient(circle at top left, #f0fdf4 0%, #fff 50%, #eff6ff 100%)',
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        }}>
            <div className="card" style={{ width: '100%', maxWidth: '420px', padding: '40px' }}>
                {/* Logo & Header */}
                <div className="flex flex-col items-center mb-8" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '32px' }}>
                    <div style={{
                        width: '56px', height: '56px',
                        background: 'linear-gradient(135deg, var(--accent-secondary) 0%, #ea580c 100%)',
                        borderRadius: '16px',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        marginBottom: '16px',
                        boxShadow: '0 10px 25px -5px rgba(249, 115, 22, 0.4)'
                    }}>
                        <Zap size={32} color="white" fill="white" />
                    </div>
                    <h1 style={{ fontSize: '28px', fontWeight: '800', color: '#111827', letterSpacing: '-0.5px', margin: '0 0 8px 0' }}>
                        SmartFlow OS
                    </h1>
                    <p style={{ color: '#6b7280', margin: 0, fontSize: '15px' }}>
                        {isRegister ? 'Create your workspace' : 'Welcome back, Founder'}
                    </p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {isRegister && (
                        <div style={{ position: 'relative' }}>
                            <User size={18} style={{ position: 'absolute', left: '12px', top: '14px', color: '#9ca3af' }} />
                            <input
                                type="text"
                                placeholder="Full Name"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                className="input"
                                style={{ paddingLeft: '40px', color: '#111827' }}
                            />
                        </div>
                    )}

                    <div style={{ position: 'relative' }}>
                        <Mail size={18} style={{ position: 'absolute', left: '12px', top: '14px', color: '#9ca3af' }} />
                        <input
                            type="email"
                            placeholder="work@company.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="input"
                            style={{ paddingLeft: '40px', color: '#111827' }}
                        />
                    </div>

                    <div style={{ position: 'relative' }}>
                        <Lock size={18} style={{ position: 'absolute', left: '12px', top: '14px', color: '#9ca3af' }} />
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="input"
                            style={{ paddingLeft: '40px', color: '#111827' }}
                        />
                    </div>

                    {error && (
                        <div style={{
                            display: 'flex', alignItems: 'center', gap: '8px',
                            padding: '12px', fontSize: '14px',
                            color: '#dc2626', background: '#fef2f2',
                            borderRadius: '8px', border: '1px solid #fee2e2'
                        }}>
                            <AlertCircle size={16} />
                            <span>{error}</span>
                        </div>
                    )}

                    {success && (
                        <div style={{
                            display: 'flex', alignItems: 'center', gap: '8px',
                            padding: '12px', fontSize: '14px',
                            color: '#16a34a', background: '#f0fdf4',
                            borderRadius: '8px', border: '1px solid #dcfce7'
                        }}>
                            <CheckCircle size={16} />
                            <span>{success}</span>
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="btn btn-primary"
                        style={{
                            height: '48px',
                            fontSize: '16px',
                            marginTop: '8px',
                            background: '#111827',
                            justifyContent: 'center',
                            width: '100%'
                        }}
                    >
                        {loading ? 'Processing...' : (isRegister ? 'Create Account' : 'Sign In')}
                        {!loading && <Zap size={18} style={{ marginLeft: '6px' }} />}
                    </button>
                </form>

                {/* Footer */}
                <div style={{ marginTop: '32px', textAlign: 'center' }}>
                    <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
                        {isRegister ? 'Already have an account?' : "New to SmartFlow?"}{' '}
                        <button
                            onClick={() => { setIsRegister(!isRegister); setError(''); setSuccess('') }}
                            style={{
                                color: '#ea580c',
                                fontWeight: '600',
                                background: 'transparent',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '14px'
                            }}
                        >
                            {isRegister ? 'Sign In' : 'Join Now'}
                        </button>
                    </p>
                </div>
            </div>
        </div>
    )
}
