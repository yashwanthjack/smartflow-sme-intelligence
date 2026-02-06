import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../AuthContext'
import { Sparkles, Send, ArrowUpRight, ArrowDownRight, MoreHorizontal, TrendingUp, Users, RefreshCw, Calendar, DollarSign, Zap } from 'lucide-react'
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
            {change && (
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
        { label: 'Initiated', value: 65200 },
        { label: 'Authorized', value: 54800 },
        { label: 'Successful', value: 48600 },
        { label: 'Payouts', value: 38300 },
        { label: 'Completed', value: 32900 },
    ]

    const chartData = data || defaultData
    const maxValue = Math.max(...chartData.map(d => d.value))

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
                            style={{ height: `${(item.value / maxValue) * 150}px` }}
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
                <span><strong>{formatCompact(chartData[2]?.value)}</strong> transactions</span>
                <span>Conversion: <strong>89%</strong></span>
                <span>Drop-off: <strong style={{ color: 'var(--danger)' }}>-11%</strong></span>
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
                <span style={{
                    padding: '4px 12px',
                    background: 'var(--text-primary)',
                    color: 'white',
                    borderRadius: 'var(--radius-full)',
                    fontSize: 12
                }}>
                    Highest: <strong>{highestDay || 'Thu'}</strong>
                </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div className="metric-value">{formatCompact(total || 1284)}</div>
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
                    <div style={{ fontWeight: 600, color: 'var(--success)' }}>+{change || 320}</div>
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
                            height: `${(item.value / maxValue) * 100}px`,
                            background: item.highlight ? 'var(--text-primary)' : 'var(--bg-muted)',
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
                <div className="metric-value" style={{ fontSize: 36 }}>+{changePercent || 20}%</div>
                <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                    This week's income is higher than last week's
                </p>
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
