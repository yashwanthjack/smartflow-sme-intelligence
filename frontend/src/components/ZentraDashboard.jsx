import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../AuthContext'
import { Sparkles, Send, ArrowUpRight, ArrowDownRight, MoreHorizontal, TrendingUp, Users, RefreshCw, Calendar, DollarSign, Zap, Plus, Trash2, X } from 'lucide-react'
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const API_BASE = '/api'

// Format number in Indian style
const formatINR = (amount) => {
    if (amount === null || amount === undefined) return '₹0'
    const absAmount = Math.abs(amount)
    if (absAmount >= 10000000) {
        return `₹${(amount / 10000000).toFixed(1)}Cr`
    } else if (absAmount >= 100000) {
        return `₹${(amount / 100000).toFixed(1)}L`
    } else if (absAmount >= 1000) {
        return `₹${(amount / 1000).toFixed(1)}K`
    }
    return `₹${amount.toFixed(0)}`
}

const formatCompact = (num) => {
    if (num === null || num === undefined) return '0'
    if (num >= 1000) return `${(num / 1000).toFixed(1)}k`
    return num.toString()
}

// ============================================
// METRIC CARD - Large Number Display
// ============================================
export function MetricCard({ title, value, change, changeType = 'positive', icon: Icon, prefix = '₹' }) {
    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">{title}</span>
                <button className="card-menu-btn">
                    <MoreHorizontal size={16} />
                </button>
            </div>
            <div className="metric-value">
                {prefix}{typeof value === 'number' ? formatCompact(value) : value}
            </div>
            {!!change && (
                <span className={`metric-change ${changeType}`}>
                    {changeType === 'positive' ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                    {change}%
                </span>
            )}
        </div>
    )
}

// ============================================
// GROSS VOLUME CARD - With Progress Bars
// ============================================
export function GrossVolumeCard({ totalVolume, change, breakdown }) {
    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Gross Volume</span>
                <button className="card-menu-btn">
                    <MoreHorizontal size={16} />
                </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 20 }}>
                <div className="metric-value-lg">₹{formatCompact(totalVolume)}</div>
                {change && (
                    <span className="metric-change positive">
                        <ArrowUpRight size={14} />
                        {change}%
                    </span>
                )}
            </div>

            {/* Progress Bars */}
            {breakdown?.map((item, idx) => (
                <div key={idx} className="progress-bar-container">
                    <div className="progress-bar-label">
                        <span>{item.label}</span>
                        <span>₹{formatCompact(item.value)}</span>
                    </div>
                    <div className="progress-bar">
                        <div
                            className={`progress-bar-fill ${item.color || 'green'}`}
                            style={{ width: `${totalVolume > 0 ? (item.value / totalVolume) * 100 : 0}%` }}
                        />
                    </div>
                </div>
            ))}
        </div>
    )
}

// ============================================
// PAYMENTS WATERFALL CHART
// ============================================
export function PaymentsWaterfallChart({ data }) {
    const defaultData = [
        { label: 'Initiated', value: 0 },
        { label: 'Authorized', value: 0 },
        { label: 'Successful', value: 0 },
        { label: 'Payouts', value: 0 },
        { label: 'Completed', value: 0 },
    ]

    const chartData = data || defaultData
    const maxValue = Math.max(...chartData.map(d => d.value))

    const initiated = chartData[0]?.value || 0
    const successful = chartData[2]?.value || 0

    const conversion = initiated > 0 ? Math.round((successful / initiated) * 100) : 0
    const dropOff = initiated > 0 ? -(100 - conversion) : 0

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Payments</span>
                <button className="card-menu-btn">
                    <MoreHorizontal size={16} />
                </button>
            </div>

            <div className="waterfall-chart">
                {chartData.map((item, idx) => (
                    <div key={idx} className="waterfall-bar">
                        <div className="waterfall-bar-value">{formatCompact(item.value)}</div>
                        <div
                            className={`waterfall-bar-fill ${idx === 2 ? 'pattern' : 'solid'}`}
                            style={{ height: `${maxValue > 0 ? (item.value / maxValue) * 150 : 0}px` }}
                        />
                        <div className="waterfall-bar-label">{item.label}</div>
                    </div>
                ))}
            </div>

            <div style={{
                display: 'flex',
                justifyContent: 'center',
                gap: 16,
                marginTop: 16,
                fontSize: 12,
                color: 'var(--text-muted)'
            }}>
                <span><strong>{formatCompact(successful)}</strong> transactions</span>
                <span>Conversion: <strong>{conversion}%</strong></span>
                <span>Drop-off: <strong style={{ color: dropOff < 0 ? 'var(--danger)' : 'var(--text-muted)' }}>{dropOff}%</strong></span>
            </div>
        </div>
    )
}

