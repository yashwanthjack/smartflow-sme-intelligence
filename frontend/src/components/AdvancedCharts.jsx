import { useState, useEffect, useMemo } from 'react'
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Shield, Target, Calendar } from 'lucide-react'
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    AreaChart,
    Area,
    RadialBarChart,
    RadialBar,
    Legend
} from 'recharts'

const API_BASE = '/api'

// Format currency in Indian Rupees
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

// Credit Score Gauge
export function CreditScoreGauge({ score = 750, riskLevel = 'Low' }) {
    const getColor = (s) => {
        if (s >= 750) return '#10b981'
        if (s >= 650) return '#f59e0b'
        return '#ef4444'
    }

    const percentage = ((score - 300) / 600) * 100

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Credit Score</span>
                <Shield size={18} style={{ opacity: 0.5 }} />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', padding: '20px 0' }}>
                <div style={{ position: 'relative', width: 160, height: 80 }}>
                    <svg viewBox="0 0 160 80" style={{ width: '100%', height: '100%' }}>
                        {/* Background arc */}
                        <path
                            d="M 10 80 A 70 70 0 0 1 150 80"
                            fill="none"
                            stroke="rgba(255,255,255,0.1)"
                            strokeWidth="12"
                        />
                        {/* Score arc */}
                        <path
                            d="M 10 80 A 70 70 0 0 1 150 80"
                            fill="none"
                            stroke={getColor(score)}
                            strokeWidth="12"
                            strokeDasharray={`${percentage * 2.2} 220`}
                            style={{ transition: 'stroke-dasharray 1s ease' }}
                        />
                    </svg>
                    <div style={{
                        position: 'absolute',
                        bottom: 0,
                        left: '50%',
                        transform: 'translateX(-50%)',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: 28, fontWeight: 'bold', color: getColor(score) }}>{score}</div>
                    </div>
                </div>
                <div style={{ marginTop: 12, display: 'flex', gap: 8, alignItems: 'center' }}>
                    <span style={{
                        padding: '4px 12px',
                        borderRadius: 20,
                        background: `${getColor(score)}20`,
                        color: getColor(score),
                        fontSize: 12,
                        fontWeight: 600
                    }}>
                        {riskLevel} Risk
                    </span>
                </div>
            </div>
        </div>
    )
}

// Burn Rate Trend Chart
export function BurnTrendChart({ data = [] }) {
    // Generate mock data if none provided
    const chartData = data.length > 0 ? data : [
        { month: 'Aug', burn: 450000, revenue: 320000 },
        { month: 'Sep', burn: 480000, revenue: 380000 },
        { month: 'Oct', burn: 520000, revenue: 420000 },
        { month: 'Nov', burn: 490000, revenue: 460000 },
        { month: 'Dec', burn: 510000, revenue: 510000 },
        { month: 'Jan', burn: 530000, revenue: 580000 },
    ]

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Burn vs Revenue Trend</span>
                <TrendingUp size={18} style={{ opacity: 0.5 }} />
            </div>
            <div style={{ height: 260, width: '100%' }}>
                <ResponsiveContainer>
                    <AreaChart data={chartData}>
                        <defs>
                            <linearGradient id="colorBurn" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                        <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={12} />
                        <YAxis stroke="var(--text-muted)" fontSize={12} tickFormatter={(v) => `₹${v / 1000}k`} />
                        <Tooltip
                            contentStyle={{ background: 'var(--bg-card)', borderColor: 'var(--glass-border)', borderRadius: 8 }}
                            formatter={(v) => formatINR(v)}
                        />
                        <Area type="monotone" dataKey="burn" stroke="#ef4444" strokeWidth={2} fill="url(#colorBurn)" name="Burn" />
                        <Area type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={2} fill="url(#colorRevenue)" name="Revenue" />
                        <Legend />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}

// DSO (Days Sales Outstanding) Chart
export function DSOChart({ data = [] }) {
    const chartData = data.length > 0 ? data : [
        { month: 'Aug', dso: 52 },
        { month: 'Sep', dso: 48 },
        { month: 'Oct', dso: 45 },
        { month: 'Nov', dso: 42 },
        { month: 'Dec', dso: 38 },
        { month: 'Jan', dso: 35 },
    ]

    const avgDso = chartData.reduce((sum, d) => sum + d.dso, 0) / chartData.length
    const trend = chartData.length > 1 ? chartData[chartData.length - 1].dso - chartData[0].dso : 0

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Days Sales Outstanding (DSO)</span>
                <Calendar size={18} style={{ opacity: 0.5 }} />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 16 }}>
                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 28, fontWeight: 'bold' }}>{Math.round(avgDso)}</div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Avg Days</div>
                </div>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    padding: '4px 8px',
                    borderRadius: 6,
                    background: trend < 0 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    color: trend < 0 ? '#10b981' : '#ef4444',
                    fontSize: 12
                }}>
                    {trend < 0 ? <TrendingDown size={14} /> : <TrendingUp size={14} />}
                    {Math.abs(trend)} days
                </div>
            </div>
            <div style={{ height: 180, width: '100%' }}>
                <ResponsiveContainer>
                    <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                        <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={12} />
                        <YAxis stroke="var(--text-muted)" fontSize={12} />
                        <Tooltip
                            contentStyle={{ background: 'var(--bg-card)', borderColor: 'var(--glass-border)', borderRadius: 8 }}
                        />
                        <Bar dataKey="dso" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}

