import React from 'react'
import { ShieldCheck, AlertTriangle, FileText, CheckCircle } from 'lucide-react'

export default function TaxComplianceCard({ data, openCopilot }) {
    const { gstr1, gstr3b, itc_match, pending_amount, pending_vendors } = data || {}

    return (
        <div className="card">
            <div className="card-header" style={{ marginBottom: '20px' }}>
                <span className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <ShieldCheck size={18} style={{ color: 'var(--success)' }} />
                    GST Compliance
                </span>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>FY 2025-26</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                <div style={{ background: 'var(--bg-muted)', padding: '12px', borderRadius: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>GSTR-1</span>
                        <CheckCircle size={14} style={{ color: gstr1?.filed ? 'var(--success)' : 'var(--text-muted)' }} />
                    </div>
                    <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)' }}>{gstr1?.status || 'Unknown'}</div>
                    <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>{gstr1?.date || '-'}</div>
                </div>
                <div style={{ background: 'var(--bg-muted)', padding: '12px', borderRadius: '8px', border: gstr3b?.color === 'danger' ? '1px solid #fee2e2' : 'none' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>GSTR-3B</span>
                        <AlertTriangle size={14} style={{ color: `var(--${gstr3b?.color || 'warning'})` }} />
                    </div>
                    <div style={{ fontSize: '14px', fontWeight: '600', color: `var(--${gstr3b?.color || 'warning'})` }}>{gstr3b?.label || 'Pending'}</div>
                    <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>{gstr3b?.date || '-'}</div>
                </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Input Tax Credit (ITC) Match</span>
                    <span style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-primary)' }}>{itc_match || 0}%</span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'var(--bg-muted)', borderRadius: '99px', overflow: 'hidden' }}>
                    <div style={{ width: `${itc_match || 0}%`, height: '100%', background: 'var(--success)', borderRadius: '99px' }} />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
                    <AlertTriangle size={10} style={{ color: 'var(--warning)' }} />
                    <span>₹{pending_amount?.toLocaleString() || 0} pending from {pending_vendors || 0} vendors</span>
                </div>
            </div>

            <button
                className="btn btn-secondary"
                style={{ width: '100%', fontSize: '13px', padding: '8px' }}
                onClick={() => openCopilot && openCopilot("Review my GST ITC mismatches and identify pending vendors.")}
            >
                Review Mismatches
            </button>
        </div>
    )
}