// ============================================
// TRANSACTIONS DOT GRID
// ============================================
export function TransactionsDotGrid({ total, change, peakDay }) {
    // Generate 7x6 dot grid
    const dots = Array(42).fill(0).map((_, i) => ({
        filled: Math.random() > 0.3,
        highlight: i === 20 // Wednesday position
    }))

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Transactions</span>
                <button className="card-menu-btn">
                    <MoreHorizontal size={16} />
                </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16 }}>
                <span style={{
                    padding: '4px 12px',
                    background: 'var(--bg-muted)',
                    borderRadius: 'var(--radius-full)',
                    fontSize: 12
                }}>
                    Peak: <strong>{peakDay || 'Wed'}</strong>
                </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div className="metric-value">{formatCompact(total || 106000)}</div>
                <div className="dot-grid">
                    {dots.map((dot, i) => (
                        <div
                            key={i}
                            className={`dot-cell ${dot.filled ? 'filled' : ''} ${dot.highlight ? 'highlight' : ''}`}
                        />
                    ))}
                </div>
                <div style={{ textAlign: 'right', fontSize: 13 }}>
                    <div style={{ color: 'var(--text-muted)' }}>vs last period</div>
                    <div style={{ fontWeight: 600, color: 'var(--success)' }}>+{change || 34002}</div>
                </div>
            </div>
        </div>
    )
}

// ============================================
// RETENTION CHART - Pink Line
// ============================================
export function RetentionChart({ data }) {
    const sampleData = [
        { month: 'Jan', value: 45 },
        { month: 'Feb', value: 52 },
        { month: 'Mar', value: 48 },
        { month: 'Apr', value: 42 },
        { month: 'May', value: 55 },
        { month: 'Jun', value: 50 },
    ]

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Retention</span>
                <button className="card-menu-btn">
                    <MoreHorizontal size={16} />
                </button>
            </div>

            <div style={{ position: 'relative' }}>
                <span style={{
                    position: 'absolute',
                    top: 20,
                    left: '50%',
                    padding: '4px 12px',
                    background: 'white',
                    border: '1px solid var(--glass-border)',
                    borderRadius: 'var(--radius-full)',
                    fontSize: 12,
                    fontWeight: 600,
                    boxShadow: 'var(--shadow-sm)',
                    zIndex: 10
                }}>
                    42%
                </span>
                <ResponsiveContainer width="100%" height={180}>
                    <AreaChart data={data || sampleData}>
                        <defs>
                            <linearGradient id="retentionGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#ec4899" stopOpacity={0.3} />
                                <stop offset="100%" stopColor="#ec4899" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <XAxis
                            dataKey="month"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fontSize: 11, fill: '#8a8a8a' }}
                        />
                        <Area
                            type="stepAfter"
                            dataKey="value"
                            stroke="#ec4899"
                            strokeWidth={2}
                            fill="url(#retentionGradient)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}

// ============================================
// INSIGHT CARD - Gradient Background
// ============================================
export function InsightCard({ percentage, title, description }) {
    return (
        <div className="insight-card">
            <div className="insight-badge">
                <Zap size={14} />
                Insights
            </div>
            <div className="insight-value">{percentage || 75}%</div>
            <div className="insight-title">{title || 'Authorization rate increased by 4% compared to last week.'}</div>
            <div className="insight-description">
                {description || 'This improvement reduced failed transactions by 950 and is projected to recover ₹12,400.'}
            </div>
        </div>
    )
}

