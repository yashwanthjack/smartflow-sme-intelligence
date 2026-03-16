import React, { useState, useEffect } from 'react'
import { Activity, HeartPulse } from 'lucide-react'

export default function HealthPulse({ entityId, token }) {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!entityId) return

        const authToken = token || localStorage.getItem('token');

        fetch(`/api/metrics/health/${entityId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        })
            .then(res => {
                if (!res.ok) throw new Error('Failed to fetch')
                return res.json()
            })
            .then(setData)
            .catch(console.error)
            .finally(() => setLoading(false))
    }, [entityId, token])

    if (loading) return <div className="card" style={{ height: '180px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading pulse...</div>
    if (!data || !data.components) return null

    const { score, status, components } = data

    // Color logic
    const color = score > 80 ? 'var(--success)' : score > 60 ? 'var(--warning)' : 'var(--danger)'
    const radius = 36
    const circumference = 2 * Math.PI * radius
    const offset = circumference - (score / 100) * circumference

    if (data.interpretation === 'No Data') {
        return (
            <div className="card" style={{ padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', minWidth: '340px' }}>
                <HeartPulse size={24} color="var(--text-muted)" />
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)' }}>Financial Pulse: No Data</span>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Requires financial data to calculate</span>
                </div>
            </div>
        )
    }

    return (
        <div className="card" style={{ padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', minWidth: '340px' }}>
            <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                    <HeartPulse size={16} color="var(--accent-orange)" />
                    Financial Pulse
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px' }}>Composite Health Score</p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', columnGap: '16px', rowGap: '8px' }}>
                    {Object.entries(components).map(([key, val]) => (
                        <div key={key} style={{ fontSize: '11px' }}>
                            <span style={{ color: 'var(--text-muted)', display: 'block', marginBottom: '2px' }}>{key}</span>
                            <div style={{ width: '100%', height: '4px', background: 'var(--bg-muted)', borderRadius: '99px', overflow: 'hidden' }}>
                                <div
                                    style={{
                                        height: '100%', borderRadius: '99px',
                                        width: `${val}%`,
                                        backgroundColor: val > 70 ? 'var(--success)' : val > 40 ? 'var(--warning)' : 'var(--danger)'
                                    }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div style={{ position: 'relative', width: '80px', height: '80px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="80" height="80" style={{ transform: 'rotate(-90deg)' }}>
                    <circle
                        cx="40" cy="40" r={radius}
                        stroke="var(--bg-muted)" strokeWidth="6" fill="transparent"
                    />
                    <circle
                        cx="40" cy="40" r={radius}
                        stroke={color} strokeWidth="6" fill="transparent"
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        strokeLinecap="round"
                        style={{ transition: 'stroke-dashoffset 1s ease' }}
                    />
                </svg>
                <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                    <span style={{ fontSize: '20px', fontWeight: '700', color: 'var(--text-primary)' }}>{score}</span>
                    <span style={{ fontSize: '10px', fontWeight: '600', color: color }}>{status}</span>
                </div>
            </div>
        </div>
    )
}
