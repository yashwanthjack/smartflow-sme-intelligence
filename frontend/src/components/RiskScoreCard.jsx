import { useState, useEffect } from 'react'
import { useAuth } from '../AuthContext'
import { Shield, TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from 'lucide-react'

const API_BASE = '/api'

export default function RiskScoreCard({ entityId }) {
    const { token } = useAuth()
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!entityId || !token) return

        const fetchRiskScore = async () => {
            try {
                const res = await fetch(`${API_BASE}/data/entities/${entityId}/risk-score`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
                if (res.ok) {
                    const json = await res.json()
                    setData(json)
                }
            } catch (e) {
                console.error('Failed to fetch risk score', e)
            }
            setLoading(false)
        }

        fetchRiskScore()
    }, [entityId, token])

    const getRiskColor = (level) => {
        switch (level) {
            case 'Low': return '#10b981'
            case 'Medium': return '#f59e0b'
            case 'High': return '#ef4444'
            case 'Critical': return '#dc2626'
            default: return '#6366f1'
        }
    }

    const getBandColor = (band) => {
        switch (band) {
            case 'A': return '#10b981'
            case 'B': return '#3b82f6'
            case 'C': return '#f59e0b'
            case 'D': return '#ef4444'
            default: return '#6366f1'
        }
    }

    if (loading) {
        return (
            <div className="card" style={{ padding: 24, textAlign: 'center' }}>
                <div className="loading-spinner" />
            </div>
        )
    }

    if (!data) {
        return null
    }

    const scorePercent = Math.min(100, Math.max(0, (data.credit_score / 900) * 100))

    return (
        <div className="card" style={{ padding: 24 }}>
            <h3 style={{ fontSize: 14, fontWeight: 500, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Shield size={18} color={getRiskColor(data.risk_level)} />
                Credit Risk Assessment
            </h3>

            {/* Main Score Display */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 24, marginBottom: 20 }}>
                {/* Score Circle */}
                <div style={{ position: 'relative', width: 100, height: 100 }}>
                    <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                        <path
                            d="M18 2.0845
                               a 15.9155 15.9155 0 0 1 0 31.831
                               a 15.9155 15.9155 0 0 1 0 -31.831"
                            fill="none"
                            stroke="rgba(255,255,255,0.1)"
                            strokeWidth="3"
                        />
                        <path
                            d="M18 2.0845
                               a 15.9155 15.9155 0 0 1 0 31.831
                               a 15.9155 15.9155 0 0 1 0 -31.831"
                            fill="none"
                            stroke={getRiskColor(data.risk_level)}
                            strokeWidth="3"
                            strokeDasharray={`${scorePercent}, 100`}
                            strokeLinecap="round"
                        />
                    </svg>
                    <div style={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: 24, fontWeight: 'bold' }}>{data.credit_score}</div>
                        <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>/ 900</div>
                    </div>
                </div>

                {/* Details */}
                <div style={{ flex: 1 }}>
                    <div style={{ marginBottom: 12 }}>
                        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>PD Band</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
                            <span style={{
                                width: 32,
                                height: 32,
                                borderRadius: '50%',
                                background: getBandColor(data.pd_band),
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontWeight: 'bold',
                                color: 'white'
                            }}>
                                {data.pd_band}
                            </span>
                            <span style={{ fontSize: 14 }}>
                                {data.pd_percentage}% Default Probability
                            </span>
                        </div>
                    </div>

                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 8,
                        padding: '8px 12px',
                        borderRadius: 8,
                        background: `${getRiskColor(data.risk_level)}20`,
                        color: getRiskColor(data.risk_level)
                    }}>
                        {data.risk_level === 'Low' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
                        <span style={{ fontWeight: 500 }}>{data.risk_level} Risk</span>
                    </div>
                </div>
            </div>

            {/* Factors */}
            {data.factors?.length > 0 && (
                <div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Key Factors</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                        {data.factors.map((f, idx) => {
                            const factorText = typeof f === 'string' ? f : (f.factor || f.name || JSON.stringify(f))
                            const isPositive = typeof f === 'object' ? f.positive : true
                            return (
                                <span
                                    key={idx}
                                    style={{
                                        fontSize: 11,
                                        padding: '4px 8px',
                                        borderRadius: 4,
                                        background: isPositive ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                                        color: isPositive ? '#10b981' : '#ef4444'
                                    }}
                                >
                                    {factorText}
                                </span>
                            )
                        })}
                    </div>
                </div>
            )}

            {/* Recommendations */}
            {data.recommendations?.length > 0 && (
                <div style={{ marginTop: 16 }}>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Recommendations</div>
                    <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13 }}>
                        {data.recommendations.map((rec, idx) => (
                            <li key={idx} style={{ marginBottom: 4 }}>{rec}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    )
}