// ============================================
// AI PROMPT BAR
// ============================================
export function AIPromptBar({ onSubmit }) {
    const [query, setQuery] = useState('')

    const handleSubmit = (e) => {
        e.preventDefault()
        if (query.trim() && onSubmit) {
            onSubmit(query)
            setQuery('')
        }
    }

    return (
        <form className="ai-prompt-bar" onSubmit={handleSubmit}>
            <div className="ai-prompt-icon">
                <Sparkles size={16} />
            </div>
            <div className="ai-prompt-text">
                <span>What would you like to explore next?</span>
            </div>
            <input
                type="text"
                className="ai-prompt-input"
                placeholder="I want to know what caused the drop-off from authorized to..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
            />
            <span className="ai-prompt-tag">/cash flow</span>
            <button type="submit" className="btn btn-icon btn-ghost">
                <Send size={18} />
            </button>
        </form>
    )
}

// ============================================
// CUSTOMERS CARD
// ============================================
export function CustomersCard({ total, change, highestDay }) {
    const dots = Array(35).fill(0).map((_, i) => ({
        filled: Math.random() > 0.4,
        highlight: i === 18
    }))

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Customers</span>
                <button className="card-menu-btn">
                    <MoreHorizontal size={16} />
                </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16 }}>
                {(total > 0 && highestDay) && (
                    <span style={{
                        padding: '4px 12px',
                        background: 'var(--text-primary)',
                        color: 'white',
                        borderRadius: 'var(--radius-full)',
                        fontSize: 12
                    }}>
                        Highest: <strong>{highestDay}</strong>
                    </span>
                )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div className="metric-value">{formatCompact(total ?? 0)}</div>
                <div className="dot-grid" style={{ '--dot-color': '#3b82f6' }}>
                    {dots.map((dot, i) => (
                        <div
                            key={i}
                            className={`dot-cell`}
                            style={{
                                background: dot.highlight ? '#1a1a1a' : dot.filled ? '#3b82f6' : 'var(--bg-muted)'
                            }}
                        />
                    ))}
                </div>
                <div style={{ textAlign: 'right', fontSize: 13 }}>
                    <div style={{ color: 'var(--text-muted)' }}>vs last period</div>
                    <div style={{ fontWeight: 600, color: 'var(--success)' }}>+{change ?? 0}</div>
                </div>
            </div>
        </div>
    )
}

// ============================================
// INCOME TRACKER CARD
// ============================================
export function IncomeTrackerCard({ weeklyData, changePercent }) {
    const defaultData = [
        { day: 'S', value: 1200 },
        { day: 'M', value: 1800 },
        { day: 'T', value: 2200 },
        { day: 'W', value: 1400 },
        { day: 'T', value: 2567, highlight: true },
        { day: 'F', value: 1900 },
        { day: 'S', value: 1600 },
    ]

    const data = weeklyData || defaultData
    const maxValue = Math.max(...data.map(d => d.value))

    return (
        <div className="card">
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16 }}>
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                        <div style={{
                            width: 32,
                            height: 32,
                            background: 'var(--bg-muted)',
                            borderRadius: 'var(--radius-md)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}>
                            <DollarSign size={16} />
                        </div>
                        <span className="card-title">Income Tracker</span>
                    </div>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 280 }}>
                        Track changes in income over time and access detailed data on each project and payments received
                    </p>
                </div>
                <select style={{
                    padding: '6px 12px',
                    borderRadius: 'var(--radius-full)',
                    border: '1px solid var(--glass-border)',
                    fontSize: 12,
                    background: 'white'
                }}>
                    <option>Week</option>
                    <option>Month</option>
                </select>
            </div>

            {/* Bar Chart */}
            <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', height: 150, marginBottom: 16 }}>
                {data.map((item, idx) => (
                    <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                        {item.highlight && (
                            <span style={{
                                padding: '4px 8px',
                                background: 'var(--text-primary)',
                                color: 'white',
                                borderRadius: 'var(--radius-full)',
                                fontSize: 11,
                                marginBottom: 8
                            }}>
                                ₹{formatCompact(item.value)}
                            </span>
                        )}
                        <div style={{
                            width: 8,
                            height: `${Math.max((item.value / (maxValue || 1)) * 100, 8)}px`,
                            background: item.highlight ? 'var(--text-primary)' : '#e5e7eb',
                            borderRadius: 4
                        }} />
                    </div>
                ))}
            </div>

            {/* Day labels */}
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                {data.map((item, idx) => (
                    <div
                        key={idx}
                        style={{
                            width: 32,
                            height: 32,
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: 12,
                            background: item.highlight ? 'var(--text-primary)' : 'transparent',
                            color: item.highlight ? 'white' : 'var(--text-muted)'
                        }}
                    >
                        {item.day}
                    </div>
                ))}
            </div>

            {/* Change indicator */}
            <div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid var(--glass-border)' }}>
                <div className="metric-value" style={{ fontSize: 36, color: (changePercent || 0) >= 0 ? 'var(--text-primary)' : 'var(--danger)' }}>
                    {(changePercent || 0) > 0 ? '+' : ''}{changePercent || 0}%
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                    {(changePercent || 0) > 0
                        ? "This week's income is higher than last week's"
                        : (changePercent || 0) < 0
                            ? "This week's income is lower than last week's"
                            : "No change in income compared to last week"
                    }
                </p>
            </div>
        </div>
    )
}

