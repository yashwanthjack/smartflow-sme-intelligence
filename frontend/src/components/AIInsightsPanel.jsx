import { useState, useEffect } from 'react'
import { Sparkles, RefreshCw } from 'lucide-react'

const API_BASE = '/api'

export default function AIInsightsPanel({ entityId, token }) {
    const [summary, setSummary] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (entityId) fetchInsights()
    }, [entityId, token])

    const fetchInsights = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE}/insights/${entityId}/summary`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setSummary(data.summary)
            }
        } catch (e) {
            console.error(e)
        }
        setLoading(false)
    }

    if (loading) return (
        <div className="card p-6 flex items-center justify-center min-h-[150px]">
            <span className="text-muted text-sm flex items-center gap-2">
                <Sparkles size={16} className="animate-pulse text-accent-primary" />
                Generating financial insights...
            </span>
        </div>
    )

    if (!summary) return null

    return (
        <div className="card p-6 relative overflow-hidden group">
            {/* Background Gradient */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-accent-primary/5 rounded-full blur-3xl -z-10 group-hover:bg-accent-primary/10 transition-all" />

            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Sparkles className="text-accent-primary" size={20} />
                    <h3 className="font-semibold text-lg">AI Financial Pulse</h3>
                </div>
                <button
                    onClick={fetchInsights}
                    className="p-1 hover:bg-white/5 rounded-full transition-colors text-muted hover:text-white"
                    title="Refresh Insights"
                >
                    <RefreshCw size={14} />
                </button>
            </div>

            <div className="prose prose-invert prose-sm">
                <p className="text-gray-300 leading-relaxed whitespace-pre-wrap text-sm">
                    {summary}
                </p>
            </div>

            <div className="mt-4 pt-4 border-t border-glass-border flex gap-3">
                <button
                    className="text-xs bg-accent-primary/10 text-accent-primary px-3 py-1.5 rounded-full hover:bg-accent-primary/20 transition-colors"
                >
                    Ask about hiring
                </button>
                <button
                    className="text-xs bg-accent-primary/10 text-accent-primary px-3 py-1.5 rounded-full hover:bg-accent-primary/20 transition-colors"
                >
                    Project cash flow
                </button>
            </div>
        </div>
    )
}
