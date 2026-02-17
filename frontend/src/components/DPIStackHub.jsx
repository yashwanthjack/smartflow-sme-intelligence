import { useState } from 'react'
import { Shield, Database, FileCheck, CreditCard, Building2, RefreshCw, CheckCircle, AlertCircle, Clock, Zap, ArrowRight, Link2, Wifi, WifiOff } from 'lucide-react'

const dpiSystems = [
    {
        id: 'aa',
        name: 'Account Aggregator',
        description: 'Consent-based financial data access from banks and financial institutions',
        icon: Database,
        color: '#6366f1',
        status: 'connected',
        lastSync: '2 min ago',
        details: {
            linkedAccounts: [
                { bank: 'HDFC Bank', type: 'Current Account', masked: '****4521', status: 'active' },
                { bank: 'ICICI Bank', type: 'Savings Account', masked: '****8833', status: 'active' },
                { bank: 'SBI', type: 'Current Account', masked: '****1290', status: 'pending' },
            ],
            consentStatus: 'Active',
            consentExpiry: '2026-08-15',
            dataPoints: 1247,
            lastFetch: '2026-02-13T09:30:00'
        }
    },
    {
        id: 'ocen',
        name: 'OCEN 4.0',
        description: 'Open Credit Enablement Network — flow-based lending protocols',
        icon: CreditCard,
        color: '#10b981',
        status: 'connected',
        lastSync: '15 min ago',
        details: {
            registeredLenders: ['HDFC Bank', 'Bajaj Finance', 'Lendingkart', 'KredX'],
            activeLoanProducts: 3,
            protocolVersion: '4.0',
            creditLine: '₹25L',
            utilizationPct: 32
        }
    },
    {
        id: 'gstn',
        name: 'GSTN Integration',
        description: 'Automated GST filing status, reconciliation, and ITC tracking',
        icon: FileCheck,
        color: '#f59e0b',
        status: 'connected',
        lastSync: '1 hr ago',
        details: {
            gstin: '29AABCT1332L1ZH',
            filingStatus: { 'GSTR-1': 'Filed', 'GSTR-3B': 'Due in 5 days', 'GSTR-9': 'Pending' },
            aspProvider: 'ClearTax ASP',
            lastReconciliation: '2026-02-12',
            itcMatched: 92
        }
    },
    {
        id: 'aadhaar',
        name: 'Aadhaar / PAN',
        description: 'Identity verification and KYC compliance via DigiLocker',
        icon: Shield,
        color: '#8b5cf6',
        status: 'verified',
        lastSync: 'Verified',
        details: {
            aadhaarVerified: true,
            panVerified: true,
            kycLevel: 'Full KYC',
            digiLockerLinked: true,
            verifiedOn: '2025-11-20'
        }
    },
    {
        id: 'tally',
        name: 'Tally Bridge',
        description: 'Bi-directional sync with on-premise Tally ERP via desktop connector',
        icon: Building2,
        color: '#ef4444',
        status: 'syncing',
        lastSync: 'Syncing...',
        details: {
            connectorVersion: '2.1.4',
            syncMode: 'Bi-directional',
            lastFullSync: '2026-02-13T08:00:00',
            pendingEntries: 23,
            syncFrequency: 'Every 30 min'
        }
    }
]

const StatusBadge = ({ status }) => {
    const config = {
        connected: { color: '#10b981', bg: 'rgba(16,185,129,0.1)', label: 'Connected', icon: Wifi },
        verified: { color: '#8b5cf6', bg: 'rgba(139,92,246,0.1)', label: 'Verified', icon: CheckCircle },
        syncing: { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', label: 'Syncing', icon: RefreshCw },
        disconnected: { color: '#ef4444', bg: 'rgba(239,68,68,0.1)', label: 'Disconnected', icon: WifiOff },
        pending: { color: '#6b7280', bg: 'rgba(107,114,128,0.1)', label: 'Pending', icon: Clock }
    }
    const { color, bg, label, icon: Icon } = config[status] || config.pending
    return (
        <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '4px 10px', borderRadius: 20,
            background: bg, color, fontSize: 11, fontWeight: 600
        }}>
            <Icon size={12} className={status === 'syncing' ? 'spin-slow' : ''} />
            {label}
        </span>
    )
}

