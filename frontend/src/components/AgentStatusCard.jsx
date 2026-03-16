import React from 'react'
import { Bot, User, Brain, Shield, CreditCard, Receipt } from 'lucide-react'

export default function AgentStatusCard() {
    const agents = [
        { name: 'Collections AI', role: 'Revenue Recovery', status: 'Active', action: 'Following up on 3 overdue invoices', icon: Receipt, color: 'var(--accent-orange)' },
        { name: 'Sentinel', role: 'GST Compliance', status: 'Idle', action: 'GSTR-2A reconciliation complete', icon: Shield, color: 'var(--success)' },
        { name: 'Payment Guard', role: 'Reconciliation', status: 'Processing', action: 'Matching transaction #TX992...', icon: CreditCard, color: 'var(--accent-indigo)' },
        { name: 'Fractional CFO', role: 'Strategy', status: 'Active', action: 'Analyzing burn rate trends', icon: Brain, color: 'var(--accent-purple)' },
    ]

    return (
        <div className="card">
            <div className="card-header" style={{ marginBottom: '16px' }}>
                <span className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Bot size={18} style={{ color: 'var(--text-primary)' }} />
                    AI Workforce
                </span>
                <span style={{ fontSize: '11px', color: 'var(--success)', background: 'var(--bg-muted)', padding: '2px 8px', borderRadius: '12px' }}>
                    4 Agents Online
                </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {agents.map((agent, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px', borderRadius: '8px', background: 'var(--bg-muted)', border: '1px solid transparent' }}>
                        <div style={{
                            width: '32px', height: '32px', borderRadius: '8px',
                            background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
                            boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                        }}>
                            <agent.icon size={16} style={{ color: agent.color }} />
                        </div>
                        <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                                <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)' }}>{agent.name}</span>
                                <span style={{ fontSize: '10px', fontWeight: '500', color: agent.status === 'Active' || agent.status === 'Processing' ? 'var(--success)' : 'var(--text-muted)' }}>
                                    {agent.status}
                                </span>
                            </div>
                            <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>
                                {agent.action}
                            </span>
                        </div>
                    </div>
                ))}
            </div>

            <button style={{
                width: '100%', marginTop: '16px', padding: '8px',
                background: 'transparent', border: '1px dashed var(--glass-border)', borderRadius: '6px',
                color: 'var(--text-secondary)', fontSize: '12px', cursor: 'pointer',
                transition: 'all 0.2s'
            }}>
                View Agent Logs →
            </button>
        </div>
    )
}
