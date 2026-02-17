import React, { useState, useEffect } from 'react'
import { Activity, CheckCircle, AlertCircle, Clock, ShieldCheck, User, Bot } from 'lucide-react'
import { format } from 'date-fns'

export default function ActivityFeed({ entityId }) {
    const [logs, setLogs] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (entityId) fetchLogs()
    }, [entityId])

    const fetchLogs = async () => {
        try {
            const token = localStorage.getItem('token')
            // Use relative path to leverage Vite proxy and ensure consistency
            const res = await fetch(`/api/audit/${entityId}?limit=10`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            })
            if (res.ok) {
                const data = await res.json()
                setLogs(data)
            }
        } catch (e) {
            console.error("Failed to fetch audit logs", e)
        } finally {
            setLoading(false)
        }
    }

    if (loading) return <div className="card" style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading activity...</div>

    return (
        <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div className="card-header">
                <span className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Activity size={18} style={{ color: 'var(--accent-orange)' }} />
                    Live Activity Feed
                </span>
                <span style={{
                    fontSize: '11px', padding: '2px 8px', borderRadius: '12px',
                    background: 'var(--bg-muted)', color: 'var(--text-secondary)',
                    border: '1px solid var(--glass-border)'
                }}>
                    Real-time
                </span>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', paddingRight: '8px' }}>
                {logs.length === 0 ? (
                    <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '32px 0', fontSize: '13px' }}>
                        No activity recorded yet.
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {logs.map((log) => (
                            <div key={log.id} style={{ display: 'flex', gap: '12px', position: 'relative' }}>
                                {/* Icon */}
                                <div style={{
                                    width: '24px', height: '24px', borderRadius: '50%', flexShrink: 0,
                                    background: log.severity === 'ERROR' ? 'var(--danger)' :
                                        log.severity === 'WARNING' ? 'var(--warning)' : 'var(--info)',
                                    color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    marginTop: '2px', zIndex: 1
                                }}>
                                    {log.agent.includes('Agent') ? <Bot size={14} /> : <User size={14} />}
                                </div>

                                {/* Content */}
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4px' }}>
                                        <span style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-primary)' }}>
                                            {log.agent}
                                        </span>
                                        <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                            <Clock size={10} />
                                            {format(new Date(log.timestamp), 'MMM d, HH:mm')}
                                        </span>
                                    </div>
                                    <div style={{ fontSize: '13px', fontWeight: '500', color: 'var(--text-secondary)', marginBottom: '2px' }}>
                                        {log.action.replace(/_/g, ' ')}
                                    </div>
                                    <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                                        {log.summary}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'flex-end', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
                <ShieldCheck size={12} />
                Audited & Secured
            </div>
        </div>
    )
}
