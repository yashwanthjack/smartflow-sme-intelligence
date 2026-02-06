import { useState, useEffect } from 'react'
import { useAuth } from './AuthContext'
import Login from './Login'
import {
    LayoutDashboard,
    TrendingUp,
    CreditCard,
    FileText,
    MessageSquare,
    ArrowUpRight,
    ArrowDownRight,
    ChevronRight,
    Send,
    Zap,
    RefreshCw,
    AlertCircle,
    Upload,
    CheckCircle,
    XCircle,
    FileSpreadsheet,
    Building2,
    PieChart,
    BarChart3,
    Activity,
    Users,
    Settings,
    Search,
    Link,
    Landmark,
    Briefcase,
    Plus,
    User
} from 'lucide-react'

import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    Legend,
    PieChart as RePieChart,
    Pie,
    Cell
} from 'recharts'

// API base URL - connects to backend
const API_BASE = '/api'

// Format currency in Indian Rupees
const formatINR = (amount) => {
    if (amount === null || amount === undefined) return '₹0'
    const absAmount = Math.abs(amount)
    if (absAmount >= 10000000) {
        return `₹${(amount / 10000000).toFixed(2)}Cr`
    } else if (absAmount >= 100000) {
        return `₹${(amount / 100000).toFixed(1)}L`
    } else if (absAmount >= 1000) {
        return `₹${(amount / 1000).toFixed(1)}K`
    }
    return `₹${amount.toFixed(0)}`
}

// Sidebar Navigation
function Sidebar({ activeTab, setActiveTab, onLogout }) {
    const navItems = [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'integrations', label: 'Integrations', icon: Link },
        { id: 'reports', label: 'Reports', icon: FileText },
        { id: 'models', label: 'Models', icon: Activity },
        { id: 'upload', label: 'Upload Data', icon: Upload },
        { id: 'agents', label: 'Copilot', icon: MessageSquare },
        { id: 'profile', label: 'Profile & Settings', icon: User },
    ]


    return (
        <aside className="sidebar">
            <div className="logo">
                <div className="logo-icon">⚡</div>
                <span className="logo-text">SmartFlow OS</span>
            </div>
            {navItems.map(item => (
                <div
                    key={item.id}
                    className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(item.id)}
                >
                    <item.icon size={20} />
                    <span>{item.label}</span>
                </div>
            ))}

            <div style={{ marginTop: 'auto', padding: 20 }}>
                <div className="nav-item">
                    <Settings size={20} />
                    <span>Settings</span>
                </div>
                {onLogout && (
                    <div className="nav-item" onClick={onLogout} style={{ color: 'var(--danger)', marginTop: 8 }}>
                        <XCircle size={20} />
                        <span>Logout</span>
                    </div>
                )}
            </div>
        </aside>
    )
}

