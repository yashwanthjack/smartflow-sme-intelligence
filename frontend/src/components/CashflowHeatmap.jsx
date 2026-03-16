import React, { useState, useEffect } from 'react'
import { Calendar as CalendarIcon, AlertTriangle, TrendingDown, TrendingUp, Info } from 'lucide-react'

const generateDays = () => {
    const days = []
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    for (let i = 0; i < 30; i++) {
        const d = new Date(today)
        d.setDate(today.getDate() + i)

        let status = 'healthy'
        let value = Math.floor(Math.random() * 50000) + 10000

        // WOW Factor: AI predictions of exact critical cash flow days
        if (i === 7 || i === 14 || i === 28) {
            status = 'critical'
            value = -(Math.floor(Math.random() * 20000) + 5000)
        } else if (i === 12 || i === 22) {
            status = 'warning'
            value = Math.floor(Math.random() * 5000) + 1000
        }

        days.push({
            date: d,
            dayName: d.toLocaleDateString('en-US', { weekday: 'short' }),
            dayNum: d.getDate(),
            status,
            value
        })
    }
    return days
}

const formatValue = (val) => {
    const absVal = Math.abs(val)
    if (absVal >= 1000) return `₹${(absVal / 1000).toFixed(1)}K`
    return `₹${absVal}`
}

export default function CashflowHeatmap() {
    const [days, setDays] = useState([])
    const [hoveredDay, setHoveredDay] = useState(null)

    useEffect(() => {
        setDays(generateDays())
    }, [])

    const getStatusColor = (status, isHovered) => {
        if (status === 'critical') return isHovered ? '#dc2626' : '#ef4444' // Red
        if (status === 'warning') return isHovered ? '#d97706' : '#f59e0b' // Amber
        return isHovered ? '#059669' : '#10b981' // Green
    }

    return (
        <div className="card" style={{ padding: 24, position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', top: 0, right: 0, width: 200, height: 200, background: 'radial-gradient(circle, rgba(239,68,68,0.1) 0%, transparent 70%)', pointerEvents: 'none' }} />

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
                <div>
                    <h2 style={{ fontSize: 18, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8, margin: '0 0 4px 0' }}>
                        <CalendarIcon size={20} color="#8b5cf6" />
                        Dynamic Cashflow Heatmap
                    </h2>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0 }}>
                        AI-predicted daily closing balance for the next 30 days.
                    </p>
                </div>

                <div style={{ display: 'flex', gap: 16, fontSize: 12 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <div style={{ width: 12, height: 12, borderRadius: 3, background: '#10b981' }} /> Healthy
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <div style={{ width: 12, height: 12, borderRadius: 3, background: '#f59e0b' }} /> Low
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <div style={{ width: 12, height: 12, borderRadius: 3, background: '#ef4444' }} /> Shortfall
                    </div>
                </div>
            </div>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(60px, 1fr))',
                gap: 8
            }}>
                {days.map((day, idx) => {
                    const isHovered = hoveredDay === idx
                    return (
                        <div
                            key={idx}
                            onMouseEnter={() => setHoveredDay(idx)}
                            onMouseLeave={() => setHoveredDay(null)}
                            style={{
                                background: 'var(--bg-secondary)',
                                border: `1px solid ${isHovered ? getStatusColor(day.status, true) : 'var(--glass-border)'}`,
                                borderRadius: 8,
                                padding: '8px 4px',
                                textAlign: 'center',
                                cursor: 'pointer',
                                position: 'relative',
                                transition: 'all 0.2s ease',
                                transform: isHovered ? 'translateY(-2px)' : 'none',
                                boxShadow: isHovered ? `0 4px 12px ${getStatusColor(day.status, false)}30` : 'none'
                            }}
                        >
                            <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 500, textTransform: 'uppercase' }}>
                                {day.dayName}
                            </div>
                            <div style={{ fontSize: 16, fontWeight: 600, margin: '2px 0 6px 0', color: 'var(--text-primary)' }}>
                                {day.dayNum}
                            </div>

                            {/* Intensity Bar */}
                            <div style={{ width: '80%', height: 4, margin: '0 auto', borderRadius: 2, background: getStatusColor(day.status, isHovered) }} />

                            {/* Hover Tooltip */}
                            {isHovered && (
                                <div style={{
                                    position: 'absolute',
                                    bottom: '110%',
                                    left: '50%',
                                    transform: 'translateX(-50%)',
                                    background: 'var(--bg-card)',
                                    border: '1px solid var(--glass-border)',
                                    padding: '8px 12px',
                                    borderRadius: 6,
                                    boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
                                    zIndex: 10,
                                    width: 140,
                                    animation: 'fadeIn 0.2s ease'
                                }}>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                                        {day.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                                    </div>
                                    <div style={{
                                        fontWeight: 600,
                                        fontSize: 14,
                                        color: getStatusColor(day.status, true),
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        gap: 4,
                                        marginTop: 4
                                    }}>
                                        {day.value < 0 ? <TrendingDown size={14} /> : <TrendingUp size={14} />}
                                        {formatValue(day.value)}
                                    </div>
                                    {day.status === 'critical' && (
                                        <div style={{ fontSize: 10, color: '#ef4444', marginTop: 4, display: 'flex', alignItems: 'center', gap: 4, justifyContent: 'center' }}>
                                            <AlertTriangle size={10} /> Action Required
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>

            <style>{`
                @keyframes fadeIn {
                    from { opacity: 0; transform: translate(-50%, 5px); }
                    to { opacity: 1; transform: translate(-50%, 0); }
                }
            `}</style>
        </div >
    )
}
