import { useState } from 'react'
import { Shield, Users, AlertTriangle, TrendingUp, TrendingDown, Building2, CheckCircle, ArrowRight } from 'lucide-react'

const networkScore = { composite: 78, status: 'Good', maxRisk: 'Moderate' }

const anchors = [
    { name: 'Tata Motors Ltd', type: 'Customer (Anchor)', revenue: '38%', health: 92, rating: 'A+', risk: 'Low', paymentDays: 28, relationship: '4.5 yrs', trend: 'stable' },
    { name: 'Mahindra Auto Parts', type: 'Customer', revenue: '22%', health: 78, rating: 'A', risk: 'Low', paymentDays: 35, relationship: '3 yrs', trend: 'improving' },
    { name: 'Bharat Steel Works', type: 'Supplier', revenue: '18%', health: 65, rating: 'B+', risk: 'Moderate', paymentDays: 45, relationship: '2 yrs', trend: 'stable' },
    { name: 'LogiFreight Services', type: 'Supplier', revenue: '12%', health: 55, rating: 'B', risk: 'Moderate', paymentDays: 52, relationship: '1.5 yrs', trend: 'declining' },
    { name: 'RawMat Suppliers', type: 'Supplier', revenue: '10%', health: 42, rating: 'B-', risk: 'High', paymentDays: 68, relationship: '8 months', trend: 'declining' }
]

const concentrationRisk = {
    topCustomer: 38,
    top3: 72,
    herfindahl: 0.24,
    verdict: 'Moderate concentration — consider diversifying customer base'
}

const riskColor = (risk) => risk === 'Low' ? '#10b981' : risk === 'Moderate' ? '#f59e0b' : '#ef4444'
const trendIcon = (trend) => trend === 'improving' ? <TrendingUp size={12} color="#10b981" /> : trend === 'declining' ? <TrendingDown size={12} color="#ef4444" /> : <ArrowRight size={12} color="#6b7280" />

const HealthBar = ({ value }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ flex: 1, height: 6, background: 'var(--glass-border)', borderRadius: 99 }}>
            <div style={{
                width: `${value}%`, height: '100%', borderRadius: 99,
                background: value > 75 ? '#10b981' : value > 50 ? '#f59e0b' : '#ef4444',
                transition: 'width 0.5s ease'
            }} />
        </div>
        <span style={{ fontSize: 12, fontWeight: 700, minWidth: 30 }}>{value}</span>
    </div>
)