// Cash Velocity Chart (Inflows vs Outflows by week)
export function CashVelocityChart({ entityId }) {
    const { token } = useAuth()
    const [data, setData] = useState([])

    useEffect(() => {
        // Generate weekly mock data
        const weeks = ['W1', 'W2', 'W3', 'W4']
        const mockData = weeks.map(w => ({
            week: w,
            inflow: Math.floor(Math.random() * 200000) + 100000,
            outflow: Math.floor(Math.random() * 150000) + 80000
        }))
        setData(mockData)
    }, [entityId])

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Weekly Cash Velocity</span>
                <TrendingUp size={18} style={{ opacity: 0.5 }} />
            </div>
            <div style={{ height: 220, width: '100%' }}>
                <ResponsiveContainer>
                    <BarChart data={data} barGap={4}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                        <XAxis dataKey="week" stroke="var(--text-muted)" fontSize={12} />
                        <YAxis stroke="var(--text-muted)" fontSize={12} tickFormatter={(v) => `₹${v / 1000}k`} />
                        <Tooltip
                            contentStyle={{ background: 'var(--bg-card)', borderColor: 'var(--glass-border)', borderRadius: 8 }}
                            formatter={(v) => formatINR(v)}
                        />
                        <Legend />
                        <Bar dataKey="inflow" name="Inflows" fill="#10b981" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="outflow" name="Outflows" fill="#ef4444" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}

// Revenue Goal Progress
export function RevenueGoalProgress({ current = 580000, goal = 1000000 }) {
    const progress = Math.min((current / goal) * 100, 100)

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Revenue Goal</span>
                <Target size={18} style={{ opacity: 0.5 }} />
            </div>
            <div style={{ padding: '16px 0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 13 }}>
                    <span style={{ color: 'var(--text-muted)' }}>Progress</span>
                    <span>{progress.toFixed(0)}%</span>
                </div>
                <div style={{
                    height: 12,
                    background: 'rgba(255,255,255,0.1)',
                    borderRadius: 6,
                    overflow: 'hidden'
                }}>
                    <div style={{
                        height: '100%',
                        width: `${progress}%`,
                        background: 'linear-gradient(90deg, #6366f1, #10b981)',
                        borderRadius: 6,
                        transition: 'width 1s ease'
                    }} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12, fontSize: 14 }}>
                    <span style={{ fontWeight: 600 }}>{formatINR(current)}</span>
                    <span style={{ color: 'var(--text-muted)' }}>of {formatINR(goal)}</span>
                </div>
            </div>
        </div>
    )
}

// Trend Indicator Card
export function TrendCard({ title, value, change, trend, icon: Icon }) {
    const isPositive = trend === 'up'
    const color = isPositive ? '#10b981' : '#ef4444'

    return (
        <div className="card" style={{ padding: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{title}</span>
                {Icon && <Icon size={16} style={{ opacity: 0.5 }} />}
            </div>
            <div style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 8 }}>{value}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color }}>
                {trend === 'up' ? <TrendingUp size={14} /> : trend === 'down' ? <TrendingDown size={14} /> : <Minus size={14} />}
                <span>{change}</span>
            </div>
        </div>
    )
}

// Risk Alerts Widget
export function RiskAlerts({ alerts = [] }) {
    const defaultAlerts = alerts.length > 0 ? alerts : [
        { type: 'warning', message: 'Burn rate increased 12% this month', severity: 'medium' },
        { type: 'info', message: 'DSO improved by 5 days', severity: 'low' },
    ]

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Risk Alerts</span>
                <AlertTriangle size={18} style={{ color: '#f59e0b' }} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {defaultAlerts.map((alert, idx) => (
                    <div key={idx} style={{
                        padding: 12,
                        borderRadius: 8,
                        background: alert.severity === 'high' ? 'rgba(239, 68, 68, 0.1)' :
                            alert.severity === 'medium' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(99, 102, 241, 0.1)',
                        borderLeft: `3px solid ${alert.severity === 'high' ? '#ef4444' :
                            alert.severity === 'medium' ? '#f59e0b' : '#6366f1'}`,
                        fontSize: 13
                    }}>
                        {alert.message}
                    </div>
                ))}
            </div>
        </div>
    )
}

export default {
    CreditScoreGauge,
    BurnTrendChart,
    DSOChart,
    CashVelocityChart,
    RevenueGoalProgress,
    TrendCard,
    RiskAlerts
}