// ============================================
// TRANSACTIONS TABLE
// ============================================
export function TransactionsTable({ entityId }) {
    const { token } = useAuth()
    const [entries, setEntries] = useState([])
    const [loading, setLoading] = useState(true)
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [page, setPage] = useState(1)
    const [total, setTotal] = useState(0)
    const limit = 50

    const fetchEntries = useCallback(() => {
        if (!entityId || !token) return
        const offset = (page - 1) * limit
        fetch(`${API_BASE}/data/entities/${entityId}/ledger?limit=${limit}&offset=${offset}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        })
            .then(res => res.json())
            .then(data => {
                const items = Array.isArray(data) ? data : (data.items || [])
                setEntries(items)
                if (data.total !== undefined) setTotal(data.total)
                setLoading(false)
            })
            .catch(console.error)
    }, [entityId, token, page])

    useEffect(() => {
        fetchEntries()
    }, [fetchEntries])

    const handleDelete = async (id) => {
        if (!confirm('Are you sure you want to delete this transaction?')) return;
        try {
            const res = await fetch(`${API_BASE}/data/entities/${entityId}/ledger/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) fetchEntries()
            else alert('Failed to delete')
        } catch (e) { console.error(e) }
    }

    if (loading) return <div className="card" style={{ padding: 20 }}>Loading transactions...</div>

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Recent Transactions</span>
                <div style={{ display: 'flex', gap: 8 }}>
                    <button className="btn btn-secondary" onClick={() => setIsModalOpen(true)} style={{ fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Plus size={14} /> Add Transaction
                    </button>
                    <button className="card-menu-btn">
                        <MoreHorizontal size={16} />
                    </button>
                </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--glass-border)', textAlign: 'left', color: 'var(--text-muted)' }}>
                            <th style={{ padding: 12 }}>Date</th>
                            <th style={{ padding: 12 }}>Description</th>
                            <th style={{ padding: 12 }}>Category</th>
                            <th style={{ padding: 12 }}>Source</th>
                            <th style={{ padding: 12, textAlign: 'right' }}>Amount</th>
                            <th style={{ padding: 12, width: 40 }}></th>
                        </tr>
                    </thead>
                    <tbody>
                        {entries.map(e => (
                            <tr key={e.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                <td style={{ padding: 12 }}>{e.date}</td>
                                <td style={{ padding: 12 }}>{e.description}</td>
                                <td style={{ padding: 12 }}>
                                    <span style={{ padding: '2px 8px', borderRadius: 12, background: 'rgba(255,255,255,0.05)', fontSize: 11 }}>
                                        {e.category}
                                    </span>
                                </td>
                                <td style={{ padding: 12, opacity: 0.7 }}>{e.source_type}</td>
                                <td style={{ padding: 12, textAlign: 'right', color: e.amount > 0 ? 'var(--success)' : 'var(--text-primary)' }}>
                                    {formatINR(e.amount)}
                                </td>
                                <td style={{ padding: 12 }}>
                                    {e.source_type === 'manual' && (
                                        <button onClick={() => handleDelete(e.id)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }} title="Delete">
                                            <Trash2 size={14} />
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div style={{ padding: '16px 24px', borderTop: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Showing {entries.length > 0 ? (page - 1) * limit + 1 : 0} to {Math.min(page * limit, total)} of {total} entries
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                    <button
                        className="btn btn-secondary"
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        style={{ fontSize: 12, padding: '4px 12px' }}
                    >
                        Previous
                    </button>
                    <button
                        className="btn btn-secondary"
                        onClick={() => setPage(p => p + 1)}
                        disabled={page * limit >= total}
                        style={{ fontSize: 12, padding: '4px 12px' }}
                    >
                        Next
                    </button>
                </div>
            </div>

            <AddTransactionModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                entityId={entityId}
                onSuccess={fetchEntries}
            />
        </div>
    )
}

// ============================================
// ADD TRANSACTION MODAL
// ============================================
export function AddTransactionModal({ isOpen, onClose, entityId, onSuccess }) {
    const { token } = useAuth()
    const [formData, setFormData] = useState({
        date: new Date().toISOString().split('T')[0],
        description: '',
        amount: '',
        type: 'income',
        category: 'Sales'
    })
    const [loading, setLoading] = useState(false)

    if (!isOpen) return null

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE}/data/entities/${entityId}/ledger/manual`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            })
            if (res.ok) {
                onSuccess()
                onClose()
                setFormData({
                    date: new Date().toISOString().split('T')[0],
                    description: '',
                    amount: '',
                    type: 'income',
                    category: 'Sales'
                })
            } else {
                alert('Failed to add transaction')
            }
        } catch (error) {
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000, backdropFilter: 'blur(5px)'
        }}>
            <div className="card" style={{ width: 400, padding: 24, background: 'var(--bg-card)', border: '1px solid var(--glass-border)' }}>
                <div className="card-header">
                    <span className="card-title">Add Manual Transaction</span>
                    <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div>
                        <label style={{ fontSize: 13, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Type</label>
                        <div style={{ display: 'flex', gap: 12 }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                <input type="radio" name="type" checked={formData.type === 'income'} onChange={() => setFormData({ ...formData, type: 'income' })} />
                                Income
                            </label>
                            <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                <input type="radio" name="type" checked={formData.type === 'expense'} onChange={() => setFormData({ ...formData, type: 'expense' })} />
                                Expense
                            </label>
                        </div>
                    </div>

                    <div>
                        <label style={{ fontSize: 13, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Date</label>
                        <input
                            type="date" className="input" required
                            value={formData.date}
                            onChange={e => setFormData({ ...formData, date: e.target.value })}
                            style={{ width: '100%', padding: '8px 12px', background: 'var(--bg-secondary)', border: '1px solid var(--glass-border)', borderRadius: 8, color: 'white' }}
                        />
                    </div>

                    <div>
                        <label style={{ fontSize: 13, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Description</label>
                        <input
                            type="text" className="input" placeholder="e.g. Cash Sale" required
                            value={formData.description}
                            onChange={e => setFormData({ ...formData, description: e.target.value })}
                            style={{ width: '100%', padding: '8px 12px', background: 'var(--bg-secondary)', border: '1px solid var(--glass-border)', borderRadius: 8, color: 'white' }}
                        />
                    </div>

                    <div>
                        <label style={{ fontSize: 13, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Category</label>
                        <input
                            type="text" className="input" placeholder="e.g. Sales, Rent, Utilities" required
                            value={formData.category}
                            onChange={e => setFormData({ ...formData, category: e.target.value })}
                            style={{ width: '100%', padding: '8px 12px', background: 'var(--bg-secondary)', border: '1px solid var(--glass-border)', borderRadius: 8, color: 'white' }}
                        />
                    </div>

                    <div>
                        <label style={{ fontSize: 13, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Amount</label>
                        <input
                            type="number" className="input" placeholder="0.00" required min="0" step="0.01"
                            value={formData.amount}
                            onChange={e => setFormData({ ...formData, amount: e.target.value })}
                            style={{ width: '100%', padding: '8px 12px', background: 'var(--bg-secondary)', border: '1px solid var(--glass-border)', borderRadius: 8, color: 'white' }}
                        />
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 12 }}>
                        <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
                        <button type="submit" className="btn btn-primary" disabled={loading}>
                            {loading ? 'Adding...' : 'Add Transaction'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default function ZentraDashboard() {
    return (
        <div>
            <h2 style={{ fontSize: 24, fontWeight: 600, marginBottom: 24 }}>Zentra Dashboard Components</h2>
            <p style={{ color: 'var(--text-muted)' }}>These components are available for use in the main dashboard.</p>
        </div>
    )
}
