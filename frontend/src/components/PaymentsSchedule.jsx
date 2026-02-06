import { useState, useEffect } from 'react'
import { useAuth } from '../AuthContext'
import { Calendar, DollarSign, Clock, CheckCircle, AlertCircle, ChevronRight } from 'lucide-react'

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

const getPriorityColor = (priority) => {
    switch (priority) {
        case 'critical': return '#ef4444'
        case 'high': return '#f59e0b'
        case 'medium': return '#3b82f6'
        default: return '#10b981'
    }
}

const getStatusIcon = (status) => {
    switch (status) {
        case 'approved': return <CheckCircle size={16} color="#10b981" />
        case 'delayed': return <AlertCircle size={16} color="#f59e0b" />
        case 'scheduled': return <Clock size={16} color="#3b82f6" />
        default: return <Clock size={16} />
    }
}

export default function PaymentsSchedule({ entityId }) {
    const { token } = useAuth()
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (!entityId || !token) return

        const fetchSchedule = async () => {
            try {
                const res = await fetch(`${API_BASE}/data/entities/${entityId}/payments-schedule`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
                if (res.ok) {
                    const json = await res.json()
                    setData(json)
                } else {
                    setError('Failed to load payments schedule')
                }
            } catch (e) {
                setError('Connection error')
            }
            setLoading(false)
        }

        fetchSchedule()
    }, [entityId, token])

    if (loading) {
        return (
            <div className="card" style={{ padding: 24, textAlign: 'center' }}>
                <div className="loading-spinner" />
                <p>Loading payments schedule...</p>
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
                <Calendar size={20} color="#6366f1" />
                Payments Schedule (30 Days)
            </h2>

            {/* Summary Stats */}
            {data?.summary && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
                    <div style={{ padding: 12, background: 'rgba(99, 102, 241, 0.1)', borderRadius: 8 }}>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Total Payables</div>
                        <div style={{ fontSize: 18, fontWeight: 'bold' }}>
                            {formatINR(data.summary.total_payables_30_days)}
                        </div>
                    </div>
                    <div style={{ padding: 12, background: 'rgba(16, 185, 129, 0.1)', borderRadius: 8 }}>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Cash Balance</div>
                        <div style={{ fontSize: 18, fontWeight: 'bold', color: '#10b981' }}>
                            {formatINR(data.current_cash_balance)}
                        </div>
                    </div>
                    <div style={{ padding: 12, background: 'rgba(239, 68, 68, 0.1)', borderRadius: 8 }}>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Critical</div>
                        <div style={{ fontSize: 18, fontWeight: 'bold', color: '#ef4444' }}>
                            {data.summary.critical_payments}
                        </div>
                    </div>
                    <div style={{ padding: 12, background: 'rgba(245, 158, 11, 0.1)', borderRadius: 8 }}>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Delayed</div>
                        <div style={{ fontSize: 18, fontWeight: 'bold', color: '#f59e0b' }}>
                            {data.summary.delayed_payments}
                        </div>
                    </div>
                </div>
            )}

            {/* Schedule List */}
            <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                {data?.schedule?.map((payment, idx) => (
                    <div
                        key={payment.invoice_id || payment.payment_id || idx}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 12,
                            padding: 12,
                            borderBottom: '1px solid rgba(255,255,255,0.1)'
                        }}
                    >
                        <div style={{
                            width: 32,
                            height: 32,
                            borderRadius: '50%',
                            background: `${getPriorityColor(payment.priority)}20`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: getPriorityColor(payment.priority)
                        }}>
                            <DollarSign size={16} />
                        </div>
                        <div style={{ flex: 1 }}>
                            <div style={{ fontWeight: 500, fontSize: 14 }}>
                                {payment.vendor || payment.invoice_number || `Payment ${idx + 1}`}
                            </div>
                            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                                Due: {payment.due_date} → Scheduled: {payment.scheduled_date}
                            </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <div style={{ fontWeight: 600 }}>
                                {formatINR(payment.amount)}
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11 }}>
                                {getStatusIcon(payment.status)}
                                <span style={{ color: payment.status === 'delayed' ? '#f59e0b' : '#10b981' }}>
                                    {payment.status}
                                </span>
                            </div>
                        </div>
                        <ChevronRight size={16} color="var(--text-muted)" />
                    </div>
                ))}
            </div>
        </div>
    )
}
