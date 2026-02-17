import React, { useState, useEffect } from 'react'
import { useAuth } from '../AuthContext'
import { DollarSign, Zap, LayoutDashboard } from 'lucide-react'
import { MetricCard, GrossVolumeCard, PaymentsWaterfallChart, CustomersCard, IncomeTrackerCard, TransactionsTable } from './ZentraDashboard'
import HealthPulse from './HealthPulse'
import ExplainableScoreCard from './ExplainableScoreCard'
import ActivityFeed from './ActivityFeed'
import ForecastChart from './ForecastChart'
import AgentStatusCard from './AgentStatusCard'
import TaxComplianceCard from './TaxComplianceCard'

export default function SaasDashboard({ openCopilot }) {
    const { user, token } = useAuth()
    const [metrics, setMetrics] = useState(null)
    const [volumeData, setVolumeData] = useState(null)
    const [waterfallData, setWaterfallData] = useState(null)
    const [incomeData, setIncomeData] = useState(null)
    const [insightData, setInsightData] = useState(null)
    const [gstData, setGstData] = useState(null)
    const [customerData, setCustomerData] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!user || !token) return

        const fetchData = async () => {
            try {
                const headers = { 'Authorization': `Bearer ${token}` }
                const entityId = user.entity_id

                // Parallel fetch
                const [resSummary, resVolume, resWaterfall, resIncome, resInsight, resGst, resCust] = await Promise.all([
                    fetch(`/api/metrics/summary/${entityId}`, { headers }),
                    fetch(`/api/metrics/gross-volume/${entityId}`, { headers }),
                    fetch(`/api/metrics/waterfall/${entityId}`, { headers }),
                    fetch(`/api/metrics/income-tracker/${entityId}`, { headers }),
                    fetch(`/api/metrics/insights/${entityId}`, { headers }),
                    fetch(`/api/metrics/gst-compliance/${entityId}`, { headers }),
                    fetch(`/api/metrics/customers/${entityId}`, { headers })
                ])

                if (resSummary.ok) setMetrics(await resSummary.json())
                if (resVolume.ok) setVolumeData(await resVolume.json())
                if (resWaterfall.ok) setWaterfallData(await resWaterfall.json())
                if (resIncome.ok) setIncomeData(await resIncome.json())
                if (resInsight.ok) setInsightData(await resInsight.json())
                if (resGst.ok) setGstData(await resGst.json())
                if (resCust.ok) setCustomerData(await resCust.json())

            } catch (e) {
                console.error("Failed to fetch dashboard data", e)
            } finally {
                setLoading(false)
            }
        }
        fetchData()
    }, [user, token])

    const handleViewAnalysis = () => {
        if (openCopilot) {
            openCopilot("Analyze my cash flow efficiency and suggest improvements.")
        } else {
            alert("Copilot capability is being initialized. Check back shortly.")
        }
    }

    if (loading) return (
        <div className="loading">
            <div className="loading-spinner" />
        </div>
    )

    return (
        <div className="dashboard">
            <div className="main-content">
                <header className="header">
                    <div>
                        <h1>Financial Overview</h1>
                        <p className="header-subtitle">Welcome back, {user?.full_name}</p>
                    </div>
                    <div className="header-actions">
                        <HealthPulse entityId={user?.entity_id} token={token} />
                        <button className="btn btn-primary" onClick={() => window.print()}>
                            Generate Report
                        </button>
                    </div>
                </header>

                {/* Top Metrics Row */}
                <div className="stats-grid">
                    <MetricCard
                        title="Bank Balance"
                        value={metrics?.bank_balance}
                        change={12}
                        icon={DollarSign}
                    />
                    <MetricCard
                        title="Net Burn"
                        value={metrics?.net_burn}
                        change={-5}
                        changeType="positive" // Lower burn is good
                    />
                    <MetricCard
                        title="Runway"
                        value={metrics?.runway_months ? `${metrics.runway_months.toFixed(1)} Months` : '0 Months'}
                        change={0}
                        prefix=""
                    />
                    <MetricCard
                        title="Net Income"
                        value={metrics?.net_income}
                        change={8}
                    />
                </div>

                {/* Main Content Grid */}
                <div className="content-grid">
                    {/* Left Column (Main Charts) */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

                        {/* Forecast Chart (New) */}
                        <ForecastChart entityId={user?.entity_id} />

                        {/* Credit Score & Volume Row/Grid */}
                        <div className="content-grid-equal">
                            <ScoreWrapper entityId={user?.entity_id} token={token} />
                            <GrossVolumeCard
                                totalVolume={volumeData?.totalVolume || 0}
                                change={volumeData?.change || 0}
                                breakdown={volumeData?.breakdown || []}
                            />
                        </div>

                        {/* Income Tracker (Restored) */}
                        <IncomeTrackerCard
                            weeklyData={incomeData?.weeklyData}
                            changePercent={incomeData?.changePercent}
                        />

                        {/* Waterfall & Tax & Customers */}
                        <div className="content-grid-equal">
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                                <TaxComplianceCard data={gstData} openCopilot={openCopilot} />
                                <CustomersCard
                                    total={customerData?.total_customers || 0}
                                    change={customerData?.new_customers || 0}
                                />
                            </div>
                            <PaymentsWaterfallChart data={waterfallData} />
                        </div>

                        {/* Transactions Table */}
                        <TransactionsTable entityId={user?.entity_id} />
                    </div>

                    {/* Right Column (Activity & Insights) */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                        {/* Agent Workforce (New) */}
                        <AgentStatusCard />

                        <ActivityFeed entityId={user?.entity_id} />

                        <div className="insight-card">
                            <div className="insight-badge">
                                <Zap size={14} fill="currentColor" />
                                <span>Smart Insight</span>
                            </div>
                            <h3 className="insight-title">{insightData?.title || "Gathering Data"}</h3>
                            <p className="insight-description">
                                {insightData?.description || "Not enough data for insights yet."}
                            </p>
                            <button
                                onClick={handleViewAnalysis}
                                className="btn btn-ghost"
                                style={{ color: 'white', padding: '8px 0', marginTop: '12px', justifyContent: 'flex-start' }}
                            >
                                View Analysis →
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

// Wrapper to fetch score data for the card
function ScoreWrapper({ entityId, token }) {
    const [data, setData] = useState(null)
    useEffect(() => {
        if (!entityId) return
        fetch(`/api/data/entities/${entityId}/risk-score`, {
            headers: { 'Authorization': `Bearer ${token}` }
        })
            .then(res => res.json())
            .then(setData)
            .catch(console.error)
    }, [entityId, token])

    return <ExplainableScoreCard scoreData={data} loading={!data} />
}

