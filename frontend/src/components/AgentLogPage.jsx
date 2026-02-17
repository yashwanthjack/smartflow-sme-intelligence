import React, { useState, useEffect } from 'react'
import { useAuth } from '../AuthContext'
import { Activity, Brain, CheckCircle, AlertTriangle, Info, Clock, Terminal, ArrowRight, Link2, Zap } from 'lucide-react'

const AGENT_COLORS = {
    'CollectionsBot': '#f59e0b',
    'PaymentsOptimizer': '#10b981',
    'GSTComplianceAgent': '#6366f1',
    'CashFlowGuard': '#3b82f6',
    'RiskSentinel': '#ef4444',
    'ForecastEngine': '#8b5cf6',
    'SupervisorAgent': '#ec4899',
}

export default function AgentLogPage() {
    const { user, token } = useAuth()
    const [logs, setLogs] = useState([])
    const [loading, setLoading] = useState(true)
    const [viewMode, setViewMode] = useState('conversations') // 'conversations' | 'timeline'

    const fetchLogs = async () => {
        if (!user || !token) return
        try {
            const res = await fetch(`/api/audit/${user.entity_id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                setLogs(await res.json())
            }
        } catch (e) {
            console.error("Failed to fetch logs", e)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchLogs()
        const interval = setInterval(fetchLogs, 5000)
        return () => clearInterval(interval)
    }, [user, token])

    const getSeverityColor = (sev) => {
        switch (sev) {
            case 'CRITICAL': return '#ef4444';
            case 'WARNING': return '#f59e0b';
            default: return '#10b981';
        }
    }

    const getIcon = (sev) => {
        switch (sev) {
            case 'CRITICAL': return <AlertTriangle size={16} />;
            case 'WARNING': return <AlertTriangle size={16} />;
            default: return <Info size={16} />;
        }
    }

    // Group logs by trace_id for conversation view
    const groupedLogs = React.useMemo(() => {
        const groups = {}
        const ungrouped = []

        logs.forEach(log => {
            const traceId = log.trace_id || (log.details && typeof log.details === 'object' ? log.details.trace : null)
            if (traceId) {
                if (!groups[traceId]) groups[traceId] = []
                groups[traceId].push(log)
            } else {
                ungrouped.push(log)
            }
        })

        // Sort each group by timestamp
        Object.values(groups).forEach(group =>
            group.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
        )

        // Create ordered list of conversations and solo logs
        const result = []
        const seenTraces = new Set()

        logs.forEach(log => {
            const traceId = log.trace_id || (log.details && typeof log.details === 'object' ? log.details.trace : null)
            if (traceId && !seenTraces.has(traceId)) {
                seenTraces.add(traceId)
                result.push({ type: 'conversation', traceId, logs: groups[traceId] })
            } else if (!traceId) {
                result.push({ type: 'solo', log })
            }
        })

        return result
    }, [logs])

    const renderConversation = (group) => {
        const agents = [...new Set(group.logs.map(l => l.agent))]
        const maxSeverity = group.logs.some(l => l.severity === 'CRITICAL') ? 'CRITICAL'
            : group.logs.some(l => l.severity === 'WARNING') ? 'WARNING' : 'INFO'

        return (
            <div key={group.traceId} style={{
                background: 'var(--bg-secondary)', borderRadius: 12,
                border: '1px solid var(--glass-border)',
                overflow: 'hidden', marginBottom: 4
            }}>
                {/* Conversation Header */}
                <div style={{
                    padding: '12px 20px',
                    background: 'rgba(99, 102, 241, 0.04)',
                    borderBottom: '1px solid var(--glass-border)',
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Link2 size={14} color="var(--accent-primary)" />
                        <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5, color: 'var(--accent-primary)' }}>
                            Multi-Agent Interaction
                        </span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                            {agents.map((agent, i) => (
                                <React.Fragment key={agent}>
                                    <span style={{
                                        fontSize: 10, padding: '2px 8px', borderRadius: 20,
                                        background: `${AGENT_COLORS[agent] || '#6b7280'}15`,
                                        color: AGENT_COLORS[agent] || '#6b7280',
                                        fontWeight: 600
                                    }}>{agent.replace('Agent', '')}</span>
                                    {i < agents.length - 1 && <ArrowRight size={10} color="var(--text-muted)" />}
                                </React.Fragment>
                            ))}
                        </div>
                    </div>
                    <span style={{
                        fontSize: 10, padding: '2px 8px', borderRadius: 20,
                        background: `${getSeverityColor(maxSeverity)}15`,
                        color: getSeverityColor(maxSeverity), fontWeight: 600
                    }}>{maxSeverity}</span>
                </div>

                {/* Conversation Messages */}
                <div style={{ padding: '8px 12px' }}>
                    {group.logs.map((log, idx) => (
                        <div key={log.id} style={{
                            display: 'flex', gap: 12, padding: '10px 8px',
                            borderBottom: idx < group.logs.length - 1 ? '1px solid rgba(255,255,255,0.03)' : 'none',
                            position: 'relative'
                        }}>
                            {/* Vertical connector line */}
                            {idx < group.logs.length - 1 && (
                                <div style={{
                                    position: 'absolute', left: 19, top: 36, bottom: -2,
                                    width: 2, background: 'var(--glass-border)'
                                }} />
                            )}

                            {/* Agent avatar */}
                            <div style={{
                                width: 28, height: 28, borderRadius: '50%',
                                background: `${AGENT_COLORS[log.agent] || '#6b7280'}20`,
                                border: `2px solid ${AGENT_COLORS[log.agent] || '#6b7280'}`,
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                flexShrink: 0, zIndex: 1,
                                fontSize: 10, fontWeight: 800,
                                color: AGENT_COLORS[log.agent] || '#6b7280'
                            }}>
                                {log.agent[0]}
                            </div>

                            <div style={{ flex: 1, minWidth: 0 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 3 }}>
                                    <span style={{
                                        fontSize: 12, fontWeight: 700,
                                        color: AGENT_COLORS[log.agent] || 'var(--text-primary)'
                                    }}>{log.agent}</span>
                                    <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                                        {new Date(log.timestamp).toLocaleTimeString()}
                                    </span>
                                </div>
                                <div style={{
                                    fontSize: 12, color: 'var(--text-primary)', lineHeight: 1.5,
                                    padding: '6px 10px', borderRadius: 8,
                                    background: 'rgba(255,255,255,0.02)'
                                }}>
                                    {log.summary}
                                </div>

                                {/* Show collaboration details */}
                                {log.details && typeof log.details === 'object' && (
                                    (log.details.triggered_by || log.details.requested_by || log.details.alerting || log.details.informed_by) && (
                                        <div style={{
                                            fontSize: 10, color: 'var(--text-muted)', marginTop: 4,
                                            display: 'flex', alignItems: 'center', gap: 4
                                        }}>
                                            <Zap size={10} />
                                            {log.details.triggered_by && `Triggered by ${log.details.triggered_by}`}
                                            {log.details.requested_by && `Requested by ${log.details.requested_by}`}
                                            {log.details.informed_by && `Informed by ${log.details.informed_by}`}
                                            {log.details.alerting && !log.details.triggered_by && `→ Alerting ${log.details.alerting}`}
                                        </div>
                                    )
                                )}

                                {log.details && (
                                    <details style={{ fontSize: 11, marginTop: 4 }}>
                                        <summary style={{ cursor: 'pointer', color: 'var(--text-muted)' }}>Data Traces</summary>
                                        <pre style={{
                                            background: '#0a0a0a', padding: 10, borderRadius: 6,
                                            overflowX: 'auto', color: '#10b981', fontSize: 10,
                                            border: '1px solid #1a1a2e', marginTop: 4
                                        }}>
                                            {typeof log.details === 'string' ? log.details : JSON.stringify(log.details, null, 2)}
                                        </pre>
                                    </details>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        )
    }

    const renderSoloLog = (log) => (
        <div key={log.id} style={{
            display: 'flex', gap: 16, padding: 14,
            background: 'var(--bg-secondary)', borderRadius: 12,
            borderLeft: `4px solid ${getSeverityColor(log.severity)}`
        }}>
            <div style={{
                width: 36, height: 36, borderRadius: 8,
                background: `${AGENT_COLORS[log.agent] || '#6b7280'}15`,
                border: `1px solid ${AGENT_COLORS[log.agent] || '#6b7280'}40`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: AGENT_COLORS[log.agent] || 'var(--text-muted)'
            }}>
                {getIcon(log.severity)}
            </div>
            <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <strong style={{ fontSize: 13, color: AGENT_COLORS[log.agent] || 'var(--text-primary)' }}>{log.agent}</strong>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                        {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-primary)', marginBottom: 6 }}>
                    {log.summary}
                </div>
                {log.details && (
                    <details style={{ fontSize: 11 }}>
                        <summary style={{ cursor: 'pointer', color: 'var(--text-muted)' }}>Data Traces</summary>
                        <pre style={{
                            background: '#0a0a0a', padding: 10, borderRadius: 6,
                            overflowX: 'auto', color: '#10b981', fontSize: 10, border: '1px solid #1a1a2e'
                        }}>
                            {typeof log.details === 'string' ? log.details : JSON.stringify(log.details, null, 2)}
                        </pre>
                    </details>
                )}
            </div>
        </div>
    )

    return (
        <div className="main-content">
            <header className="header">
                <div>
                    <h1 style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Brain size={24} /> Agent Workforce
                    </h1>
                    <p className="header-subtitle">Multi-agent orchestration — agents collaborate, analyze, and make autonomous decisions</p>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                    <button
                        className={`btn ${viewMode === 'conversations' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => setViewMode('conversations')}
                        style={{ fontSize: 12 }}
                    >
                        <Link2 size={14} style={{ marginRight: 4 }} /> Conversations
                    </button>
                    <button
                        className={`btn ${viewMode === 'timeline' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => setViewMode('timeline')}
                        style={{ fontSize: 12 }}
                    >
                        <Activity size={14} style={{ marginRight: 4 }} /> Timeline
                    </button>
                    <button className="btn btn-secondary" onClick={fetchLogs} style={{ fontSize: 12 }}>
                        <Clock size={14} style={{ marginRight: 4 }} /> Refresh
                    </button>
                </div>
            </header>

            {/* Agent Status Bar */}
            <div style={{
                display: 'flex', gap: 10, marginTop: 20, flexWrap: 'wrap'
            }}>
                {Object.entries(AGENT_COLORS).map(([agent, color]) => {
                    const count = logs.filter(l => l.agent === agent).length
                    return (
                        <div key={agent} style={{
                            padding: '6px 14px', borderRadius: 20,
                            background: count > 0 ? `${color}12` : 'var(--bg-secondary)',
                            border: `1px solid ${count > 0 ? `${color}40` : 'var(--glass-border)'}`,
                            fontSize: 11, fontWeight: 600,
                            color: count > 0 ? color : 'var(--text-muted)',
                            display: 'flex', alignItems: 'center', gap: 6
                        }}>
                            <div style={{
                                width: 6, height: 6, borderRadius: '50%',
                                background: count > 0 ? color : 'var(--text-muted)',
                                animation: count > 0 ? 'pulse 2s infinite' : 'none'
                            }} />
                            {agent.replace('Agent', '')}
                            {count > 0 && <span style={{ opacity: 0.6 }}>({count})</span>}
                        </div>
                    )
                })}
            </div>

            <div className="card" style={{ marginTop: 20, padding: 0, overflow: 'hidden' }}>
                <div className="card-header" style={{ padding: '14px 20px', borderBottom: '1px solid var(--glass-border)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <Terminal size={18} color="var(--text-primary)" />
                        <span className="card-title">
                            {viewMode === 'conversations' ? 'Agent Conversations' : 'Decision Governance Feed'}
                        </span>
                        <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 8 }}>
                            {logs.length} events · auto-refreshes every 5s
                        </span>
                    </div>
                </div>

                <div style={{ padding: '16px' }}>
                    {loading && logs.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
                            <Brain size={48} style={{ marginBottom: 16, opacity: 0.5 }} className="animate-pulse" />
                            <p>Connecting to Agent Workforce...</p>
                        </div>
                    ) : logs.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
                            <p>No active agent logs. Agents are monitoring in the background.</p>
                        </div>
                    ) : viewMode === 'conversations' ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                            {groupedLogs.map((item, idx) =>
                                item.type === 'conversation'
                                    ? renderConversation(item)
                                    : renderSoloLog(item.log)
                            )}
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                            {logs.map(log => renderSoloLog(log))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
