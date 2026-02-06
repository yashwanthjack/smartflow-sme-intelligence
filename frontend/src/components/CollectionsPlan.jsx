import { useState, useEffect } from 'react'
import { useAuth } from '../AuthContext'
import { AlertTriangle, Phone, Mail, Clock, DollarSign, ChevronRight } from 'lucide-react'

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

const getUrgencyColor = (urgency) => {
    switch (urgency) {
        case 'critical': return '#ef4444'
        case 'high': return '#f59e0b'
        case 'medium': return '#3b82f6'
        case 'low': return '#10b981'
        default: return '#6366f1'
    }
}

const getUrgencyIcon = (urgency) => {
    switch (urgency) {
        case 'critical': return <AlertTriangle size={16} />
        case 'high': return <Phone size={16} />
        case 'medium': return <Mail size={16} />
        case 'low': return <Clock size={16} />
        default: return <DollarSign size={16} />
    }
}

export default function CollectionsPlan({ entityId }) {
    const { token } = useAuth()
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (!entityId || !token) return

        const fetchPlan = async () => {
            try {
                const res = await fetch(`${API_BASE}/data/entities/${entityId}/collections-plan`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
                if (res.ok) {
                    const json = await res.json()
                    setData(json)
                } else {
                    setError('Failed to load collections plan')
                }
            } catch (e) {
                setError('Connection error')
            }
            setLoading(false)
        }

        fetchPlan()
    }, [entityId, token])

    if (loading) {
        return (
            <div className="card" style={{ padding: 24, textAlign: 'center' }}>
                <div className="loading-spinner" />
                <p>Loading collections plan...</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className="card" style={{ padding: 24, textAlign: 'center', color: '#ef4444' }}>
                {error}
            </div>
        )
    }

    return (
        <div className="card" style={{ padding: 24 }}>
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <AlertTriangle size={20} color="#f59e0b" />
                Collections Plan
            </h2>

            {/* Summary Stats */}
            {data?.summary && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
                    <div style={{ padding: 12, background: 'rgba(239, 68, 68, 0.1)', borderRadius: 8 }}>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Total Overdue</div>
                        <div style={{ fontSize: 18, fontWeight: 'bold', color: '#ef4444' }}>
                            {formatINR(data.summary.total_overdue_amount)}
                        </div>
                    </div>
                    <div style={{ padding: 12, background: 'rgba(245, 158, 11, 0.1)', borderRadius: 8 }}>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Invoices</div>
                        <div style={{ fontSize: 18, fontWeight: 'bold' }}>
                            {data.summary.overdue_invoice_count}
                        </div>
                    </div>
                    <div style={{ padding: 12, background: 'rgba(99, 102, 241, 0.1)', borderRadius: 8 }}>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Avg Days Overdue</div>
                        <div style={{ fontSize: 18, fontWeight: 'bold' }}>
                            {data.summary.average_days_overdue}
                        </div>
                    </div>
                    <div style={{ padding: 12, background: 'rgba(239, 68, 68, 0.1)', borderRadius: 8 }}>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Critical</div>
                        <div style={{ fontSize: 18, fontWeight: 'bold', color: '#ef4444' }}>
                            {data.summary.critical_count}
                        </div>
                    </div>
                </div>
            )}

            {/* Action List */}
            <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                {data?.actions?.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: 32, color: '#10b981' }}>
                        ✅ No overdue invoices! All collections are current.
                    </div>
                ) : (
                    data?.actions?.map((action, idx) => (
                        <div
                            key={action.invoice_id || idx}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 12,
                                padding: 12,
                                borderBottom: '1px solid rgba(255,255,255,0.1)',
                                cursor: 'pointer'
                            }}
                        >
                            <div style={{
                                width: 32,
                                height: 32,
                                borderRadius: '50%',
                                background: `${getUrgencyColor(action.urgency)}20`,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: getUrgencyColor(action.urgency)
                            }}>
                                {getUrgencyIcon(action.urgency)}
                            </div>
                            <div style={{ flex: 1 }}>
                                <div style={{ fontWeight: 500, fontSize: 14 }}>
                                    {action.invoice_number || `Invoice ${idx + 1}`}
                                </div>
                                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                                    {action.days_overdue} days overdue • Due: {action.due_date}
                                </div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontWeight: 600, color: getUrgencyColor(action.urgency) }}>
                                    {formatINR(action.amount)}
                                </div>
                                <div style={{ fontSize: 11, color: 'var(--text-muted)', maxWidth: 150 }}>
                                    {action.recommended_action}
                                </div>
                            </div>
                            <ChevronRight size={16} color="var(--text-muted)" />
                        </div>
                    ))
                )}
            </div>
        </div>
    )
}
