import { useState, useCallback } from 'react'
import { useAuth } from '../AuthContext'
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
    Area,
    ComposedChart
} from 'recharts'
import { Users, TrendingUp, DollarSign, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

const API_BASE = '/api'

const formatINR = (amount) => {
    if (amount === null || amount === undefined) return '₹0'
    const absAmount = Math.abs(amount)
    if (absAmount >= 10000000) {
        return `₹${(amount / 10000000).toFixed(2)}Cr`
    } else if (absAmount >= 100000) {
        return `₹${(amount / 100000).toFixed(1)}L`
    } else if (absAmount >= 1000) {
        return `₹${(amount / 1000).toFixed(1)}K`
    }
    return `₹${amount.toFixed(0)}`
}

export default function ScenarioSimulator({ entityId }) {
    const { token } = useAuth()

    // Input state
    const [hiringCount, setHiringCount] = useState(0)
    const [salaryPerHire, setSalaryPerHire] = useState(80000)
    const [marketingIncrease, setMarketingIncrease] = useState(0)
    const [revenueGrowth, setRevenueGrowth] = useState(0)
    const [oneTimeExpense, setOneTimeExpense] = useState(0)

    // Result state
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const runSimulation = useCallback(async () => {
        setLoading(true)
        setError(null)

        try {
            const res = await fetch(`${API_BASE}/simulate/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    hiring_count: hiringCount,
                    monthly_salary_per_hire: salaryPerHire,
                    marketing_increase_percent: marketingIncrease,
                    revenue_growth_percent: revenueGrowth,
                    one_time_expense: oneTimeExpense
                })
            })

            if (res.ok) {
                const data = await res.json()
                setResult(data)
            } else {
                const err = await res.json()
                setError(err.detail || 'Simulation failed')
            }
        } catch (e) {
            setError('Connection error')
        }

        setLoading(false)
    }, [token, hiringCount, salaryPerHire, marketingIncrease, revenueGrowth, oneTimeExpense])

    const getStatusColor = (status) => {
        switch (status) {
            case 'SAFE': return '#10b981'
            case 'WARN': return '#f59e0b'
            case 'BLOCK': return '#ef4444'
            default: return '#6366f1'
        }
    }

    const getStatusIcon = (status) => {
        switch (status) {
            case 'SAFE': return <CheckCircle size={20} />
            case 'WARN': return <AlertTriangle size={20} />
            case 'BLOCK': return <XCircle size={20} />
            default: return null
        }
    }

    return (
        <div className="card" style={{ padding: 24 }}>
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 20 }}>
                📊 Scenario Simulator
            </h2>

            {/* Input Controls */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20, marginBottom: 24 }}>

                {/* Hiring */}
                <div>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, marginBottom: 8 }}>
                        <Users size={16} /> New Hires
                    </label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <input
                            type="range"
                            min="0"
                            max="10"
                            value={hiringCount}
                            onChange={(e) => setHiringCount(parseInt(e.target.value))}
                            style={{ flex: 1 }}
                        />
                        <span style={{ minWidth: 40, textAlign: 'right', fontWeight: 600 }}>{hiringCount}</span>
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
                        @ ₹{(salaryPerHire / 1000).toFixed(0)}k/mo each = {formatINR(hiringCount * salaryPerHire)}/mo
                    </div>
                </div>

                {/* Marketing */}
                <div>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, marginBottom: 8 }}>
                        <TrendingUp size={16} /> Marketing Increase
                    </label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <input
                            type="range"
                            min="0"
                            max="100"
                            value={marketingIncrease}
                            onChange={(e) => setMarketingIncrease(parseInt(e.target.value))}
                            style={{ flex: 1 }}
                        />
                        <span style={{ minWidth: 40, textAlign: 'right', fontWeight: 600 }}>{marketingIncrease}%</span>
                    </div>
                </div>

                {/* Revenue Growth */}
                <div>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, marginBottom: 8 }}>
                        <DollarSign size={16} /> Revenue Growth
                    </label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <input
                            type="range"
                            min="0"
                            max="50"
                            value={revenueGrowth}
                            onChange={(e) => setRevenueGrowth(parseInt(e.target.value))}
                            style={{ flex: 1 }}
                        />
                        <span style={{ minWidth: 40, textAlign: 'right', fontWeight: 600 }}>{revenueGrowth}%</span>
                    </div>
                </div>

                {/* One-time Expense */}
                <div>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, marginBottom: 8 }}>
                        One-time Expense
                    </label>
                    <input
                        type="number"
                        className="input"
                        value={oneTimeExpense}
                        onChange={(e) => setOneTimeExpense(parseFloat(e.target.value) || 0)}
                        placeholder="e.g. 500000"
                        style={{ width: '100%' }}
                    />
                </div>
            </div>

            {/* Run Button */}
            <button
                className="btn btn-primary"
                onClick={runSimulation}
                disabled={loading}
                style={{ width: '100%', marginBottom: 24 }}
            >
                {loading ? 'Simulating...' : 'Run Simulation'}
            </button>

            {error && (
                <div style={{ padding: 12, background: 'rgba(239, 68, 68, 0.1)', borderRadius: 8, color: '#ef4444', marginBottom: 16 }}>
                    {error}
                </div>
            )}

            {/* Results */}
            {result && (
                <div>
                    {/* Status Badge */}
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 12,
                        padding: 16,
                        borderRadius: 12,
                        background: `${getStatusColor(result.status)}15`,
                        border: `1px solid ${getStatusColor(result.status)}40`,
                        marginBottom: 20
                    }}>
                        <div style={{ color: getStatusColor(result.status) }}>
                            {getStatusIcon(result.status)}
                        </div>
                        <div>
                            <div style={{ fontWeight: 600, color: getStatusColor(result.status) }}>
                                {result.status} - {result.risk_level} Risk
                            </div>
                            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                                {result.impact_summary}
                            </div>
                        </div>
                    </div>

                    {/* Metrics Comparison */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16, marginBottom: 20 }}>
                        <div style={{ padding: 16, background: 'rgba(255,255,255,0.05)', borderRadius: 8 }}>
                            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Runway</div>
                            <div style={{ fontSize: 24, fontWeight: 'bold' }}>
                                {result.current_runway_months.toFixed(1)} → {result.new_runway_months.toFixed(1)} mo
                            </div>
                        </div>
                        <div style={{ padding: 16, background: 'rgba(255,255,255,0.05)', borderRadius: 8 }}>
                            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Monthly Burn</div>
                            <div style={{ fontSize: 24, fontWeight: 'bold' }}>
                                {formatINR(result.current_monthly_burn)} → {formatINR(result.new_monthly_burn)}
                            </div>
                        </div>
                    </div>

                    {/* AI Recommendation */}
                    <div style={{
                        padding: 16,
                        background: 'rgba(99, 102, 241, 0.1)',
                        borderRadius: 12,
                        borderLeft: '4px solid #6366f1',
                        marginBottom: 20
                    }}>
                        <div style={{ fontSize: 12, color: '#6366f1', marginBottom: 4 }}>AI Recommendation</div>
                        <div style={{ fontSize: 14, lineHeight: 1.5 }}>{result.ai_recommendation}</div>
                    </div>

                    {/* 12-Month Projection Chart */}
                    <div style={{ height: 280 }}>
                        <ResponsiveContainer>
                            <ComposedChart data={result.projection_series}>
                                <defs>
                                    <linearGradient id="balanceGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={11} />
                                <YAxis stroke="var(--text-muted)" fontSize={11} tickFormatter={(v) => `₹${v / 100000}L`} />
                                <Tooltip
                                    contentStyle={{ background: 'var(--bg-card)', borderColor: 'var(--glass-border)', borderRadius: 8 }}
                                    formatter={(v) => formatINR(v)}
                                />
                                <ReferenceLine y={result.projection_series[0]?.threshold || 500000} stroke="#f59e0b" strokeDasharray="5 5" label="Safety Threshold" />
                                <Area type="monotone" dataKey="balance" stroke="#6366f1" fill="url(#balanceGradient)" name="Projected Balance" />
                                <Line type="monotone" dataKey="threshold" stroke="#f59e0b" strokeDasharray="5 5" dot={false} name="Safety Line" />
                            </ComposedChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    )
}
