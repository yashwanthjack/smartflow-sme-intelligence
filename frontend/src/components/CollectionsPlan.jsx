import { useState, useEffect } from 'react'
import { useAuth } from '../AuthContext'
import { AlertTriangle, Phone, Mail, Clock, DollarSign, ChevronRight, Sparkles, X, Send, CheckCircle } from 'lucide-react'

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
    const [selectedInvoice, setSelectedInvoice] = useState(null)
    const [isDrafting, setIsDrafting] = useState(false)
    const [draftedText, setDraftedText] = useState('')
    const [emailSent, setEmailSent] = useState(false)

    const handleMagicDraft = (e, action) => {
        e.stopPropagation()
        setSelectedInvoice(action)
        setIsDrafting(true)
        setDraftedText('')
        setEmailSent(false)

        // Simulate AI generating a personalized email
        setTimeout(() => {
            setIsDrafting(false)
            setDraftedText(`Subject: Action Required: Overdue Payment for ${action.invoice_number || 'Invoice'}\n\nDear Client,\n\nWe hope this email finds you well.\n\nThis is a polite reminder that payment of ${formatINR(action.amount)} for invoice ${action.invoice_number || 'Invoice'} is currently ${action.days_overdue} days overdue (Due Date: ${action.due_date}).\n\nGiven your valued relationship with us, we wanted to personally reach out to ensure you received the invoice and avoid any late penalties. Please process the payment at your earliest convenience.\n\nLet us know if you need another copy of the invoice.\n\nBest regards,\nSmartFlow Collections AI`)
        }, 2500)
    }

    const handleSendEmail = () => {
        setEmailSent(true)
        setTimeout(() => {
            setSelectedInvoice(null)
            setEmailSent(false)
        }, 2000)
    }

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

                            <button
                                onClick={(e) => handleMagicDraft(e, action)}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 6,
                                    padding: '6px 12px',
                                    borderRadius: 6,
                                    background: 'linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%)',
                                    color: 'white',
                                    border: 'none',
                                    cursor: 'pointer',
                                    fontSize: 12,
                                    fontWeight: 500,
                                    marginLeft: 'auto',
                                    transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                                    boxShadow: '0 2px 10px rgba(217, 70, 239, 0.3)'
                                }}
                                onMouseOver={(e) => {
                                    e.currentTarget.style.transform = 'translateY(-1px)'
                                    e.currentTarget.style.boxShadow = '0 4px 15px rgba(217, 70, 239, 0.4)'
                                }}
                                onMouseOut={(e) => {
                                    e.currentTarget.style.transform = 'translateY(0)'
                                    e.currentTarget.style.boxShadow = '0 2px 10px rgba(217, 70, 239, 0.3)'
                                }}
                            >
                                <Sparkles size={14} /> Magic Draft
                            </button>
                        </div>
                    ))
                )}
            </div>

            {/* Magic Draft Modal */}
            {selectedInvoice && (
                <div style={{
                    position: 'fixed',
                    top: 0, left: 0, right: 0, bottom: 0,
                    background: 'rgba(0,0,0,0.6)',
                    backdropFilter: 'blur(4px)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000,
                    animation: 'fadeIn 0.2s ease-out'
                }}>
                    <div style={{
                        background: 'var(--card-bg)',
                        border: '1px solid var(--border-color)',
                        borderRadius: 16,
                        width: '100%',
                        maxWidth: 500,
                        padding: 24,
                        boxShadow: '0 20px 40px rgba(0,0,0,0.4)',
                        position: 'relative'
                    }}>
                        <button
                            onClick={() => setSelectedInvoice(null)}
                            style={{
                                position: 'absolute', top: 16, right: 16,
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--text-muted)',
                                cursor: 'pointer'
                            }}
                        >
                            <X size={20} />
                        </button>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
                            <div style={{
                                width: 40, height: 40, borderRadius: '50%',
                                background: 'linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%)',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                color: 'white'
                            }}>
                                <Sparkles size={20} />
                            </div>
                            <div>
                                <h3 style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>AI Magic Draft</h3>
                                <p style={{ margin: 0, fontSize: 12, color: 'var(--text-muted)' }}>
                                    Drafting for {selectedInvoice.invoice_number || 'Invoice'} • {formatINR(selectedInvoice.amount)}
                                </p>
                            </div>
                        </div>

                        {isDrafting ? (
                            <div style={{ padding: '40px 20px', textAlign: 'center' }}>
                                <div className="loading-spinner" style={{ margin: '0 auto 16px' }} />
                                <div style={{
                                    fontSize: 15,
                                    fontWeight: 500,
                                    background: 'linear-gradient(90deg, #8b5cf6, #d946ef, #8b5cf6)',
                                    backgroundSize: '200% auto',
                                    color: 'transparent',
                                    WebkitBackgroundClip: 'text',
                                    animation: 'gradientFlow 2s linear infinite'
                                }}>
                                    Analyzing payment history & drafting personalized email...
                                </div>
                                <style>{`
                                    @keyframes gradientFlow {
                                        0% { background-position: 0% center; }
                                        100% { background-position: 200% center; }
                                    }
                                    @keyframes fadeIn {
                                        from { opacity: 0; transform: translateY(10px); }
                                        to { opacity: 1; transform: translateY(0); }
                                    }
                                `}</style>
                            </div>
                        ) : emailSent ? (
                            <div style={{ padding: '40px 20px', textAlign: 'center', color: '#10b981', animation: 'fadeIn 0.3s ease-out' }}>
                                <CheckCircle size={48} style={{ margin: '0 auto 16px', display: 'block' }} />
                                <h3 style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>Email Sent Successfully!</h3>
                            </div>
                        ) : (
                            <div style={{ animation: 'fadeIn 0.3s ease-out' }}>
                                <div style={{
                                    background: 'rgba(255,255,255,0.03)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: 8,
                                    padding: 16,
                                    marginBottom: 20,
                                    position: 'relative'
                                }}>
                                    <textarea
                                        value={draftedText}
                                        onChange={(e) => setDraftedText(e.target.value)}
                                        style={{
                                            width: '100%',
                                            minHeight: 200,
                                            background: 'transparent',
                                            border: 'none',
                                            color: 'var(--text-color)',
                                            fontSize: 14,
                                            lineHeight: 1.6,
                                            outline: 'none',
                                            resize: 'vertical',
                                            fontFamily: 'inherit'
                                        }}
                                    />
                                </div>

                                <button
                                    onClick={handleSendEmail}
                                    style={{
                                        width: '100%',
                                        padding: 14,
                                        borderRadius: 8,
                                        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                                        color: 'white',
                                        border: 'none',
                                        cursor: 'pointer',
                                        fontSize: 15,
                                        fontWeight: 600,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        gap: 8,
                                        transition: 'transform 0.2s ease',
                                        boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)'
                                    }}
                                    onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-1px)'}
                                    onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                                >
                                    <Send size={18} /> Send Reminder
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