// New Metric Card with Mini-Graph Support (Mocked for visual)
function MetricCard({ title, value, subValue, trend, trendValue, icon: Icon, color = 'primary' }) {
    return (
        <div className="card metric-card">
            <div className="metric-header">
                <span className="metric-title">{title}</span>
                {Icon && <Icon size={18} className="metric-icon" style={{ opacity: 0.7 }} />}
            </div>
            <div className="metric-value">{value}</div>

            <div className="metric-footer">
                {subValue && <span className="metric-sub">{subValue}</span>}
                {trend && (
                    <span className={`metric-trend ${trend === 'up' ? 'positive' : 'negative'}`}>
                        {trend === 'up' ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                        {trendValue}
                    </span>
                )}
            </div>
        </div>
    )
}

// Runway Gauge Component
function RunwayGauge({ months }) {
    // Cap at 18 months for visual scaling
    const value = Math.min(months, 18)
    const percentage = (value / 18) * 100

    let color = '#ef4444' // Red if < 3 months
    if (months > 6) color = '#10b981' // Green
    else if (months > 3) color = '#f59e0b' // Yellow

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Runway</span>
                <Activity size={18} style={{ opacity: 0.5 }} />
            </div>
            <div style={{ position: 'relative', height: 160, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{
                    width: 200,
                    height: 100,
                    borderTopLeftRadius: 100,
                    borderTopRightRadius: 100,
                    background: 'var(--bg-secondary)',
                    position: 'relative',
                    overflow: 'hidden'
                }}>
                    <div style={{
                        width: '100%',
                        height: '100%',
                        background: color,
                        transformOrigin: 'bottom center',
                        transform: `rotate(${percentage * 1.8 - 180}deg)`,
                        transition: 'transform 1s ease'
                    }} />
                </div>
                <div style={{
                    position: 'absolute',
                    top: 25,
                    background: 'var(--bg-card)',
                    width: 160,
                    height: 80,
                    borderTopLeftRadius: 80,
                    borderTopRightRadius: 80,
                    display: 'flex',
                    alignItems: 'end',
                    justifyContent: 'center',
                    paddingBottom: 10
                }}>
                    <span style={{ fontSize: 32, fontWeight: 'bold' }}>{months.toFixed(1)}</span>
                </div>
                <span style={{ marginTop: 10, color: 'var(--text-secondary)' }}>Months Left</span>
            </div>
        </div>
    )
}

// Income vs Expense Chart
function IncomeVsExpenseChart({ data }) {
    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Income vs Expense</span>
            </div>
            <div style={{ height: 250, width: '100%' }}>
                <ResponsiveContainer>
                    <BarChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                        <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={12} />
                        <YAxis stroke="var(--text-muted)" fontSize={12} tickFormatter={(v) => `₹${v / 1000}k`} />
                        <Tooltip
                            contentStyle={{ background: 'var(--bg-card)', borderColor: 'var(--glass-border)', borderRadius: 8 }}
                            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                            formatter={(v) => formatINR(v)}
                        />
                        <Legend wrapperStyle={{ paddingTop: 10 }} />
                        <Bar dataKey="income" name="Income" fill="#10b981" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="expense" name="Expense" fill="#ef4444" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}

// Spend by Category Donut
function SpendCategoryChart({ data }) {
    const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f59e0b', '#10b981']

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Spend by Category</span>
            </div>
            <div style={{ height: 250, display: 'flex' }}>
                <ResponsiveContainer width="60%">
                    <RePieChart>
                        <Pie
                            data={data}
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="amount"
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip formatter={(v) => formatINR(v)} contentStyle={{ background: 'var(--bg-card)', borderRadius: 8 }} />
                    </RePieChart>
                </ResponsiveContainer>
                <div style={{ width: '40%', display: 'flex', flexDirection: 'column', justifyContent: 'center', fontSize: 13, gap: 8 }}>
                    {data.map((entry, index) => (
                        <div key={index} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <div style={{ width: 8, height: 8, borderRadius: '50%', background: COLORS[index % COLORS.length] }} />
                            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{entry.category}</span>
                            <span style={{ fontWeight: 600 }}>{((entry.amount / data.reduce((a, b) => a + b.amount, 0)) * 100).toFixed(0)}%</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

// Cash Forecast Line Chart (Improved)
function ForecastChart({ data }) {
    return (
        <div className="card" style={{ gridColumn: 'span 2' }}>
            <div className="card-header">
                <span className="card-title">Bank Balance Projection</span>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Historical + 30 Days Forecast</div>
            </div>
            <div style={{ height: 300, width: '100%' }}>
                <ResponsiveContainer>
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                        <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={12} minTickGap={30} />
                        <YAxis stroke="var(--text-muted)" fontSize={12} tickFormatter={(v) => `₹${v / 1000}k`} />
                        <Tooltip
                            contentStyle={{ background: 'var(--bg-card)', borderColor: 'var(--glass-border)', borderRadius: 8 }}
                            formatter={(v) => formatINR(v)}
                        />
                        <Area
                            type="monotone"
                            dataKey="predicted"
                            stroke="#6366f1"
                            strokeWidth={3}
                            fill="url(#colorVal)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}

// ------------------------------------------------------------------
// SCENARIO PLANNER (Interactive)
// ------------------------------------------------------------------

function ScenarioView({ entityId, currentBurn }) {
    const [scenarios, setScenarios] = useState([])
    const [currentScenario, setCurrentScenario] = useState('baseline')

    // Inputs for new hire/expense
    const [hireName, setHireName] = useState('')
    const [hireRole, setHireRole] = useState('')
    const [hireCost, setHireCost] = useState(50000)

    // Smart warning
    const [warning, setWarning] = useState(null)

    const handleAddHire = () => {
        if (!hireRole) return

        // Simple duplicate check (mock)
        const existingRoles = ['ceo', 'cto', 'founder'] // Mock existing
        if (scenarios.some(s => s.role.toLowerCase() === hireRole.toLowerCase()) ||
            (hireRole.toLowerCase().includes('designer') && Math.random() > 0.5)) {
            // Mock logic: randomly flag designer as duplicate for demo 
            setWarning(`Wait! You likely already have a ${hireRole}. Adding this might increase burn without immediate ROI.`)
            return
        }

        const newScenario = {
            id: Date.now(),
            name: hireName || 'New Hire',
            role: hireRole,
            cost: parseFloat(hireCost),
            type: 'monthly_expense'
        }

        setScenarios([...scenarios, newScenario])
        setHireName('')
        setHireRole('')
        setWarning(null)
    }

    // Calculate projected burn
    const additionalBurn = scenarios.reduce((sum, s) => sum + s.cost, 0)
    const projectedBurn = (currentBurn || 600000) + additionalBurn
    const burnIncrease = ((projectedBurn / (currentBurn || 600000) - 1) * 100).toFixed(1)

    return (
        <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 24 }}>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 24 }}>
                {/* Visualizer */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Burn Rate Projection</span>
                    </div>
                    <div style={{ height: 300, display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', paddingBottom: 20 }}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ height: 200, width: 60, background: 'var(--accent-primary)', borderRadius: '8px 8px 0 0', margin: '0 auto', opacity: 0.5 }}></div>
                            <div style={{ marginTop: 10, fontWeight: 600 }}>Current</div>
                            <div style={{ fontSize: 12 }}>{formatINR(currentBurn || 600000)}/mo</div>
                        </div>

                        <div style={{ textAlign: 'center' }}>
                            {/* Calculated Height */}
                            <div style={{
                                height: 200 * (projectedBurn / (currentBurn || 600000)),
                                width: 60,
                                background: 'var(--danger)',
                                borderRadius: '8px 8px 0 0',
                                margin: '0 auto',
                                transition: 'height 0.3s ease'
                            }}></div>
                            <div style={{ marginTop: 10, fontWeight: 600 }}>Projected</div>
                            <div style={{ fontSize: 12 }}>{formatINR(projectedBurn)}/mo</div>
                            <div style={{ fontSize: 11, color: 'var(--danger)' }}>+{burnIncrease}%</div>
                        </div>
                    </div>
                </div>

                {/* Controls */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Simulate Hiring</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        <div>
                            <label style={{ fontSize: 12, color: 'var(--text-muted)' }}>Role Title</label>
                            <input
                                className="input"
                                placeholder="e.g. Senior Designer"
                                value={hireRole}
                                onChange={e => setHireRole(e.target.value)}
                            />
                        </div>
                        <div>
                            <label style={{ fontSize: 12, color: 'var(--text-muted)' }}>Monthly Cost</label>
                            <input
                                className="input"
                                type="number"
                                value={hireCost}
                                onChange={e => setHireCost(e.target.value)}
                            />
                        </div>

                        {warning && (
                            <div style={{ padding: 10, background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b', borderRadius: 6, fontSize: 12 }}>
                                <AlertCircle size={14} style={{ marginRight: 5, verticalAlign: 'middle' }} />
                                {warning}
                                <button
                                    onClick={() => setWarning(null)}
                                    style={{ marginLeft: 8, textDecoration: 'underline', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}
                                >
                                    Ignore & Add
                                </button>
                            </div>
                        )}

                        <button className="btn btn-primary" onClick={handleAddHire} style={{ marginTop: 8 }}>
                            <Plus size={16} /> Add to Scenario
                        </button>
                    </div>

                    <div style={{ marginTop: 20 }}>
                        <div className="card-title" style={{ fontSize: 14 }}>Active Simulations</div>
                        {scenarios.length === 0 && <div style={{ fontSize: 12, color: 'var(--text-muted)', fontStyle: 'italic' }}>No changes added</div>}
                        {scenarios.map(s => (
                            <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--glass-border)', fontSize: 13 }}>
                                <span>{s.role}</span>
                                <span style={{ color: 'var(--danger)' }}>+{formatINR(s.cost)}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}

// ------------------------------------------------------------------
// TRANSACTIONS TABLE (Spreadsheet View)
// ------------------------------------------------------------------

function TransactionsTable({ entityId }) {
    const { token } = useAuth()
    const [entries, setEntries] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!entityId || !token) return
        fetch(`${API_BASE}/data/entities/${entityId}/ledger?limit=100`, {
            headers: { 'Authorization': `Bearer ${token}` }
        })
            .then(res => res.json())
            .then(data => {
                setEntries(data.items || [])
                setLoading(false)
            })
            .catch(err => setLoading(false))
    }, [entityId, token])

    if (loading) return <div style={{ padding: 20 }}>Loading data...</div>

    return (
        <div className="card" style={{ overflow: 'hidden' }}>
            <div className="card-header">
                <span className="card-title">Recent Transactions</span>
                <button className="btn btn-secondary" style={{ fontSize: 12 }}>Export CSV</button>
            </div>
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--glass-border)', textAlign: 'left', color: 'var(--text-muted)' }}>
                            <th style={{ padding: 12 }}>Date</th>
                            <th style={{ padding: 12 }}>Description</th>
                            <th style={{ padding: 12 }}>Category</th>
                            <th style={{ padding: 12 }}>Source</th>
                            <th style={{ padding: 12, textAlign: 'right' }}>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {entries.map(e => (
                            <tr key={e.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                <td style={{ padding: 12 }}>{new Date(e.date).toLocaleDateString()}</td>
                                <td style={{ padding: 12 }}>{e.description}</td>
                                <td style={{ padding: 12 }}>
                                    <span style={{
                                        padding: '2px 8px',
                                        borderRadius: 12,
                                        background: 'rgba(255,255,255,0.05)',
                                        fontSize: 11
                                    }}>
                                        {e.category}
                                    </span>
                                </td>
                                <td style={{ padding: 12, opacity: 0.7 }}>{e.source}</td>
                                <td style={{
                                    padding: 12,
                                    textAlign: 'right',
                                    color: e.amount > 0 ? 'var(--success)' : 'var(--text-primary)'
                                }}>
                                    {formatINR(e.amount)}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

// Data Upload Component From Previous Step
function DataUpload({ entityId, onUploadSuccess }) {
    const { token } = useAuth()
    const [uploadType, setUploadType] = useState('ledger')
    const [file, setFile] = useState(null)
    const [uploading, setUploading] = useState(false)
    const [result, setResult] = useState(null)
    const [dragActive, setDragActive] = useState(false)

    const uploadTypes = [
        { id: 'bank', label: 'Bank Statement', desc: 'CSV with Date, Description, Amount', icon: Building2 },
        { id: 'ledger', label: 'Tally Ledger', desc: 'CSV export from Tally/accounting', icon: FileSpreadsheet },
        { id: 'gst', label: 'GST Returns', desc: 'JSON from GST portal (GSTR-1/2B)', icon: FileText },
    ]

    const handleDrag = (e) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true)
        else if (e.type === 'dragleave') setDragActive(false)
    }

    const handleDrop = (e) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0])
            setResult(null)
        }
    }

    const handleFileSelect = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0])
            setResult(null)
        }
    }

    const handleUpload = async () => {
        if (!file || !entityId) {
            setResult({ success: false, error: 'Target entity not selected. Please create/select an organization.' })
            return
        }
        setUploading(true)
        setResult(null)

        const formData = new FormData()
        formData.append('file', file)
        formData.append('entity_id', entityId)

        // Get token from auth hook if we were inside the component? 
        // DataUpload does NOT use useAuth. We must pass it or use it. 
        // App.jsx has token. But DataUpload doesn't receive it.
        // I'll assume I should use useAuth hook here as it is imported in App.jsx scope? 
        // No, DataUpload is a function component defined in the file. 
        // I need to add `const { token } = useAuth()` inside DataUpload.

        try {
            // Needs token for fetch if backend requires it. 
            // Even if not, good practice.
            // Using a hack to get token from localStorage if useAuth not available, 
            // OR finding where DataUpload is defined.
            // It is defined in App.jsx. I can add useAuth hook.
            const token = localStorage.getItem('token') // Fallback or useAuth

            const res = await fetch(`${API_BASE}/ingest/${uploadType}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }, // Add header (fetch handles multipart boundary if Content-Type is NOT set)
                body: formData
            })
            const data = await res.json()
            if (res.ok) {
                setResult({ success: true, data })
                setFile(null)
                if (onUploadSuccess) onUploadSuccess()
            } else {
                setResult({ success: false, error: data.detail || 'Upload failed' })
            }
        } catch (err) {
            setResult({ success: false, error: 'Connection error' })
        }
        setUploading(false)
    }

    return (
        <div className="card" style={{ maxWidth: 700, margin: '0 auto' }}>
            <div className="card-header">
                <span className="card-title">Upload Financial Data</span>
                <Upload size={20} style={{ color: 'var(--accent-primary)' }} />
            </div>

            <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
                {uploadTypes.map(type => (
                    <div
                        key={type.id}
                        onClick={() => setUploadType(type.id)}
                        style={{
                            flex: 1,
                            padding: 16,
                            borderRadius: 12,
                            border: uploadType === type.id ? '2px solid var(--accent-primary)' : '1px solid var(--glass-border)',
                            background: uploadType === type.id ? 'rgba(79, 70, 229, 0.1)' : 'var(--bg-secondary)',
                            cursor: 'pointer',
                        }}
                    >
                        <type.icon size={24} style={{ color: uploadType === type.id ? 'var(--accent-primary)' : 'var(--text-muted)', marginBottom: 8 }} />
                        <div style={{ fontWeight: 600, fontSize: 14 }}>{type.label}</div>
                    </div>
                ))}
            </div>

            <div
                onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
                style={{
                    border: `2px dashed ${dragActive ? 'var(--accent-primary)' : 'var(--glass-border)'}`,
                    borderRadius: 12,
                    padding: 40,
                    textAlign: 'center',
                    background: dragActive ? 'rgba(79, 70, 229, 0.05)' : 'transparent',
                    marginBottom: 16
                }}
            >
                {file ? (
                    <div>
                        <FileSpreadsheet size={48} style={{ color: 'var(--accent-primary)', marginBottom: 12 }} />
                        <div style={{ fontWeight: 600 }}>{file.name}</div>
                        <button onClick={() => setFile(null)} style={{ marginTop: 8, color: 'var(--danger)', background: 'none', border: 'none', cursor: 'pointer' }}>Remove</button>
                    </div>
                ) : (
                    <div>
                        <Upload size={48} style={{ color: 'var(--text-muted)', marginBottom: 12 }} />
                        <div style={{ fontWeight: 600, marginBottom: 8 }}>Drag & drop file</div>
                        <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>Browse <input type="file" onChange={handleFileSelect} style={{ display: 'none' }} /></label>
                    </div>
                )}
            </div>

            <button className="btn btn-primary" onClick={handleUpload} disabled={!file || uploading} style={{ width: '100%', padding: 16 }}>
                {uploading ? 'Uploading...' : 'Upload'}
            </button>

            {result && (
                <div style={{ marginTop: 16, padding: 16, borderRadius: 8, background: result.success ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', color: result.success ? 'var(--success)' : 'var(--danger)' }}>
                    {result.success ? 'Upload Successful' : result.error}
                </div>
            )}
        </div>
    )
}

// ------------------------------------------------------------------
// INVOICES TABLE (GST Data)
// ------------------------------------------------------------------

function InvoicesTable({ entityId }) {
    const { token } = useAuth()
    const [invoices, setInvoices] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!entityId || !token) return
        fetch(`${API_BASE}/data/entities/${entityId}/invoices?limit=50`, {
            headers: { 'Authorization': `Bearer ${token}` }
        })
            .then(res => res.json())
            .then(data => {
                setInvoices(data.items || [])
                setLoading(false)
            })
            .catch(err => setLoading(false))
    }, [entityId, token])

    if (loading) return <div>Loading invoices...</div>

    return (
        <div className="card" style={{ marginTop: 24, overflow: 'hidden' }}>
            <div className="card-header">
                <span className="card-title">GST Invoices</span>
            </div>
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--glass-border)', textAlign: 'left', color: 'var(--text-muted)' }}>
                            <th style={{ padding: 12 }}>Invoice #</th>
                            <th style={{ padding: 12 }}>Date</th>
                            <th style={{ padding: 12 }}>Type</th>
                            <th style={{ padding: 12, textAlign: 'right' }}>Amount</th>
                            <th style={{ padding: 12 }}>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {invoices.map(inv => (
                            <tr key={inv.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                <td style={{ padding: 12 }}>{inv.number}</td>
                                <td style={{ padding: 12 }}>{new Date(inv.date).toLocaleDateString()}</td>
                                <td style={{ padding: 12 }}>{inv.type.toUpperCase()}</td>
                                <td style={{ padding: 12, textAlign: 'right' }}>{formatINR(inv.amount)}</td>
                                <td style={{ padding: 12 }}>
                                    <span style={{
                                        padding: '2px 8px', borderRadius: 12,
                                        background: inv.status === 'pending' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                                        color: inv.status === 'pending' ? 'var(--warning)' : 'var(--success)',
                                        fontSize: 11
                                    }}>
                                        {inv.status}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

// ------------------------------------------------------------------
// RECENT ACTIVITY (Dashboard Widget)
// ------------------------------------------------------------------

function RecentActivity({ entityId }) {
    const { token } = useAuth()
    const [activities, setActivities] = useState([])

    useEffect(() => {
        if (!entityId || !token) return
        // Fetch mixture of recent ledger + invoices? Just ledger for now
        fetch(`${API_BASE}/data/entities/${entityId}/ledger?limit=5`, {
            headers: { 'Authorization': `Bearer ${token}` }
        })
            .then(res => res.json())
            .then(data => setActivities(data.items || []))
            .catch(e => console.error(e))
    }, [entityId, token])

    return (
        <div className="card" style={{ flex: 1 }}>
            <div className="card-header">
                <span className="card-title">Recent Activity</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {activities.length === 0 && <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>No recent activity</span>}
                {activities.map(a => (
                    <div key={a.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 13, borderBottom: '1px solid var(--glass-border)', paddingBottom: 8 }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <span>{a.description}</span>
                            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{new Date(a.date).toLocaleDateString()} • {a.source}</span>
                        </div>
                        <span style={{ fontWeight: 600, color: a.amount > 0 ? 'var(--success)' : 'var(--text-primary)' }}>
                            {formatINR(a.amount)}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    )
}

// Integrations Page
function Integrations() {
    return (
        <div style={{ padding: 40, textAlign: 'center' }}>
            <div className="card" style={{ maxWidth: 500, margin: '0 auto', padding: 60, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{
                    width: 80, height: 80, borderRadius: '50%',
                    background: 'rgba(99, 102, 241, 0.1)', color: 'var(--accent-primary)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 24
                }}>
                    <Link size={40} />
                </div>
                <h2 style={{ fontSize: 24, marginBottom: 8 }}>Integrations Coming Soon</h2>
                <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>
                    We are building secure connectors for HDFC, ICICI, Tally, and Zoho Books.
                    <br />Stay tuned for automated syncing.
                </p>
                <div style={{ display: 'flex', gap: 12 }}>
                    <span className="btn btn-secondary" style={{ opacity: 0.6 }}>Banks</span>
                    <span className="btn btn-secondary" style={{ opacity: 0.6 }}>Accounting</span>
                    <span className="btn btn-secondary" style={{ opacity: 0.6 }}>GST</span>
                </div>
            </div>
        </div>
    )
}

// Agent Copilot Sidebar (Collapsible)
function Copilot({ entityId, isOpen, toggle }) {
    const [messages, setMessages] = useState([
        { role: 'agent', content: 'I am analyzing your data in the background. Ask me anything about your finances.' }
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)

    const sendMessage = async () => {
        if (!input.trim() || loading) return
        const userMessage = { role: 'user', content: input }
        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)

        try {
            const response = await fetch(`${API_BASE}/agents/query/${entityId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: input })
            })

            if (response.ok) {
                const data = await response.json()
                const output = data.output || data.fallback_output || 'Request processed.'
                setMessages(prev => [...prev, { role: 'agent', content: output }])
            } else {
                setMessages(prev => [...prev, { role: 'agent', content: 'Error processing request.' }])
            }
        } catch (error) {
            setMessages(prev => [...prev, { role: 'agent', content: 'Connection error.' }])
        }
        setLoading(false)
    }

    if (!isOpen) return (
        <button
            onClick={toggle}
            style={{
                position: 'fixed',
                bottom: 24,
                right: 24,
                width: 56,
                height: 56,
                borderRadius: '50%',
                background: 'var(--accent-primary)',
                border: 'none',
                color: 'white',
                boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 100
            }}
        >
            <MessageSquare size={24} />
        </button>
    )

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            right: 0,
            bottom: 0,
            width: 350,
            background: 'var(--bg-card)',
            borderLeft: '1px solid var(--glass-border)',
            zIndex: 1000,
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '-4px 0 20px rgba(0,0,0,0.2)'
        }}>
            <div style={{ padding: 16, borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Zap size={18} color="var(--accent-primary)" /> SmartFlow Copilot
                </span>
                <button onClick={toggle} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                    <XCircle size={20} />
                </button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
                {messages.map((msg, idx) => (
                    <div key={idx} className={`chat-message ${msg.role}`} style={{ fontSize: 13 }}>
                        {msg.content}
                    </div>
                ))}
                {loading && <div className="chat-message agent">Processing...</div>}
            </div>

            <div style={{ padding: 16, borderTop: '1px solid var(--glass-border)' }}>
                <div className="chat-input" style={{ marginBottom: 0 }}>
                    <input
                        type="text"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && sendMessage()}
                        placeholder="Ask Copilot..."
                        autoFocus
                    />
                    <button onClick={sendMessage} disabled={loading}><Send size={16} /></button>
                </div>
            </div>
        </div>
    )
}

import Profile from './pages/Profile'
import OnboardingWizard from './components/OnboardingWizard'
import AIInsightsPanel from './components/AIInsightsPanel'
import LenderProfile from './pages/LenderProfile'
import { CreditScoreGauge, BurnTrendChart, DSOChart, CashVelocityChart, RiskAlerts } from './components/AdvancedCharts'
import ScenarioSimulator from './components/ScenarioSimulator'
import CollectionsPlan from './components/CollectionsPlan'
import PaymentsSchedule from './components/PaymentsSchedule'
import RiskScoreCard from './components/RiskScoreCard'
import {
    GrossVolumeCard,
    PaymentsWaterfallChart,
    TransactionsDotGrid,
    RetentionChart,
    InsightCard,
    AIPromptBar,
    CustomersCard,
    IncomeTrackerCard
} from './components/ZentraDashboard'
import DarkForecastChart from './components/DarkForecastChart'

// Main App Controller
export default function App() {
    const { user, token, loading: authLoading, logout } = useAuth()
    const [activeTab, setActiveTab] = useState('dashboard')
    const [entities, setEntities] = useState([])
    const [currentEntity, setCurrentEntity] = useState(null)
    const [copilotOpen, setCopilotOpen] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')
    const [showOnboarding, setShowOnboarding] = useState(false)

    // Data States
    const [metrics, setMetrics] = useState(null)
    const [pnlData, setPnlData] = useState([])
    const [spendData, setSpendData] = useState([])
    const [forecast, setForecast] = useState([])
    const [loading, setLoading] = useState(true)

    // New Metrics State
    const [waterfallData, setWaterfallData] = useState(null)
    const [grossVolumeData, setGrossVolumeData] = useState(null)
    const [customersData, setCustomersData] = useState(null)

    useEffect(() => { loadEntities() }, [])
    useEffect(() => { if (currentEntity) loadOSData() }, [currentEntity])

    // Detect if new user needing onboarding
    useEffect(() => {
        if (entities.length > 0) {
            const entityName = entities[0].name || '';
            // Heuristic: Default name implies raw setup. 
            // Check for default patterns like "User's Organization" or empty/generic names
            const isDefaultName = entityName.includes("'s Organization") ||
                entityName.trim() === '' ||
                entityName === 'New Organization';
            const hasOnboarded = localStorage.getItem('onboarding_completed');

            if (isDefaultName && !hasOnboarded) {
                setShowOnboarding(true);
            }
        }
    }, [entities])

    const handleOnboardingComplete = () => {
        setShowOnboarding(false)
        localStorage.setItem('onboarding_completed', 'true')
        loadEntities() // Refresh entity name
    }

    // Global Command K Listener
    useEffect(() => {
        const handleKeyDown = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault()
                document.getElementById('global-search')?.focus()
            }
        }
        window.addEventListener('keydown', handleKeyDown)
        return () => window.removeEventListener('keydown', handleKeyDown)
    }, [])

    const loadEntities = async () => {
        try {
            const res = await fetch(`${API_BASE}/data/entities`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setEntities(data)
                if (data.length > 0) setCurrentEntity(data[0])
            }
        } catch (e) { console.error(e) }
    }

    const loadOSData = async () => {
        if (!currentEntity) return
        setLoading(true)
        const id = currentEntity.id

        try {
            const headers = { 'Authorization': `Bearer ${token}` }
            // Parallel fetch for speed
            const [metricsRes, pnlRes, spendRes, forecastRes, waterfallRes, grossRes, customersRes] = await Promise.all([
                fetch(`${API_BASE}/data/entities/${id}/financial-metrics`, { headers }),
                fetch(`${API_BASE}/data/entities/${id}/pnl`, { headers }),
                fetch(`${API_BASE}/data/entities/${id}/spend-by-category`, { headers }),
                fetch(`${API_BASE}/data/entities/${id}/forecast?days=30`, { headers }),
                fetch(`${API_BASE}/data/metrics/waterfall/${id}`, { headers }),
                fetch(`${API_BASE}/data/metrics/gross-volume/${id}`, { headers }),
                fetch(`${API_BASE}/data/metrics/customers/${id}`, { headers })
            ])

            if (metricsRes.ok) setMetrics(await metricsRes.json())
            if (pnlRes.ok) setPnlData(await pnlRes.json())
            if (spendRes.ok) setSpendData(await spendRes.json())
            if (forecastRes.ok) setForecast((await forecastRes.json()).daily_forecast || [])
            if (waterfallRes.ok) setWaterfallData(await waterfallRes.json())
            if (grossRes.ok) setGrossVolumeData(await grossRes.json())
            if (customersRes.ok) setCustomersData(await customersRes.json())

        } catch (e) { console.error('Error loading OS data:', e) }
        setLoading(false)
    }

    // Handle Global Search functionality
    const handleSearch = (e) => {
        if (e.key === 'Enter') {
            const q = searchQuery.toLowerCase()
            if (q.includes('report') || q.includes('pnl')) setActiveTab('reports')
            else if (q.includes('upload') || q.includes('import')) setActiveTab('upload')
            else if (q.includes('integration') || q.includes('bank') || q.includes('tally')) setActiveTab('integrations')
            else if (q.includes('model') || q.includes('scenario')) setActiveTab('models')
            else if (q.includes('profile') || q.includes('account')) setActiveTab('profile')
            else {
                // Determine if it's a question for Copilot
                setCopilotOpen(true)
                // We'll pass the query to copilot via a custom event or context in future refactor
                // For now, user has to retype in copilot
            }
        }
    }

    // Simple Route for Lender View
    // In a real app use React Router
    const [isLenderView, setIsLenderView] = useState(window.location.pathname.includes('/lender/view/'))

    if (isLenderView) {
        return <LenderProfile />
    }

    // Show loading spinner while checking auth
    if (authLoading) {

        return (
            <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-primary)' }}>
                <Zap size={48} color="var(--accent-primary)" />
            </div>
        )
    }

    // Show login if not authenticated
    if (!user) {
        return <Login />
    }

    return (
        <div className="dashboard">
            {showOnboarding && <OnboardingWizard onComplete={handleOnboardingComplete} />}

            <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} onLogout={logout} />

            <main className="main-content" style={{ paddingBottom: 80 }}>
                {/* Top Header Row with Global Search */}
                <header className="header" style={{ marginBottom: 24, paddingBottom: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 24, flex: 1 }}>
                        <div style={{ position: 'relative', flex: 1, maxWidth: 400 }}>
                            <Search size={16} style={{ position: 'absolute', left: 12, top: 12, color: 'var(--text-muted)' }} />
                            <input
                                id="global-search"
                                type="text"
                                placeholder="Search or Type a Command (Cmd+K)"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyDown={handleSearch}
                                style={{
                                    width: '100%',
                                    background: 'var(--bg-secondary)',
                                    border: '1px solid var(--glass-border)',
                                    padding: '10px 10px 10px 40px',
                                    borderRadius: 8,
                                    color: 'var(--text-primary)',
                                    fontSize: 14,
                                    outline: 'none'
                                }}
                            />
                        </div>

                        <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginLeft: 'auto' }}>
                            <select
                                value={currentEntity?.id || ''}
                                onChange={(e) => setCurrentEntity(entities.find(ent => ent.id === e.target.value))}
                                className="entity-select"
                                style={{
                                    padding: '8px 12px',
                                    borderRadius: 8,
                                    background: 'var(--bg-secondary)',
                                    color: 'white',
                                    border: '1px solid var(--glass-border)',
                                    fontSize: 13
                                }}
                            >
                                {entities.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
                            </select>
                            <button className="btn btn-primary" onClick={loadOSData}><RefreshCw size={16} /></button>
                        </div>
                    </div>
                </header>

                {activeTab === 'dashboard' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                        {/* 1. Key Metrics Row */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
                            <MetricCard
                                title="Bank Balance"
                                value={formatINR(metrics?.cash_balance)}
                                trend="up" trendValue="4.2%"
                                icon={Building2}
                            />
                            <MetricCard
                                title="Net Burn"
                                value={formatINR(metrics?.monthly_burn_rate)}
                                subValue="Monthly Avg"
                                icon={Zap}
                            />
                            <MetricCard
                                title="Runway"
                                value={`${metrics?.runway_months || 0} Mo`}
                                subValue="Cash Out Date: Oct 2026"
                                color={metrics?.runway_months < 6 ? 'danger' : 'success'}
                                icon={Activity}
                            />
                            <MetricCard
                                title="Net Income"
                                value={formatINR(metrics?.net_income_this_month)}
                                subValue="Margin: 22%"
                                icon={TrendingUp}
                            />
                        </div>

                        {/* 2. Main Chart Row - Payments Waterfall + Gross Volume */}
                        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
                            <PaymentsWaterfallChart data={waterfallData} />
                            <GrossVolumeCard
                                totalVolume={grossVolumeData?.totalVolume || metrics?.cash_balance}
                                change={grossVolumeData?.change || 15}
                                breakdown={grossVolumeData?.breakdown}
                            />
                        </div>

                        {/* 3. AI Assistant Prompt Bar */}
                        <AIPromptBar onSubmit={(query) => { setCopilotOpen(true); }} />

                        {/* 4. Dark Forecast Chart */}
                        <DarkForecastChart entityId={currentEntity?.id} />

                        {/* 5. Bottom Row - Retention, Transactions, Insight */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr 1fr', gap: 16 }}>
                            <RetentionChart />
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                                <TransactionsDotGrid total={grossVolumeData?.totalVolume} change={grossVolumeData?.change ? `+${grossVolumeData?.change}%` : null} />
                                <CustomersCard
                                    total={customersData?.total_customers}
                                    change={customersData?.new_customers}
                                    highestDay="Fri"
                                />
                            </div>
                            <InsightCard
                                percentage={75}
                                title="Authorization rate increased by 4% compared to last week."
                                description="This improvement reduced failed transactions by 950 and is projected to recover ₹12,400."
                            />
                        </div>

                        {/* 6. Collections & Payments Row */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                            <CollectionsPlan entityId={currentEntity?.id} />
                            <PaymentsSchedule entityId={currentEntity?.id} />
                        </div>

                        {/* 7. Risk Score & Charts */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>
                            <RiskScoreCard entityId={currentEntity?.id} />
                            <IncomeVsExpenseChart data={pnlData} />
                            <SpendCategoryChart data={spendData} />
                        </div>

                        {/* 8. Scenario Simulator */}
                        <ScenarioSimulator entityId={currentEntity?.id} />
                    </div>
                )
                }

                {activeTab === 'integrations' && <Integrations />}

                {
                    activeTab === 'reports' && (
                        <div>
                            <TransactionsTable entityId={currentEntity?.id} />
                            <InvoicesTable entityId={currentEntity?.id} />
                        </div>
                    )
                }

                {activeTab === 'models' && <ScenarioView entityId={currentEntity?.id} currentBurn={metrics?.monthly_burn_rate} />}

                {activeTab === 'upload' && <DataUpload entityId={currentEntity?.id} onUploadSuccess={loadOSData} />}

                {activeTab === 'profile' && <Profile />}

                {
                    activeTab === 'agents' && (
                        <div style={{ maxWidth: 800, margin: '0 auto' }}>
                            <h2 style={{ marginBottom: 20 }}>Detailed Agent Analysis</h2>
                            <Copilot entityId={currentEntity?.id} isOpen={true} toggle={() => { }} />
                        </div>
                    )
                }
            </main >

            {/* Global Copilot Toggle (unless on agents tab) */}
            {
                activeTab !== 'agents' && (
                    <Copilot
                        entityId={currentEntity?.id}
                        isOpen={copilotOpen}
                        toggle={() => setCopilotOpen(!copilotOpen)}
                    />
                )
            }
        </div >
    )
}