export default function SupplyChainScore() {
    const [partners, setPartners] = useState([
        { id: 1, name: 'Tata Motors Ltd', type: 'Customer (Anchor)', revenue: '38%', health: 92, rating: 'A+', risk: 'Low', paymentDays: 28, relationship: '4.5 yrs', trend: 'stable' },
        { id: 2, name: 'Mahindra Auto Parts', type: 'Customer', revenue: '22%', health: 78, rating: 'A', risk: 'Low', paymentDays: 35, relationship: '3 yrs', trend: 'improving' },
        { id: 3, name: 'Bharat Steel Works', type: 'Supplier', revenue: '18%', health: 65, rating: 'B+', risk: 'Moderate', paymentDays: 45, relationship: '2 yrs', trend: 'stable' },
        { id: 4, name: 'LogiFreight Services', type: 'Supplier', revenue: '12%', health: 55, rating: 'B', risk: 'Moderate', paymentDays: 52, relationship: '1.5 yrs', trend: 'declining' },
        { id: 5, name: 'RawMat Suppliers', type: 'Supplier', revenue: '10%', health: 42, rating: 'B-', risk: 'High', paymentDays: 68, relationship: '8 months', trend: 'declining' }
    ])
    const [selectedPartner, setSelectedPartner] = useState(null)
    const [showAddForm, setShowAddForm] = useState(false)
    const [newPartner, setNewPartner] = useState({ name: '', type: 'Supplier', revenue: '', health: 75 })

    const handleAdd = () => {
        if (!newPartner.name) return
        setPartners([...partners, {
            id: Date.now(),
            ...newPartner,
            rating: newPartner.health > 80 ? 'A' : newPartner.health > 60 ? 'B' : 'C',
            risk: newPartner.health > 80 ? 'Low' : newPartner.health > 60 ? 'Moderate' : 'High',
            paymentDays: 30, // Default
            relationship: 'New',
            trend: 'stable'
        }])
        setShowAddForm(false)
        setNewPartner({ name: '', type: 'Supplier', revenue: '', health: 75 })
    }

    const handleRemove = (id, e) => {
        e.stopPropagation()
        setPartners(partners.filter(p => p.id !== id))
        if (selectedPartner === id) setSelectedPartner(null)
    }

    // Dynamic Score Calculation based on partners
    const avgHealth = Math.round(partners.reduce((acc, p) => acc + p.health, 0) / (partners.length || 1))
    const networkScore = { composite: avgHealth, status: avgHealth > 75 ? 'Good' : 'Average', maxRisk: partners.some(p => p.risk === 'High') ? 'High' : 'Moderate' }

    return (
        <div style={{ padding: '0 8px' }}>
            <div style={{ marginBottom: 24 }}>
                <h2 style={{ fontSize: 22, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                    <Shield size={22} color="#8b5cf6" /> Supply Chain Network Score
                </h2>
                <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                    Holistic credit assessment using supply chain health, anchor relationships, and concentration risk
                </p>
            </div>

            {/* Composite Score */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 16, marginBottom: 24 }}>
                <div className="card" style={{ padding: 28, textAlign: 'center' }}>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 }}>Supply Chain Credit Score</div>
                    <div style={{
                        width: 100, height: 100, borderRadius: '50%', margin: '0 auto 12px',
                        background: `conic-gradient(#8b5cf6 ${networkScore.composite * 3.6}deg, var(--glass-border) 0)`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>
                        <div style={{ width: 78, height: 78, borderRadius: '50%', background: 'var(--bg-card)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <span style={{ fontSize: 28, fontWeight: 800 }}>{networkScore.composite}</span>
                        </div>
                    </div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: '#8b5cf6' }}>{networkScore.status}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Max Risk: {networkScore.maxRisk}</div>
                </div>

                <div className="card" style={{ padding: 22 }}>
                    <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Users size={16} color="var(--accent-primary)" /> Concentration Analysis
                    </h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 16 }}>
                        <div style={{ padding: 12, background: 'var(--bg-muted)', borderRadius: 10 }}>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Top Customer</div>
                            <div style={{ fontSize: 20, fontWeight: 800, color: concentrationRisk.topCustomer > 30 ? '#f59e0b' : '#10b981' }}>{concentrationRisk.topCustomer}%</div>
                        </div>
                        <div style={{ padding: 12, background: 'var(--bg-muted)', borderRadius: 10 }}>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Top 3 Combined</div>
                            <div style={{ fontSize: 20, fontWeight: 800, color: concentrationRisk.top3 > 60 ? '#ef4444' : '#10b981' }}>{concentrationRisk.top3}%</div>
                        </div>
                        <div style={{ padding: 12, background: 'var(--bg-muted)', borderRadius: 10 }}>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Herfindahl Index</div>
                            <div style={{ fontSize: 20, fontWeight: 800 }}>{concentrationRisk.herfindahl}</div>
                        </div>
                    </div>
                    <div style={{ padding: 12, borderRadius: 8, background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.15)', fontSize: 12, color: '#f59e0b' }}>
                        <AlertTriangle size={12} style={{ marginRight: 4, verticalAlign: -1 }} />
                        {concentrationRisk.verdict}
                    </div>
                </div>
            </div>

            {/* Partners Table */}
            <div className="card" style={{ overflow: 'hidden' }}>
                <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ fontSize: 14, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Building2 size={16} /> Network Partners
                    </h3>
                    <button onClick={() => setShowAddForm(!showAddForm)} style={{
                        background: 'var(--accent-primary)', color: 'white', border: 'none', borderRadius: 6,
                        padding: '6px 12px', fontSize: 12, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4
                    }}>
                        {showAddForm ? 'Cancel' : '+ Add Partner'}
                    </button>
                </div>

                {showAddForm && (
                    <div style={{ padding: 16, background: 'var(--bg-muted)', borderBottom: '1px solid var(--glass-border)', display: 'flex', gap: 10, alignItems: 'end' }}>
                        <div style={{ flex: 2 }}>
                            <div style={{ fontSize: 11, marginBottom: 4 }}>Name</div>
                            <input value={newPartner.name} onChange={e => setNewPartner({ ...newPartner, name: e.target.value })} style={{ width: '100%', padding: 6, borderRadius: 4, border: '1px solid var(--glass-border)', background: 'var(--bg-card)', color: 'white' }} placeholder="Partner Name" />
                        </div>
                        <div style={{ flex: 1 }}>
                            <div style={{ fontSize: 11, marginBottom: 4 }}>Type</div>
                            <select value={newPartner.type} onChange={e => setNewPartner({ ...newPartner, type: e.target.value })} style={{ width: '100%', padding: 6, borderRadius: 4, border: '1px solid var(--glass-border)', background: 'var(--bg-card)', color: 'white' }}>
                                <option>Supplier</option>
                                <option>Customer</option>
                            </select>
                        </div>
                        <div style={{ flex: 1 }}>
                            <div style={{ fontSize: 11, marginBottom: 4 }}>Revenue %</div>
                            <input value={newPartner.revenue} onChange={e => setNewPartner({ ...newPartner, revenue: e.target.value })} style={{ width: '100%', padding: 6, borderRadius: 4, border: '1px solid var(--glass-border)', background: 'var(--bg-card)', color: 'white' }} placeholder="e.g. 15%" />
                        </div>
                        <div style={{ flex: 1 }}>
                            <div style={{ fontSize: 11, marginBottom: 4 }}>Health (0-100)</div>
                            <input type="number" value={newPartner.health} onChange={e => setNewPartner({ ...newPartner, health: parseInt(e.target.value) })} style={{ width: '100%', padding: 6, borderRadius: 4, border: '1px solid var(--glass-border)', background: 'var(--bg-card)', color: 'white' }} />
                        </div>
                        <button onClick={handleAdd} style={{ padding: '6px 16px', borderRadius: 4, background: '#10b981', color: 'white', border: 'none', height: 32, cursor: 'pointer', fontWeight: 600 }}>Save</button>
                    </div>
                )}

                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                    <thead>
                        <tr style={{ borderBottom: '2px solid var(--glass-border)' }}>
                            {['Partner', 'Type', 'Revenue %', 'Health', 'Rating', 'Risk', 'Avg Pmt Days', 'Trend', 'Action'].map(h => (
                                <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {partners.map((a) => (
                            <tr key={a.id} style={{ borderBottom: '1px solid var(--glass-border)', cursor: 'pointer', transition: 'background 0.15s' }}
                                onClick={() => setSelectedPartner(selectedPartner === a.id ? null : a.id)}
                                onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-muted)'}
                                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                            >
                                <td style={{ padding: '12px 14px', fontWeight: 600 }}>{a.name}</td>
                                <td style={{ padding: '12px 14px' }}>
                                    <span style={{
                                        padding: '2px 8px', borderRadius: 8, fontSize: 10, fontWeight: 600,
                                        background: a.type.includes('Anchor') ? 'rgba(99,102,241,0.1)' : 'var(--bg-muted)',
                                        color: a.type.includes('Anchor') ? 'var(--accent-primary)' : 'var(--text-muted)'
                                    }}>{a.type}</span>
                                </td>
                                <td style={{ padding: '12px 14px', fontWeight: 700 }}>{a.revenue}</td>
                                <td style={{ padding: '12px 14px', width: 120 }}><HealthBar value={a.health} /></td>
                                <td style={{ padding: '12px 14px' }}>
                                    <span style={{ padding: '2px 10px', borderRadius: 8, fontSize: 11, fontWeight: 700, background: 'rgba(139,92,246,0.08)', color: '#8b5cf6' }}>{a.rating}</span>
                                </td>
                                <td style={{ padding: '12px 14px' }}>
                                    <span style={{ fontSize: 12, fontWeight: 600, color: riskColor(a.risk) }}>{a.risk}</span>
                                </td>
                                <td style={{ padding: '12px 14px', fontWeight: 600 }}>{a.paymentDays}d</td>
                                <td style={{ padding: '12px 14px' }}>{trendIcon(a.trend)}</td>
                                <td style={{ padding: '12px 14px' }}>
                                    <button onClick={(e) => handleRemove(a.id, e)} style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', opacity: 0.7 }} title="Remove Partner">
                                        ×
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {selectedPartner !== null && (
                    <div style={{ padding: 18, background: 'var(--bg-muted)', borderTop: '1px solid var(--glass-border)', fontSize: 13 }}>
                        <strong>{partners.find(p => p.id === selectedPartner)?.name}</strong> — Relationship: {partners.find(p => p.id === selectedPartner)?.relationship}
                        {(() => {
                            const p = partners.find(p => p.id === selectedPartner)
                            if (!p) return null
                            if (p.risk === 'High') {
                                return (
                                    <div style={{ marginTop: 8, padding: 10, borderRadius: 8, background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.15)' }}>
                                        <div style={{ fontSize: 12, color: '#ef4444', fontWeight: 600, marginBottom: 6 }}>
                                            <AlertTriangle size={12} style={{ verticalAlign: -2, marginRight: 4 }} />
                                            High Risk — Consider reducing exposure
                                        </div>
                                        <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                                            <strong>Why:</strong> Health score is <span style={{ color: '#ef4444', fontWeight: 700 }}>{p.health}/100</span> (below 50 threshold)
                                            · Average payment cycle is <span style={{ color: '#ef4444', fontWeight: 700 }}>{p.paymentDays} days</span> (industry avg: 30-45 days)
                                            · Payment trend is <span style={{ color: '#ef4444', fontWeight: 700 }}>{p.trend}</span>
                                            · Rating: {p.rating}
                                        </div>
                                    </div>
                                )
                            }
                            if (p.risk === 'Moderate') {
                                return (
                                    <div style={{ marginTop: 8, padding: 10, borderRadius: 8, background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.15)' }}>
                                        <div style={{ fontSize: 12, color: '#f59e0b', fontWeight: 600, marginBottom: 6 }}>
                                            <AlertTriangle size={12} style={{ verticalAlign: -2, marginRight: 4 }} />
                                            Moderate Risk — Monitor closely
                                        </div>
                                        <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                                            <strong>Why:</strong> Health score is <span style={{ fontWeight: 700 }}>{p.health}/100</span>
                                            · Avg payment days: <span style={{ fontWeight: 700 }}>{p.paymentDays}d</span>
                                            · Trend: {p.trend}
                                        </div>
                                    </div>
                                )
                            }
                            return null
                        })()}
                        {partners.find(p => p.id === selectedPartner)?.type.includes('Anchor') && (
                            <span style={{ marginLeft: 12, fontSize: 12, color: '#10b981' }}>
                                <CheckCircle size={12} style={{ verticalAlign: -2, marginRight: 4 }} />
                                Anchor enterprise — eligible for supply chain financing discount
                            </span>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}
