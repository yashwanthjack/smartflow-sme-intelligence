import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../AuthContext'
import {
    BookOpen, Plus, Play, Trash2, ChevronDown, ChevronUp,
    CheckCircle, XCircle, Clock, GripVertical, Edit3, X, Save
} from 'lucide-react'

const API_BASE = '/api'

const AGENT_OPTIONS = [
    { value: '', label: 'Auto (Supervisor decides)' },
    { value: 'CollectionsAgent', label: '📋 Collections Agent' },
    { value: 'PaymentsAgent', label: '💰 Payments Agent' },
    { value: 'GSTAgent', label: '🧾 GST Agent' },
    { value: 'CreditAdvisoryAgent', label: '📊 Credit Advisory' },
    { value: 'DecisionAdvisorAgent', label: '🧠 Decision Advisor' },
]

function StatusBadge({ status }) {
    const config = {
        completed: { color: '#10b981', bg: 'rgba(16,185,129,0.1)', icon: CheckCircle, label: 'Completed' },
        failed:    { color: '#ef4444', bg: 'rgba(239,68,68,0.1)',  icon: XCircle,    label: 'Failed' },
        running:   { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', icon: Clock,      label: 'Running' },
    }
    const c = config[status] || config.running
    const Icon = c.icon
    return (
        <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 4,
            padding: '3px 10px', borderRadius: 12, fontSize: 11, fontWeight: 600,
            background: c.bg, color: c.color
        }}>
            <Icon size={12} /> {c.label}
        </span>
    )
}

