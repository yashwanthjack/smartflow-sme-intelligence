import { useState, useEffect } from 'react'
import { FileCheck, CheckCircle, AlertTriangle, XCircle, Search, Download, Mail, ArrowUpRight, UploadCloud } from 'lucide-react'

// Empty for now as backend ingestion does not yet support line-level reconciliation
const reconciliationData = []

const MatchBadge = ({ type }) => {
    const config = {
        exact: { color: '#10b981', bg: 'rgba(16,185,129,0.08)', label: '✓ Exact Match' },
        fuzzy: { color: '#f59e0b', bg: 'rgba(245,158,11,0.08)', label: '~ Fuzzy Match' },
        mismatch: { color: '#ef4444', bg: 'rgba(239,68,68,0.08)', label: '✗ Mismatch' },
        missing: { color: '#8b5cf6', bg: 'rgba(139,92,246,0.08)', label: '⊘ Not in GSTR-2B' }
    }
    const { color, bg, label } = config[type] || config.mismatch
    return (
        <span style={{ padding: '3px 10px', borderRadius: 12, fontSize: 11, fontWeight: 600, background: bg, color }}>
            {label}
        </span>
    )
}

export default function GSTReconciliation() {
    const [filter, setFilter] = useState('all')
    const [searchTerm, setSearchTerm] = useState('')

    // Fallback if data is empty
    if (!reconciliationData || reconciliationData.length === 0) {
        return (
            <div style={{ padding: '0 8px' }}>
                <div style={{ marginBottom: 24 }}>
                    <h2 style={{ fontSize: 22, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                        <FileCheck size={22} color="#f59e0b" />
                        GST Reconciliation Engine
                    </h2>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                        Automated GSTR-2A/2B matching against your Purchase Register
                    </p>
                </div>

                <div className="card" style={{
                    padding: 48,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    textAlign: 'center',
                    minHeight: 300
                }}>
                    <div style={{
                        width: 80, height: 80, borderRadius: '50%',
                        background: 'rgba(245,158,11,0.1)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        marginBottom: 24
                    }}>
                        <UploadCloud size={40} color="#f59e0b" />
                    </div>
                    <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8, color: 'var(--text-primary)' }}>No GST Data Found</h3>
                    <p style={{ fontSize: 14, color: 'var(--text-muted)', maxWidth: 400, marginBottom: 24 }}>
                        Upload your GSTR-2A/2B files to start the automated reconciliation process and identify ITC mismatches.
                    </p>
                </div>
            </div>
        )
    }

    const totalInvoices = reconciliationData.length
    const matched = reconciliationData.filter(r => r.status === 'matched').length
    const mismatched = reconciliationData.filter(r => r.status === 'mismatch').length
    const missing = reconciliationData.filter(r => r.status === 'missing').length
    const totalITC = reconciliationData.reduce((sum, r) => sum + r.itcEligible, 0)
    const blockedITC = reconciliationData.filter(r => r.status !== 'matched').reduce((sum, r) => sum + r.amount * 0.18, 0)

    const filtered = reconciliationData.filter(r => {
        if (filter !== 'all' && r.status !== filter) return false
        if (searchTerm && !r.vendorName.toLowerCase().includes(searchTerm.toLowerCase()) && !r.invoiceNo.toLowerCase().includes(searchTerm.toLowerCase())) return false
        return true
    })

    return (
        <div style={{ padding: '0 8px' }}>
            {/* Header */}
            <div style={{ marginBottom: 24 }}>
                <h2 style={{ fontSize: 22, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                    <FileCheck size={22} color="#f59e0b" />
                    GST Reconciliation Engine
                </h2>
                <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                    Automated GSTR-2A/2B matching against your Purchase Register with fuzzy logic
                </p>
            </div>

            {/* Summary Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 14, marginBottom: 24 }}>
                <div className="card" style={{ padding: 16, textAlign: 'center' }}>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Total Invoices</div>
                    <div style={{ fontSize: 24, fontWeight: 800 }}>{totalInvoices}</div>
                </div>
                <div className="card" style={{ padding: 16, textAlign: 'center' }}>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Matched</div>
                    <div style={{ fontSize: 24, fontWeight: 800, color: '#10b981' }}>{matched}</div>
                </div>
                <div className="card" style={{ padding: 16, textAlign: 'center' }}>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Mismatched</div>
                    <div style={{ fontSize: 24, fontWeight: 800, color: '#ef4444' }}>{mismatched}</div>
                </div>
                <div className="card" style={{ padding: 16, textAlign: 'center' }}>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Missing</div>
                    <div style={{ fontSize: 24, fontWeight: 800, color: '#8b5cf6' }}>{missing}</div>
                </div>
                <div className="card" style={{ padding: 16, textAlign: 'center' }}>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>ITC Eligible</div>
                    <div style={{ fontSize: 20, fontWeight: 800, color: '#10b981' }}>₹{(totalITC / 1000).toFixed(0)}K</div>
                </div>
            </div>

            {/* ITC Recovery Banner */}
            {blockedITC > 0 && (
                <div className="card" style={{
                    padding: '16px 20px', marginBottom: 20,
                    background: 'linear-gradient(135deg, rgba(245,158,11,0.08), rgba(239,68,68,0.06))',
                    border: '1px solid rgba(245,158,11,0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                }}>
                    <div>
                        <div style={{ fontSize: 14, fontWeight: 700, color: '#f59e0b', marginBottom: 2 }}>
                            <AlertTriangle size={14} style={{ marginRight: 6, verticalAlign: -2 }} />
                            ₹{(blockedITC / 1000).toFixed(1)}K ITC at risk
                        </div>
                        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                            {mismatched + missing} invoices need vendor follow-up to recover blocked Input Tax Credit
                        </div>
                    </div>
                    <button className="btn btn-primary" style={{ fontSize: 12, padding: '8px 16px' }}>
                        <Mail size={14} style={{ marginRight: 4 }} /> Notify Vendors
                    </button>
                </div>
            )}

            {/* Filters + Search */}
            <div className="card" style={{ padding: '14px 18px', marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: 8 }}>
                    {[
                        { key: 'all', label: 'All' },
                        { key: 'matched', label: 'Matched' },
                        { key: 'mismatch', label: 'Mismatch' },
                        { key: 'missing', label: 'Missing' }
                    ].map(f => (
                        <button
                            key={f.key}
                            onClick={() => setFilter(f.key)}
                            style={{
                                padding: '5px 14px', borderRadius: 20, border: '1px solid var(--glass-border)',
                                background: filter === f.key ? 'var(--text-primary)' : 'transparent',
                                color: filter === f.key ? 'white' : 'var(--text-muted)',
                                fontSize: 12, cursor: 'pointer', fontWeight: 500
                            }}
                        >{f.label}</button>
                    ))}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ position: 'relative' }}>
                        <Search size={14} style={{ position: 'absolute', left: 10, top: 8, color: 'var(--text-muted)' }} />
                        <input
                            type="text"
                            placeholder="Search vendor or invoice..."
                            value={searchTerm}
                            onChange={e => setSearchTerm(e.target.value)}
                            style={{
                                padding: '6px 12px 6px 30px', borderRadius: 8, border: '1px solid var(--glass-border)',
                                background: 'var(--bg-muted)', fontSize: 12, width: 200, outline: 'none',
                                color: 'var(--text-primary)'
                            }}
                        />
                    </div>
                    <button className="btn btn-secondary" style={{ fontSize: 11, padding: '6px 12px' }}>
                        <Download size={12} style={{ marginRight: 4 }} /> Export
                    </button>
                </div>
            </div>

            {/* Reconciliation Table */}
            <div className="card" style={{ overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                    <thead>
                        <tr style={{ borderBottom: '2px solid var(--glass-border)' }}>
                            <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Vendor</th>
                            <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Invoice #</th>
                            <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>GSTR-2B #</th>
                            <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Amount</th>
                            <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Match</th>
                            <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>ITC</th>
                            <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.map(row => (
                            <tr key={row.id} style={{ borderBottom: '1px solid var(--glass-border)', transition: 'background 0.15s' }}
                                onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-muted)'}
                                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                            >
                                <td style={{ padding: '12px 16px' }}>
                                    <div style={{ fontWeight: 600, fontSize: 13 }}>{row.vendorName}</div>
                                    <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'monospace' }}>{row.vendorGstin}</div>
                                </td>
                                <td style={{ padding: '12px 16px', fontFamily: 'monospace', fontSize: 12 }}>{row.invoiceNo}</td>
                                <td style={{ padding: '12px 16px', fontFamily: 'monospace', fontSize: 12 }}>
                                    {row.gstrInvoice || <span style={{ color: '#8b5cf6', fontStyle: 'italic' }}>Not Found</span>}
                                </td>
                                <td style={{ padding: '12px 16px', textAlign: 'right', fontWeight: 600 }}>
                                    ₹{row.amount.toLocaleString()}
                                    {row.diff && (
                                        <div style={{ fontSize: 10, color: '#ef4444' }}>Δ ₹{row.diff.toLocaleString()}</div>
                                    )}
                                </td>
                                <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                    <MatchBadge type={row.matchType} />
                                </td>
                                <td style={{ padding: '12px 16px', textAlign: 'right', fontWeight: 600, color: row.itcEligible > 0 ? '#10b981' : '#6b7280' }}>
                                    {row.itcEligible > 0 ? `₹${row.itcEligible.toLocaleString()}` : '—'}
                                </td>
                                <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                    {row.status !== 'matched' && (
                                        <button style={{
                                            padding: '4px 10px', borderRadius: 6, border: '1px solid rgba(245,158,11,0.3)',
                                            background: 'rgba(245,158,11,0.06)', color: '#f59e0b',
                                            fontSize: 11, cursor: 'pointer', fontWeight: 500
                                        }}>
                                            <Mail size={10} style={{ marginRight: 3, verticalAlign: -1 }} /> Follow Up
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