export default function DPIStackHub() {
    const [selected, setSelected] = useState('aa')
    const active = dpiSystems.find(d => d.id === selected)

    return (
        <div style={{ padding: '0 8px' }}>
            {/* Header */}
            <div style={{ marginBottom: 28 }}>
                <h2 style={{ fontSize: 22, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                    <Zap size={22} color="var(--accent-primary)" />
                    India Stack — Digital Public Infrastructure
                </h2>
                <p style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 600 }}>
                    Real-time connections to Account Aggregator, OCEN, GSTN, and identity systems.
                    All data fetched via consent-based protocols.
                </p>
            </div>

            {/* Pipeline Visualization */}
            <div style={{
                display: 'flex', gap: 8, marginBottom: 28, overflowX: 'auto',
                padding: '4px 0'
            }}>
                {dpiSystems.map((sys, idx) => (
                    <div key={sys.id} style={{ display: 'flex', alignItems: 'center' }}>
                        <button
                            onClick={() => setSelected(sys.id)}
                            style={{
                                display: 'flex', alignItems: 'center', gap: 10,
                                padding: '12px 18px', borderRadius: 12,
                                border: selected === sys.id ? `2px solid ${sys.color}` : '1px solid var(--glass-border)',
                                background: selected === sys.id ? `${sys.color}10` : 'var(--bg-card)',
                                cursor: 'pointer', transition: 'all 0.2s',
                                minWidth: 'max-content'
                            }}
                        >
                            <div style={{
                                width: 36, height: 36, borderRadius: 10,
                                background: `${sys.color}15`, color: sys.color,
                                display: 'flex', alignItems: 'center', justifyContent: 'center'
                            }}>
                                <sys.icon size={18} />
                            </div>
                            <div style={{ textAlign: 'left' }}>
                                <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{sys.name}</div>
                                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{sys.lastSync}</div>
                            </div>
                        </button>
                        {idx < dpiSystems.length - 1 && (
                            <div style={{ padding: '0 4px', color: 'var(--text-muted)' }}>
                                <ArrowRight size={16} />
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* Detail Panel */}
            {active && (
                <div className="card" style={{ padding: 28 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
                        <div>
                            <h3 style={{ fontSize: 18, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                                <active.icon size={20} color={active.color} />
                                {active.name}
                            </h3>
                            <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>{active.description}</p>
                        </div>
                        <StatusBadge status={active.status} />
                    </div>

                    {/* Account Aggregator Details */}
                    {active.id === 'aa' && (
                        <div>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 20 }}>
                                <div style={{ padding: 14, background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Consent Status</div>
                                    <div style={{ fontSize: 16, fontWeight: 700, color: '#10b981' }}>{active.details.consentStatus}</div>
                                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Expires: {active.details.consentExpiry}</div>
                                </div>
                                <div style={{ padding: 14, background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Data Points Synced</div>
                                    <div style={{ fontSize: 16, fontWeight: 700 }}>{active.details.dataPoints.toLocaleString()}</div>
                                </div>
                                <div style={{ padding: 14, background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Linked Accounts</div>
                                    <div style={{ fontSize: 16, fontWeight: 700 }}>{active.details.linkedAccounts.length}</div>
                                </div>
                            </div>
                            <h4 style={{ fontSize: 13, fontWeight: 600, marginBottom: 10 }}>Linked Bank Accounts</h4>
                            {active.details.linkedAccounts.map((acc, i) => (
                                <div key={i} style={{
                                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                    padding: '10px 14px', borderBottom: '1px solid var(--glass-border)'
                                }}>
                                    <div>
                                        <div style={{ fontSize: 13, fontWeight: 600 }}>{acc.bank}</div>
                                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{acc.type} • {acc.masked}</div>
                                    </div>
                                    <StatusBadge status={acc.status === 'active' ? 'connected' : 'pending'} />
                                </div>
                            ))}
                        </div>
                    )}

                    {/* OCEN Details */}
                    {active.id === 'ocen' && (
                        <div>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 20 }}>
                                <div style={{ padding: 14, background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Credit Line</div>
                                    <div style={{ fontSize: 16, fontWeight: 700, color: '#10b981' }}>{active.details.creditLine}</div>
                                </div>
                                <div style={{ padding: 14, background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Utilization</div>
                                    <div style={{ fontSize: 16, fontWeight: 700 }}>{active.details.utilizationPct}%</div>
                                    <div style={{ width: '100%', height: 4, background: 'var(--glass-border)', borderRadius: 99, marginTop: 6 }}>
                                        <div style={{ width: `${active.details.utilizationPct}%`, height: '100%', background: '#10b981', borderRadius: 99 }} />
                                    </div>
                                </div>
                                <div style={{ padding: 14, background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Active Products</div>
                                    <div style={{ fontSize: 16, fontWeight: 700 }}>{active.details.activeLoanProducts}</div>
                                </div>
                            </div>
                            <h4 style={{ fontSize: 13, fontWeight: 600, marginBottom: 10 }}>Registered Lenders</h4>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                                {active.details.registeredLenders.map((l, i) => (
                                    <span key={i} style={{
                                        padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 500,
                                        background: 'rgba(16,185,129,0.08)', color: '#10b981', border: '1px solid rgba(16,185,129,0.2)'
                                    }}>{l}</span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* GSTN Details */}
                    {active.id === 'gstn' && (
                        <div>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 20 }}>
                                <div style={{ padding: 14, background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>GSTIN</div>
                                    <div style={{ fontSize: 13, fontWeight: 700, fontFamily: 'monospace' }}>{active.details.gstin}</div>
                                </div>
                                <div style={{ padding: 14, background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>ASP Provider</div>
                                    <div style={{ fontSize: 13, fontWeight: 600 }}>{active.details.aspProvider}</div>
                                </div>
                                <div style={{ padding: 14, background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>ITC Match Rate</div>
                                    <div style={{ fontSize: 16, fontWeight: 700, color: '#10b981' }}>{active.details.itcMatched}%</div>
                                </div>
                            </div>
                            <h4 style={{ fontSize: 13, fontWeight: 600, marginBottom: 10 }}>Filing Status</h4>
                            {Object.entries(active.details.filingStatus).map(([key, val]) => (
                                <div key={key} style={{
                                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                    padding: '10px 14px', borderBottom: '1px solid var(--glass-border)'
                                }}>
                                    <span style={{ fontSize: 13, fontWeight: 600 }}>{key}</span>
                                    <span style={{
                                        fontSize: 12, fontWeight: 600,
                                        color: val === 'Filed' ? '#10b981' : val.includes('Due') ? '#f59e0b' : '#ef4444'
                                    }}>
                                        {val === 'Filed' && <CheckCircle size={12} style={{ marginRight: 4, verticalAlign: -1 }} />}
                                        {val.includes('Due') && <Clock size={12} style={{ marginRight: 4, verticalAlign: -1 }} />}
                                        {val === 'Pending' && <AlertCircle size={12} style={{ marginRight: 4, verticalAlign: -1 }} />}
                                        {val}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Aadhaar/PAN Details */}
                    {active.id === 'aadhaar' && (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 14 }}>
                            {[
                                { label: 'Aadhaar', verified: active.details.aadhaarVerified },
                                { label: 'PAN', verified: active.details.panVerified },
                                { label: 'DigiLocker', verified: active.details.digiLockerLinked },
                                { label: 'KYC Level', value: active.details.kycLevel }
                            ].map((item, i) => (
                                <div key={i} style={{ padding: 16, background: 'var(--bg-muted)', borderRadius: 10, display: 'flex', alignItems: 'center', gap: 12 }}>
                                    {item.verified !== undefined ? (
                                        <CheckCircle size={20} color={item.verified ? '#10b981' : '#6b7280'} />
                                    ) : (
                                        <Shield size={20} color="#8b5cf6" />
                                    )}
                                    <div>
                                        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{item.label}</div>
                                        <div style={{ fontSize: 14, fontWeight: 600 }}>
                                            {item.value || (item.verified ? 'Verified ✓' : 'Not Verified')}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Tally Bridge Details */}
                    {active.id === 'tally' && (
                        <div>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 20 }}>
                                <div style={{ padding: 14, background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Connector</div>
                                    <div style={{ fontSize: 13, fontWeight: 700 }}>v{active.details.connectorVersion}</div>
                                </div>
                                <div style={{ padding: 14, background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Sync Mode</div>
                                    <div style={{ fontSize: 13, fontWeight: 600, color: '#6366f1' }}>{active.details.syncMode}</div>
                                </div>
                                <div style={{ padding: 14, background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Pending Entries</div>
                                    <div style={{ fontSize: 16, fontWeight: 700, color: '#f59e0b' }}>{active.details.pendingEntries}</div>
                                </div>
                            </div>
                            <div style={{
                                padding: 14, background: 'rgba(99,102,241,0.06)', borderRadius: 10,
                                border: '1px solid rgba(99,102,241,0.15)', fontSize: 13, color: 'var(--text-secondary)'
                            }}>
                                <RefreshCw size={14} style={{ marginRight: 6, verticalAlign: -2, color: 'var(--accent-primary)' }} />
                                Sync frequency: <strong>{active.details.syncFrequency}</strong> — Desktop connector must be running
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
