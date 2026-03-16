import { useState, useEffect } from 'react'
import { Building2, ShieldCheck, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react'

// Note: In a real app, we'd use React Router params to get the token
// For this single-file setup, we might need a workaround or assume standard routing
// We'll assume the token is passed as a prop or parsed from URL window.location in this MVP

const API_BASE = '/api'

export default function LenderProfile() {
    const [loading, setLoading] = useState(true)
    const [data, setData] = useState(null)
    const [error, setError] = useState(null)

    useEffect(() => {
        // Simple URL param parsing for MVP
        const pathParts = window.location.pathname.split('/')
        const token = pathParts[pathParts.length - 1]

        if (token) fetchReport(token)
        else setError("Invalid Link")
    }, [])

    const fetchReport = async (token) => {
        try {
            const res = await fetch(`${API_BASE}/lender/report/${token}`)
            if (res.ok) {
                setData(await res.json())
            } else {
                setError("Link Expired or Invalid")
            }
        } catch (e) {
            setError("Connection Error")
        }
        setLoading(false)
    }

    if (loading) return <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">Loading Report...</div>
    if (error) return <div className="min-h-screen flex items-center justify-center bg-gray-900 text-red-400">{error}</div>
    if (!data) return null

    const { entity_name, industry, financials, credit, risk_assessment } = data

    return (
        <div className="min-h-screen bg-gray-950 text-white font-sans selection:bg-accent-primary/30">
            <div className="max-w-4xl mx-auto p-8">
                {/* Header */}
                <header className="flex items-center justify-between mb-12 border-b border-white/10 pb-6">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-10 h-10 bg-accent-primary rounded-lg flex items-center justify-center">
                                <Building2 className="text-white" size={20} />
                            </div>
                            <h1 className="text-2xl font-bold">{entity_name}</h1>
                        </div>
                        <p className="text-muted text-sm uppercase tracking-wider">{industry} • Verified Profile</p>
                    </div>
                    <div className="text-right">
                        <div className="text-sm text-muted mb-1">SmartFlow Trust Score</div>
                        <div className={`text-3xl font-bold ${credit.score > 700 ? 'text-green-400' : 'text-yellow-400'}`}>
                            {credit.score}
                        </div>
                    </div>
                </header>

                {/* Main Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                    {/* Financial Summary */}
                    <div className="card p-6 col-span-2">
                        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                            <TrendingUp className="text-accent-primary" size={20} />
                            Financial Health
                        </h3>
                        <div className="grid grid-cols-2 gap-y-8 gap-x-4">
                            <div>
                                <p className="text-xs text-muted mb-1">Annual Run Rate</p>
                                <p className="text-xl font-mono text-white">₹{((financials.net_income_this_month * 12) || 0).toLocaleString()}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted mb-1">Monthly Burn</p>
                                <p className="text-xl font-mono text-white">₹{financials.monthly_burn_rate.toLocaleString()}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted mb-1">Cash Balance</p>
                                <p className="text-xl font-mono text-white">₹{financials.cash_balance.toLocaleString()}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted mb-1">Runway</p>
                                <p className={`text-xl font-mono ${financials.runway_months < 6 ? 'text-red-400' : 'text-green-400'}`}>
                                    {financials.runway_months} Months
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* AI Risk Assessment */}
                    <div className="card p-6 bg-accent-primary/5 border-accent-primary/20">
                        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                            <ShieldCheck className="text-accent-primary" size={20} />
                            AI Risk Assessment
                        </h3>
                        <div className="space-y-4">
                            <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                                <p className="text-xs text-muted uppercase mb-1">Risk Level</p>
                                <p className={`font-bold ${credit.risk_level === 'Low' ? 'text-green-400' : 'text-orange-400'}`}>
                                    {credit.risk_level}
                                </p>
                            </div>
                            <div className="text-sm text-gray-300 leading-relaxed">
                                {risk_assessment.summary}
                            </div>
                            <div className="mt-4 pt-4 border-t border-white/10">
                                <p className="text-xs text-muted uppercase mb-2">Recommended Limit</p>
                                <p className="text-xl font-bold text-white">₹{credit.max_credit_limit.toLocaleString()}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <footer className="text-center text-muted text-xs border-t border-white/10 pt-8">
                    <p>Generated by SmartFlow Financial OS. Data verified via Bank Statements & GST Network.</p>
                </footer>
            </div>
        </div>
    )
}
