import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../AuthContext'
import { Brain, Plus, Trash2, Search, Tag, Shield, Lightbulb, Star, BookOpen } from 'lucide-react'

const API_BASE = '/api'

const CATEGORY_CONFIG = {
    rule:       { label: 'Rule',       icon: Shield,    color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' },
    preference: { label: 'Preference', icon: Star,      color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)' },
    insight:    { label: 'Insight',    icon: Lightbulb, color: '#6366f1', bg: 'rgba(99, 102, 241, 0.1)' },
    fact:       { label: 'Fact',       icon: BookOpen,  color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' },
}

export default function MemoryManager({ entityId }) {
    const { token } = useAuth()
    const [memories, setMemories] = useState([])
    const [total, setTotal] = useState(0)
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [filterCategory, setFilterCategory] = useState(null)
    const [showAdd, setShowAdd] = useState(false)
    const [newContent, setNewContent] = useState('')
    const [newCategory, setNewCategory] = useState('insight')
    const [adding, setAdding] = useState(false)

    const fetchMemories = useCallback(async () => {
        if (!entityId || !token) return
        setLoading(true)
        try {
            let url = `${API_BASE}/memory/${entityId}?`
            if (filterCategory) url += `category=${filterCategory}&`
            if (search) url += `search=${encodeURIComponent(search)}&`

            const res = await fetch(url, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setMemories(data.memories || [])
                setTotal(data.total || 0)
            }
        } catch (e) {
            console.error('Failed to fetch memories', e)
        }
        setLoading(false)
    }, [entityId, token, filterCategory, search])

    useEffect(() => { fetchMemories() }, [fetchMemories])

    const addMemory = async () => {
        if (!newContent.trim()) return
        setAdding(true)
        try {
            const res = await fetch(`${API_BASE}/memory/${entityId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: newContent,
                    category: newCategory,
                    importance: 3,
                    source_agent: 'user'
                })
            })
            if (res.ok) {
                setNewContent('')
                setShowAdd(false)
                fetchMemories()
            }
        } catch (e) {
            console.error('Failed to add memory', e)
        }
        setAdding(false)
    }

    const deleteMemory = async (memoryId) => {
        try {
            const res = await fetch(`${API_BASE}/memory/${entityId}/${memoryId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                setMemories(prev => prev.filter(m => m.id !== memoryId))
                setTotal(prev => prev - 1)
            }
        } catch (e) {
            console.error('Failed to delete memory', e)
        }
    }

    return (
        <div style={{ padding: 24, maxWidth: 900, margin: '0 auto' }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{
                        width: 44, height: 44, borderRadius: 12,
                        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>
                        <Brain size={24} color="#fff" />
                    </div>
                    <div>
                        <h2 style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>Agent Memory</h2>
                        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                            {total} memories stored — Agents learn from your preferences
                        </span>
                    </div>
                </div>
                <button
                    className="btn btn-primary"
                    onClick={() => setShowAdd(!showAdd)}
                    style={{ display: 'flex', alignItems: 'center', gap: 6 }}
                >
                    <Plus size={16} /> Add Memory
                </button>
            </div>

            {/* Add Memory Form */}
            {showAdd && (
                <div className="card" style={{
                    padding: 20, marginBottom: 20,
                    border: '1px solid rgba(99, 102, 241, 0.3)',
                    background: 'rgba(99, 102, 241, 0.05)'
                }}>
                    <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
                        {Object.entries(CATEGORY_CONFIG).map(([key, cfg]) => (
                            <button
                                key={key}
                                onClick={() => setNewCategory(key)}
                                style={{
                                    padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 600,
                                    border: newCategory === key ? `2px solid ${cfg.color}` : '1px solid var(--glass-border)',
                                    background: newCategory === key ? cfg.bg : 'transparent',
                                    color: newCategory === key ? cfg.color : 'var(--text-muted)',
                                    cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4
                                }}
                            >
                                <cfg.icon size={12} /> {cfg.label}
                            </button>
                        ))}
                    </div>
                    <div style={{ display: 'flex', gap: 12 }}>
                        <input
                            className="input"
                            placeholder="e.g. Never send urgent reminders to ABC Corp — they are our oldest client"
                            value={newContent}
                            onChange={e => setNewContent(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && addMemory()}
                            style={{ flex: 1 }}
                        />
                        <button className="btn btn-primary" onClick={addMemory} disabled={adding}>
                            {adding ? 'Saving…' : 'Save'}
                        </button>
                    </div>
                </div>
            )}

            {/* Search + Category Filters */}
            <div style={{ display: 'flex', gap: 12, marginBottom: 20, alignItems: 'center' }}>
                <div style={{ position: 'relative', flex: 1 }}>
                    <Search size={16} style={{
                        position: 'absolute', left: 12, top: '50%',
                        transform: 'translateY(-50%)', color: 'var(--text-muted)'
                    }} />
                    <input
                        className="input"
                        placeholder="Search memories..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        style={{ paddingLeft: 36, width: '100%' }}
                    />
                </div>
                <button
                    onClick={() => setFilterCategory(null)}
                    style={{
                        padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 600,
                        border: !filterCategory ? '2px solid #6366f1' : '1px solid var(--glass-border)',
                        background: !filterCategory ? 'rgba(99,102,241,0.1)' : 'transparent',
                        color: !filterCategory ? '#6366f1' : 'var(--text-muted)',
                        cursor: 'pointer'
                    }}
                >All</button>
                {Object.entries(CATEGORY_CONFIG).map(([key, cfg]) => (
                    <button
                        key={key}
                        onClick={() => setFilterCategory(filterCategory === key ? null : key)}
                        style={{
                            padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 600,
                            border: filterCategory === key ? `2px solid ${cfg.color}` : '1px solid var(--glass-border)',
                            background: filterCategory === key ? cfg.bg : 'transparent',
                            color: filterCategory === key ? cfg.color : 'var(--text-muted)',
                            cursor: 'pointer'
                        }}
                    >{cfg.label}</button>
                ))}
            </div>

            {/* Memory List */}
            {loading ? (
                <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
                    Loading memories...
                </div>
            ) : memories.length === 0 ? (
                <div className="card" style={{
                    textAlign: 'center', padding: 60,
                    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12
                }}>
                    <Brain size={48} style={{ color: 'var(--text-muted)', opacity: 0.3 }} />
                    <div style={{ fontSize: 16, fontWeight: 600 }}>No memories yet</div>
                    <div style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 400 }}>
                        Tell the Copilot your preferences (e.g. "Always use polite tone for reminders")
                        and it will remember them for future conversations.
                    </div>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {memories.map(mem => {
                        const cfg = CATEGORY_CONFIG[mem.category] || CATEGORY_CONFIG.insight
                        const Icon = cfg.icon
                        return (
                            <div key={mem.id} className="card" style={{
                                padding: 16, display: 'flex', alignItems: 'center', gap: 14,
                                transition: 'border-color 0.2s',
                                cursor: 'default'
                            }}>
                                <div style={{
                                    width: 36, height: 36, borderRadius: 10,
                                    background: cfg.bg, color: cfg.color,
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    flexShrink: 0
                                }}>
                                    <Icon size={18} />
                                </div>
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontSize: 14, lineHeight: 1.5 }}>{mem.content}</div>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
                                        <span style={{
                                            padding: '1px 8px', borderRadius: 10,
                                            background: cfg.bg, color: cfg.color,
                                            fontSize: 10, fontWeight: 600, marginRight: 8
                                        }}>{cfg.label}</span>
                                        by {mem.source_agent || 'user'}
                                        {mem.created_at && ` · ${new Date(mem.created_at).toLocaleDateString()}`}
                                    </div>
                                </div>
                                <button
                                    onClick={() => deleteMemory(mem.id)}
                                    style={{
                                        background: 'none', border: 'none', cursor: 'pointer',
                                        color: 'var(--text-muted)', padding: 8, borderRadius: 8,
                                        transition: 'color 0.2s'
                                    }}
                                    onMouseEnter={e => e.target.style.color = '#ef4444'}
                                    onMouseLeave={e => e.target.style.color = 'var(--text-muted)'}
                                    title="Forget this memory"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        )
                    })}
                </div>
            )}
        </div>
    )
}
