import { useState } from 'react'
import { Landmark, AlertTriangle, TrendingUp, Clock, ArrowRight, Zap, Shield, BarChart3 } from 'lucide-react'

const cashGap = { detected: true, amount: 485000, daysUntil: 18, confidence: 87 }

const loanProducts = [
    { id: 1, lender: 'HDFC Bank', product: 'Invoice Discounting', amount: '₹5L - ₹25L', rate: '10.5%', tenure: '30-90 days', disbursal: '24 hrs', eligible: true, bestRate: true, status: null },
    { id: 2, lender: 'Bajaj Finance', product: 'Working Capital', amount: '₹2L - ₹50L', rate: '12.0%', tenure: '6-24 months', disbursal: '48 hrs', eligible: true, bestRate: false, status: null },
    { id: 3, lender: 'Lendingkart', product: 'Overdraft Facility', amount: '₹1L - ₹10L', rate: '14.5%', tenure: 'Revolving', disbursal: '4 hrs', eligible: true, bestRate: false, status: null },
    { id: 4, lender: 'KredX', product: 'Supply Chain Finance', amount: '₹10L - ₹1Cr', rate: '11.2%', tenure: '60-180 days', disbursal: '72 hrs', eligible: false, bestRate: false, status: null }
]

const flowMetrics = [
    { label: 'Cash Velocity', value: '₹12.4L/mo', trend: '+8%', good: true },
    { label: 'GST Fidelity', value: '92%', trend: '+3%', good: true },
    { label: 'DSO (Days)', value: '38 days', trend: '-5', good: true },
    { label: 'Debt Service Ratio', value: '1.8x', trend: '+0.2', good: true },
]

export default function CreditMarketplace() {
    const [products, setProducts] = useState(loanProducts)

    const applyForLoan = (id) => {
        setProducts(prev => prev.map(p => p.id === id ? { ...p, status: 'applied' } : p))
        setTimeout(() => {
            setProducts(prev => prev.map(p => p.id === id ? { ...p, status: 'under_review' } : p))
        }, 2000)
    }

    return (
        <div style={{ padding: '0 8px' }}>
            <div style={{ marginBottom: 24 }}>
                <h2 style={{ fontSize: 22, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                    <Landmark size={22} color="#10b981" /> OCEN Credit Marketplace
                </h2>
                <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                    Flow-based lending via OCEN. AI-predicted cash gaps trigger just-in-time credit offers.
                </p>
            </div>

            {cashGap.detected && (
                <div className="card" style={{
                    padding: '18px 22px', marginBottom: 22,
                    background: 'linear-gradient(135deg, rgba(239,68,68,0.06), rgba(245,158,11,0.08))',
                    border: '1px solid rgba(239,68,68,0.15)'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                                <AlertTriangle size={18} color="#ef4444" />
                                <span style={{ fontSize: 15, fontWeight: 700, color: '#ef4444' }}>Cash Gap Predicted</span>
                                <span style={{ padding: '2px 8px', borderRadius: 10, fontSize: 10, fontWeight: 600, background: 'rgba(239,68,68,0.1)', color: '#ef4444' }}>
                                    {cashGap.confidence}% confidence
                                </span>
                            </div>
                            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                                AI forecasts a <strong>₹{(cashGap.amount / 1000).toFixed(0)}K shortfall</strong> in <strong>{cashGap.daysUntil} days</strong>.
                            </p>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: 28, fontWeight: 800, color: '#ef4444' }}>₹{(cashGap.amount / 100000).toFixed(1)}L</div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Estimated Shortfall</div>
                        </div>
                    </div>
                </div>
            )}

            <div style={{ marginBottom: 24 }}>
                <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <BarChart3 size={16} color="var(--accent-primary)" /> Flow-Based Underwriting Signals
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
                    {flowMetrics.map((m, i) => (
                        <div key={i} className="card" style={{ padding: 16 }}>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>{m.label}</div>
                            <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                                <span style={{ fontSize: 20, fontWeight: 800 }}>{m.value}</span>
                                <span style={{ fontSize: 11, fontWeight: 600, color: m.good ? '#10b981' : '#ef4444' }}>
                                    <TrendingUp size={10} style={{ verticalAlign: -1, marginRight: 2 }} />{m.trend}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Zap size={16} color="#f59e0b" /> Available Credit Products
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}>
                {products.map(p => (
                    <div key={p.id} className="card" style={{
                        padding: 22, position: 'relative',
                        opacity: p.eligible ? 1 : 0.55,
                        border: p.bestRate ? '2px solid rgba(16,185,129,0.4)' : undefined
                    }}>
                        {p.bestRate && (
                            <span style={{ position: 'absolute', top: -8, right: 16, padding: '3px 10px', borderRadius: 10, fontSize: 10, fontWeight: 700, background: '#10b981', color: 'white' }}>Best Rate</span>
                        )}
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 14 }}>
                            <div>
                                <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 2 }}>{p.product}</div>
                                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{p.lender}</div>
                            </div>
                            <Landmark size={18} color={p.eligible ? '#10b981' : '#6b7280'} />
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10, marginBottom: 16 }}>
                            <div><div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Amount</div><div style={{ fontSize: 13, fontWeight: 600 }}>{p.amount}</div></div>
                            <div><div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Rate</div><div style={{ fontSize: 13, fontWeight: 700, color: p.bestRate ? '#10b981' : 'inherit' }}>{p.rate} p.a.</div></div>
                            <div><div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Tenure</div><div style={{ fontSize: 13, fontWeight: 600 }}>{p.tenure}</div></div>
                            <div><div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Disbursal</div><div style={{ fontSize: 13, fontWeight: 600 }}>{p.disbursal}</div></div>
                        </div>
                        {p.status === 'applied' && <div style={{ padding: '10px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600, background: 'rgba(99,102,241,0.08)', color: 'var(--accent-primary)', display: 'flex', alignItems: 'center', gap: 6 }}><Clock size={14} /> Application Submitted</div>}
                        {p.status === 'under_review' && <div style={{ padding: '10px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600, background: 'rgba(245,158,11,0.08)', color: '#f59e0b', display: 'flex', alignItems: 'center', gap: 6 }}><Shield size={14} /> Under Review</div>}
                        {!p.status && p.eligible && <button onClick={() => applyForLoan(p.id)} className="btn btn-primary" style={{ width: '100%', fontSize: 13, padding: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>Apply via OCEN <ArrowRight size={14} /></button>}
                        {!p.eligible && <div style={{ padding: '10px 14px', borderRadius: 8, fontSize: 12, background: 'var(--bg-muted)', color: 'var(--text-muted)', textAlign: 'center' }}>Not eligible — Requires ₹10L+ monthly volume</div>}
                    </div>
                ))}
            </div>
        </div>
    )
}