export default function PlaybookManager({ entityId }) {
    const { token } = useAuth()
    const [playbooks, setPlaybooks] = useState([])
    const [loading, setLoading] = useState(true)
    const [runningId, setRunningId] = useState(null)
    const [expandedRun, setExpandedRun] = useState(null)
    const [runResults, setRunResults] = useState({})
    const [showCreate, setShowCreate] = useState(false)

    // Create form state
    const [newName, setNewName] = useState('')
    const [newDesc, setNewDesc] = useState('')
    const [newSteps, setNewSteps] = useState([{ order: 1, instruction: '', agent_hint: '' }])

    const fetchPlaybooks = useCallback(async () => {
        if (!entityId || !token) return
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE}/playbooks/${entityId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setPlaybooks(data)
            }
        } catch (e) { console.error(e) }
        setLoading(false)
    }, [entityId, token])

    useEffect(() => { fetchPlaybooks() }, [fetchPlaybooks])

    const executePlaybook = async (playbookId) => {
        setRunningId(playbookId)
        try {
            const res = await fetch(`${API_BASE}/playbooks/${entityId}/${playbookId}/run`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setRunResults(prev => ({ ...prev, [playbookId]: data }))
                setExpandedRun(playbookId)
                fetchPlaybooks() // Refresh last_run_at
            }
        } catch (e) { console.error(e) }
        setRunningId(null)
    }

    const createPlaybook = async () => {
        if (!newName.trim() || newSteps.every(s => !s.instruction.trim())) return
        try {
            const res = await fetch(`${API_BASE}/playbooks/${entityId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: newName,
                    description: newDesc,
                    steps: newSteps.filter(s => s.instruction.trim())
                })
            })
            if (res.ok) {
                setShowCreate(false)
                setNewName('')
                setNewDesc('')
                setNewSteps([{ order: 1, instruction: '', agent_hint: '' }])
                fetchPlaybooks()
            }
        } catch (e) { console.error(e) }
    }

    const deletePlaybook = async (id) => {
        try {
            await fetch(`${API_BASE}/playbooks/${entityId}/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            })
            setPlaybooks(prev => prev.filter(p => p.id !== id))
        } catch (e) { console.error(e) }
    }

    const addStep = () => {
        setNewSteps(prev => [...prev, { order: prev.length + 1, instruction: '', agent_hint: '' }])
    }

    const updateStep = (idx, field, value) => {
        setNewSteps(prev => prev.map((s, i) => i === idx ? { ...s, [field]: value } : s))
    }

    const removeStep = (idx) => {
        setNewSteps(prev => prev.filter((_, i) => i !== idx).map((s, i) => ({ ...s, order: i + 1 })))
    }

    return (
        <div style={{ padding: 24, maxWidth: 900, margin: '0 auto' }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{
                        width: 44, height: 44, borderRadius: 12,
                        background: 'linear-gradient(135deg, #10b981, #059669)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>
                        <BookOpen size={24} color="#fff" />
                    </div>
                    <div>
                        <h2 style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>Playbooks</h2>
                        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                            Automate multi-step agent workflows
                        </span>
                    </div>
                </div>
                <button
                    className="btn btn-primary"
                    onClick={() => setShowCreate(!showCreate)}
                    style={{ display: 'flex', alignItems: 'center', gap: 6 }}
                >
                    {showCreate ? <><X size={16} /> Cancel</> : <><Plus size={16} /> New Playbook</>}
                </button>
            </div>

            {/* Create Form */}
            {showCreate && (
                <div className="card" style={{
                    padding: 24, marginBottom: 24,
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    background: 'rgba(16, 185, 129, 0.03)'
                }}>
                    <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Create Playbook</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                        <div>
                            <label style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Name</label>
                            <input className="input" placeholder="e.g. Monthly Close" value={newName} onChange={e => setNewName(e.target.value)} style={{ width: '100%' }} />
                        </div>
                        <div>
                            <label style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Description</label>
                            <input className="input" placeholder="What does this playbook do?" value={newDesc} onChange={e => setNewDesc(e.target.value)} style={{ width: '100%' }} />
                        </div>
                    </div>

                    <label style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 8 }}>Steps</label>
                    {newSteps.map((step, idx) => (
                        <div key={idx} style={{
                            display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8,
                            padding: 10, background: 'rgba(255,255,255,0.03)', borderRadius: 8,
                            border: '1px solid var(--glass-border)'
                        }}>
                            <span style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 700, width: 24 }}>{idx + 1}</span>
                            <input
                                className="input"
                                placeholder="e.g. Check overdue invoices and suggest collection actions"
                                value={step.instruction}
                                onChange={e => updateStep(idx, 'instruction', e.target.value)}
                                style={{ flex: 1 }}
                            />
                            <select
                                value={step.agent_hint}
                                onChange={e => updateStep(idx, 'agent_hint', e.target.value)}
                                style={{
                                    padding: '6px 8px', borderRadius: 6, fontSize: 11,
                                    background: 'var(--bg-secondary)', color: 'var(--text-primary)',
                                    border: '1px solid var(--glass-border)', width: 160
                                }}
                            >
                                {AGENT_OPTIONS.map(opt => (
                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                ))}
                            </select>
                            {newSteps.length > 1 && (
                                <button onClick={() => removeStep(idx)} style={{
                                    background: 'none', border: 'none', cursor: 'pointer',
                                    color: 'var(--text-muted)', padding: 4
                                }}>
                                    <Trash2 size={14} />
                                </button>
                            )}
                        </div>
                    ))}
                    <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
                        <button onClick={addStep} className="btn btn-secondary" style={{ fontSize: 12 }}>
                            <Plus size={14} /> Add Step
                        </button>
                        <button onClick={createPlaybook} className="btn btn-primary" style={{ fontSize: 12, marginLeft: 'auto' }}>
                            <Save size={14} /> Create Playbook
                        </button>
                    </div>
                </div>
            )}

            {/* Playbook List */}
            {loading ? (
                <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>Loading playbooks...</div>
            ) : playbooks.length === 0 ? (
                <div className="card" style={{
                    textAlign: 'center', padding: 60,
                    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12
                }}>
                    <BookOpen size={48} style={{ color: 'var(--text-muted)', opacity: 0.3 }} />
                    <div style={{ fontSize: 16, fontWeight: 600 }}>No playbooks yet</div>
                    <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                        Create your first playbook to automate multi-step financial workflows.
                    </div>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {playbooks.map(pb => {
                        const isRunning = runningId === pb.id
                        const result = runResults[pb.id]
                        const isExpanded = expandedRun === pb.id

                        return (
                            <div key={pb.id} className="card" style={{ padding: 0, overflow: 'hidden' }}>
                                {/* Card Header */}
                                <div style={{
                                    padding: 20, display: 'flex', alignItems: 'center', gap: 16,
                                    borderBottom: isExpanded ? '1px solid var(--glass-border)' : 'none'
                                }}>
                                    <div style={{
                                        width: 40, height: 40, borderRadius: 10,
                                        background: pb.is_template
                                            ? 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.15))'
                                            : 'rgba(16,185,129,0.1)',
                                        color: pb.is_template ? '#6366f1' : '#10b981',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        flexShrink: 0
                                    }}>
                                        <BookOpen size={20} />
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                            <span style={{ fontWeight: 600, fontSize: 15 }}>{pb.name}</span>
                                            {pb.is_template && (
                                                <span style={{
                                                    fontSize: 9, fontWeight: 700, padding: '2px 6px', borderRadius: 4,
                                                    background: 'rgba(99,102,241,0.15)', color: '#6366f1', textTransform: 'uppercase'
                                                }}>Template</span>
                                            )}
                                        </div>
                                        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                                            {pb.description || `${(pb.steps || []).length} steps`}
                                            {pb.last_run_at && ` · Last run: ${new Date(pb.last_run_at).toLocaleDateString()}`}
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', gap: 8 }}>
                                        <button
                                            className="btn btn-primary"
                                            onClick={() => executePlaybook(pb.id)}
                                            disabled={isRunning}
                                            style={{
                                                display: 'flex', alignItems: 'center', gap: 6,
                                                fontSize: 12, padding: '6px 14px',
                                                opacity: isRunning ? 0.6 : 1
                                            }}
                                        >
                                            <Play size={14} /> {isRunning ? 'Running…' : 'Run Now'}
                                        </button>
                                        {result && (
                                            <button
                                                onClick={() => setExpandedRun(isExpanded ? null : pb.id)}
                                                style={{
                                                    background: 'none', border: '1px solid var(--glass-border)',
                                                    borderRadius: 6, padding: '6px 10px', cursor: 'pointer',
                                                    color: 'var(--text-muted)', display: 'flex', alignItems: 'center'
                                                }}
                                            >
                                                {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                                            </button>
                                        )}
                                        {!pb.is_template && (
                                            <button
                                                onClick={() => deletePlaybook(pb.id)}
                                                style={{
                                                    background: 'none', border: 'none', cursor: 'pointer',
                                                    color: 'var(--text-muted)', padding: 8,
                                                }}
                                                title="Delete playbook"
                                            >
                                                <Trash2 size={14} />
                                            </button>
                                        )}
                                    </div>
                                </div>

                                {/* Expanded Run Results */}
                                {isExpanded && result && (
                                    <div style={{ padding: 20, background: 'rgba(0,0,0,0.15)' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                                            <StatusBadge status={result.status} />
                                            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                                                {result.steps_succeeded}/{result.step_count} steps succeeded
                                            </span>
                                        </div>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                            {(result.step_results || []).map((step, idx) => (
                                                <div key={idx} style={{
                                                    padding: 14, borderRadius: 8,
                                                    background: 'var(--bg-card)',
                                                    border: `1px solid ${step.success ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}`,
                                                }}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                                                        <span style={{
                                                            width: 22, height: 22, borderRadius: '50%',
                                                            background: step.success ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                                                            color: step.success ? '#10b981' : '#ef4444',
                                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                            fontSize: 11, fontWeight: 700
                                                        }}>{step.step}</span>
                                                        <span style={{ fontSize: 13, fontWeight: 600 }}>{step.instruction}</span>
                                                        {step.agent_used && (
                                                            <span style={{
                                                                fontSize: 10, padding: '2px 6px', borderRadius: 4,
                                                                background: 'rgba(99,102,241,0.1)', color: '#6366f1',
                                                                marginLeft: 'auto'
                                                            }}>{step.agent_used}</span>
                                                        )}
                                                    </div>
                                                    <div style={{
                                                        fontSize: 12, color: 'var(--text-secondary)',
                                                        whiteSpace: 'pre-wrap', lineHeight: 1.5,
                                                        maxHeight: 200, overflowY: 'auto'
                                                    }}>
                                                        {step.output}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )
                    })}
                </div>
            )}
        </div>
    )
}
