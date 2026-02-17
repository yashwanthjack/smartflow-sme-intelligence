import React from 'react'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ReferenceLine } from 'recharts'
import { AlertTriangle, TrendingUp, TrendingDown, Info } from 'lucide-react'

const ShapWaterfall = ({ data }) => {
    let current = 0
    const chartData = data.map(item => {
        const prev = current
        current += item.value
        return {
            name: item.name,
            value: item.value,
            start: Math.min(prev, current),
            end: Math.max(prev, current),
            color: item.value >= 0 ? '#10b981' : '#ef4444',
            description: item.description
        }
    })
    chartData.push({ name: 'Final Score', value: current, start: 0, end: current, color: '#6366f1', description: 'Your calculated credit score' })

    return (
        <div style={{ height: 256, width: '100%', marginTop: 16 }}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <XAxis type="number" domain={[300, 900]} hide />
                    <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11, fill: 'var(--text-muted)' }} />
                    <Tooltip
                        cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                        content={({ active, payload }) => {
                            if (active && payload && payload.length) {
                                const d = payload[0].payload
                                return (
                                    <div style={{
                                        background: 'var(--bg-card)', border: '1px solid var(--glass-border)',
                                        padding: 10, borderRadius: 8, fontSize: 12, boxShadow: '0 4px 16px rgba(0,0,0,0.15)'
                                    }}>
                                        <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{d.name}</div>
                                        <div style={{ color: d.value >= 0 ? '#10b981' : '#ef4444' }}>
                                            Impact: {d.value > 0 ? '+' : ''}{d.value} points
                                        </div>
                                        <div style={{ color: 'var(--text-muted)', marginTop: 4 }}>{d.description}</div>
                                    </div>
                                )
                            }
                            return null
                        }}
                    />
                    <ReferenceLine x={0} stroke="var(--glass-border)" />
                    <Bar dataKey="end" stackId="a" fill="transparent" />
                    <Bar dataKey="value" stackId="a">
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}

export default function ExplainableScoreCard({ scoreData, loading }) {
    if (loading) return (
        <div className="card" style={{ height: 384, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>Calculating score...</div>
        </div>
    )

    if (!scoreData) return null

    // Support both backend field names: 'score' and 'credit_score'
    const score = scoreData.score || scoreData.credit_score || 0
    const risk_band = scoreData.risk_band || 'N/A'
    const risk_label = scoreData.risk_label || scoreData.risk_level || ''
    const factors = scoreData.factors || []
    const shap_values = scoreData.shap_values

    const explainabilityData = shap_values || [
        { name: 'Base Score', value: 600, description: 'Starting baseline for SME' },
        ...factors.map(f => ({
            name: f.factor || f.name || 'Factor',
            value: parseInt(String(f.impact || f.value || '0').replace('+', '')),
            description: f.description || f.factor || ''
        }))
    ]

    const bandColor = risk_band.includes('A') ? '#10b981' : risk_band.includes('B') ? '#f59e0b' : '#ef4444'
    const bandBg = risk_band.includes('A') ? 'rgba(16,185,129,0.1)' : risk_band.includes('B') ? 'rgba(245,158,11,0.1)' : 'rgba(239,68,68,0.1)'

    return (
        <div className="card" style={{ padding: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
                <div>
                    <h3 style={{ fontSize: 17, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <Info size={18} color="var(--accent-primary)" />
                        SmartFlow Credit Score
                    </h3>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>AI-Explained Assessment</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 36, fontWeight: 800, letterSpacing: -1 }}>{score}</div>
                    <div style={{
                        display: 'inline-block', marginTop: 4, padding: '3px 10px',
                        borderRadius: 8, fontSize: 12, fontWeight: 600,
                        background: bandBg, color: bandColor
                    }}>
                        Band {risk_band} • {risk_label}
                    </div>
                </div>
            </div>

            {/* Explainable AI Section */}
            <div style={{ marginBottom: 24 }}>
                <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>
                    Explainable AI (SHAP Analysis)
                </div>
                <div style={{ background: 'var(--bg-muted)', borderRadius: 10, border: '1px solid var(--glass-border)', padding: 16 }}>
                    <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>
                        How your score was calculated based on financial behavior:
                    </p>
                    <ShapWaterfall data={explainabilityData} />
                </div>
            </div>

            {/* Recommendations */}
            {scoreData.recommendations && scoreData.recommendations.length > 0 && (
                <div>
                    <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10 }}>
                        Improvement Actions
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {scoreData.recommendations.slice(0, 3).map((rec, i) => (
                            <div key={i} style={{
                                display: 'flex', gap: 10, fontSize: 13, color: 'var(--text-secondary)',
                                padding: '10px 12px', borderRadius: 8, background: 'var(--bg-muted)',
                                border: '1px solid var(--glass-border)', alignItems: 'flex-start'
                            }}>
                                {rec.includes("Reduce") || rec.includes("Avoid") ? (
                                    <TrendingDown size={16} color="#10b981" style={{ flexShrink: 0, marginTop: 1 }} />
                                ) : (
                                    <TrendingUp size={16} color="var(--accent-primary)" style={{ flexShrink: 0, marginTop: 1 }} />
                                )}
                                {rec}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
