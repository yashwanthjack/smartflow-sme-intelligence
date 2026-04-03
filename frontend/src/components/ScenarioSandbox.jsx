import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuth } from '../AuthContext'
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, ReferenceLine, Area, ComposedChart, Legend
} from 'recharts'
import {
    Users, TrendingUp, DollarSign, Briefcase, AlertTriangle,
    CheckCircle, XCircle, Zap, ArrowRight
} from 'lucide-react'

const API_BASE = '/api'

const formatINR = (amount) => {
    if (amount === null || amount === undefined) return '₹0'
    const absAmount = Math.abs(amount)
    if (absAmount >= 10000000) return `₹${(amount / 10000000).toFixed(2)}Cr`
    if (absAmount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`
    if (absAmount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`
    return `₹${amount.toFixed(0)}`
}

function LiveSlider({ label, icon: Icon, value, onChange, min, max, step = 1, suffix = '', color = '#6366f1', formatValue }) {
    return (
        <div style={{ padding: 14, background: 'rgba(255,255,255,0.02)', borderRadius: 12, border: '1px solid var(--glass-border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--text-secondary)' }}>
                    <Icon size={15} color={color} /> {label}
                </label>
                <span style={{ fontSize: 16, fontWeight: 700, color }}>{formatValue ? formatValue(value) : value}{suffix}</span>
            </div>
            <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={value}
                onChange={e => onChange(parseFloat(e.target.value))}
                style={{
                    width: '100%', height: 6, appearance: 'none', borderRadius: 3,
                    background: `linear-gradient(to right, ${color} 0%, ${color} ${((value - min) / (max - min)) * 100}%, rgba(255,255,255,0.1) ${((value - min) / (max - min)) * 100}%, rgba(255,255,255,0.1) 100%)`,
                    cursor: 'pointer', outline: 'none'
                }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                <span>{formatValue ? formatValue(min) : min}{suffix}</span>
                <span>{formatValue ? formatValue(max) : max}{suffix}</span>
            </div>
        </div>
    )
}

function RiskBadge({ status, riskLevel }) {
    const config = {
        SAFE:  { gradient: 'linear-gradient(135deg, #10b981, #059669)', icon: CheckCircle },
        WARN:  { gradient: 'linear-gradient(135deg, #f59e0b, #d97706)', icon: AlertTriangle },
        BLOCK: { gradient: 'linear-gradient(135deg, #ef4444, #dc2626)', icon: XCircle },
    }
    const c = config[status] || config.SAFE
    const Icon = c.icon
    return (
        <div style={{
            display: 'flex', alignItems: 'center', gap: 10, padding: '12px 20px',
            borderRadius: 14, background: c.gradient, color: '#fff',
            fontWeight: 700, fontSize: 14, boxShadow: '0 4px 16px rgba(0,0,0,0.2)'
        }}>
            <Icon size={20} /> {status} — {riskLevel} Risk
        </div>
    )
}

export default function ScenarioSandbox({ entityId }) {
    const { token } = useAuth()
    const debounceRef = useRef(null)

    // Slider state
    const [hiringCount, setHiringCount] = useState(0)
    const [salary, setSalary] = useState(80000)
    const [marketingPct, setMarketingPct] = useState(0)
    const [revenuePct, setRevenuePct] = useState(0)
    const [oneTime, setOneTime] = useState(0)
    const [loanAmount, setLoanAmount] = useState(0)

    // Result state
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)

    const fetchLive = useCallback(async () => {
        if (!entityId || !token) return
        setLoading(true)
        try {
            const params = new URLSearchParams({
                hiring_count: hiringCount,
                salary, marketing_pct: marketingPct,
                revenue_pct: revenuePct, one_time: oneTime,
                loan_amount: loanAmount,
            })
            const res = await fetch(`${API_BASE}/simulate/live?${params}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setResult(data)
            }
        } catch (e) { console.error(e) }
        setLoading(false)
    }, [entityId, token, hiringCount, salary, marketingPct, revenuePct, oneTime, loanAmount])

    // Debounced live fetch — fires 200ms after last slider change
    useEffect(() => {
        if (debounceRef.current) clearTimeout(debounceRef.current)
        debounceRef.current = setTimeout(fetchLive, 200)
        return () => clearTimeout(debounceRef.current)
    }, [fetchLive])

    return (
        <div style={{ padding: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
                <div style={{
                    width: 44, height: 44, borderRadius: 12,
                    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                    <Zap size={24} color="#fff" />
                </div>
                <div>
                    <h2 style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>Scenario Sandbox</h2>
                    <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                        Drag sliders to see instant impact on your financial runway
                    </span>
                </div>
                {result && <div style={{ marginLeft: 'auto' }}><RiskBadge status={result.status} riskLevel={result.risk_level} /></div>}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 24 }}>
                {/* Slider Controls */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    <LiveSlider
                        label="New Hires" icon={Users} value={hiringCount} onChange={setHiringCount}
                        min={0} max={10} color="#6366f1"
                    />
                    <LiveSlider
                        label="Salary / Hire" icon={Briefcase} value={salary} onChange={setSalary}
                        min={30000} max={200000} step={5000} color="#8b5cf6"
                        formatValue={v => formatINR(v)}
                    />
                    <LiveSlider
                        label="Marketing Increase" icon={TrendingUp} value={marketingPct} onChange={setMarketingPct}
                        min={0} max={100} suffix="%" color="#ec4899"
                    />
                    <LiveSlider
                        label="Revenue Growth" icon={DollarSign} value={revenuePct} onChange={setRevenuePct}
                        min={0} max={50} suffix="%" color="#10b981"
                    />
                    <LiveSlider
                        label="One-time Expense" icon={AlertTriangle} value={oneTime} onChange={setOneTime}
                        min={0} max={5000000} step={50000} color="#f59e0b"
                        formatValue={v => formatINR(v)}
                    />
                    <LiveSlider
                        label="Loan Injection" icon={DollarSign} value={loanAmount} onChange={setLoanAmount}
                        min={0} max={5000000} step={50000} color="#14b8a6"
                        formatValue={v => formatINR(v)}
                    />

                    {/* Hiring cost summary */}
                    {hiringCount > 0 && (
                        <div style={{
                            padding: 12, borderRadius: 10,
                            background: 'rgba(99,102,241,0.08)',
                            border: '1px solid rgba(99,102,241,0.2)',
                            fontSize: 12, color: 'var(--text-secondary)'
                        }}>
                            💼 {hiringCount} hire{hiringCount > 1 ? 's' : ''} × {formatINR(salary)}/mo = <strong style={{ color: '#6366f1' }}>{formatINR(hiringCount * salary)}/mo</strong> added burn
                        </div>
                    )}
                </div>

                {/* Chart + Metrics */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    {/* Key Metrics Row */}
                    {result && (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
                            <div className="card" style={{ padding: 16, textAlign: 'center' }}>
                                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Runway</div>
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                                    <span style={{ fontSize: 22, fontWeight: 700 }}>{result.current_runway}</span>
                                    <ArrowRight size={14} color="var(--text-muted)" />
                                    <span style={{
                                        fontSize: 22, fontWeight: 700,
                                        color: result.new_runway < result.current_runway ? '#ef4444' :
                                               result.new_runway > result.current_runway ? '#10b981' : 'var(--text-primary)'
                                    }}>{result.new_runway}</span>
                                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>mo</span>
                                </div>
                            </div>
                            <div className="card" style={{ padding: 16, textAlign: 'center' }}>
                                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Monthly Burn</div>
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                                    <span style={{ fontSize: 16, fontWeight: 600 }}>{formatINR(result.current_burn)}</span>
                                    <ArrowRight size={14} color="var(--text-muted)" />
                                    <span style={{ fontSize: 16, fontWeight: 700, color: '#ef4444' }}>{formatINR(result.new_burn)}</span>
                                </div>
                            </div>
                            <div className="card" style={{ padding: 16, textAlign: 'center' }}>
                                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Cash Now</div>
                                <div style={{ fontSize: 18, fontWeight: 700 }}>{formatINR(result.cash_balance)}</div>
                            </div>
                            <div className="card" style={{ padding: 16, textAlign: 'center' }}>
                                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Adjusted Cash</div>
                                <div style={{ fontSize: 18, fontWeight: 700, color: '#14b8a6' }}>{formatINR(result.adjusted_cash)}</div>
                            </div>
                        </div>
                    )}

                    {/* Chart */}
                    <div className="card" style={{ padding: 20 }}>
                        <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>
                            12-Month Cash Projection
                            {loading && <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 8 }}>updating…</span>}
                        </div>
                        <div style={{ height: 320 }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart data={result?.projection || []}>
                                    <defs>
                                        <linearGradient id="baseGrad" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="scenGrad" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                                    <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={11} />
                                    <YAxis stroke="var(--text-muted)" fontSize={11} tickFormatter={v => formatINR(v)} />
                                    <Tooltip
                                        contentStyle={{ background: 'var(--bg-card)', borderColor: 'var(--glass-border)', borderRadius: 8, fontSize: 12 }}
                                        formatter={v => formatINR(v)}
                                    />
                                    <Legend wrapperStyle={{ fontSize: 11 }} />
                                    <ReferenceLine y={500000} stroke="#f59e0b" strokeDasharray="5 5" label={{ value: "Safety", fill: "#f59e0b", fontSize: 10 }} />
                                    <Area type="monotone" dataKey="baseline" stroke="#6366f1" fill="url(#baseGrad)" strokeWidth={2} name="Current Path" dot={false} />
                                    <Line type="monotone" dataKey="scenario" stroke="#10b981" strokeWidth={3} name="With Changes" dot={false} strokeDasharray="0" />
                                </ComposedChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* AI Recommendation */}
                    {result?.recommendation && (
                        <div style={{
                            padding: 16, borderRadius: 12,
                            background: 'rgba(99,102,241,0.06)',
                            borderLeft: '4px solid #6366f1'
                        }}>
                            <div style={{ fontSize: 11, fontWeight: 600, color: '#6366f1', marginBottom: 6 }}>AI RECOMMENDATION</div>
                            <div style={{ fontSize: 13, lineHeight: 1.6 }}>{result.recommendation}</div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
