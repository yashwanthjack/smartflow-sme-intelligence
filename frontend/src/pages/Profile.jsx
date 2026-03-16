import { useState, useEffect } from 'react'
import { useAuth } from '../AuthContext'
import { User, Building, Lock, Save, AlertCircle, CheckCircle, ShieldCheck } from 'lucide-react'

const API_BASE = '/api'

export default function Profile() {
    const { token, user } = useAuth()
    const [profile, setProfile] = useState(null)
    const [org, setOrg] = useState(null)
    const [loading, setLoading] = useState(true)
    const [message, setMessage] = useState(null) // { type: 'success'|'error', text: '' }

    // Form states
    const [fullName, setFullName] = useState('')
    const [passwordData, setPasswordData] = useState({ old: '', new: '' })

    // Org states
    const [orgName, setOrgName] = useState('')
    const [gstin, setGstin] = useState('')

    useEffect(() => {
        fetchData()
    }, [token])

    const fetchData = async () => {
        try {
            // Fetch Profile
            const pRes = await fetch(`${API_BASE}/profile/me`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            const pData = await pRes.json()
            setProfile(pData)
            setFullName(pData.full_name || '')

            // Fetch Org (if linked)
            if (pData.entity_id) {
                const oRes = await fetch(`${API_BASE}/org/`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
                if (oRes.ok) {
                    const oData = await oRes.json()
                    setOrg(oData)
                    setOrgName(oData.name)
                    setGstin(oData.gstin || '')
                }
            }
            setLoading(false)
        } catch (e) {
            console.error(e)
            setLoading(false)
        }
    }

    const handleUpdateProfile = async () => {
        setMessage(null)
        try {
            const res = await fetch(`${API_BASE}/profile/me`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ full_name: fullName })
            })
            if (res.ok) {
                setMessage({ type: 'success', text: 'Profile updated successfully' })
                fetchData()
            } else {
                setMessage({ type: 'error', text: 'Failed to update profile' })
            }
        } catch (e) {
            setMessage({ type: 'error', text: e.message })
        }
    }

    const handleChangePassword = async () => {
        setMessage(null)
        try {
            const res = await fetch(`${API_BASE}/profile/password`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    old_password: passwordData.old,
                    new_password: passwordData.new
                })
            })
            const data = await res.json()
            if (res.ok) {
                setMessage({ type: 'success', text: 'Password changed successfully' })
                setPasswordData({ old: '', new: '' })
            } else {
                setMessage({ type: 'error', text: data.detail || 'Failed to change password' })
            }
        } catch (e) {
            setMessage({ type: 'error', text: e.message })
        }
    }

    const handleUpdateOrg = async () => {
        setMessage(null)
        try {
            const res = await fetch(`${API_BASE}/org/`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: orgName,
                    gstin: gstin
                })
            })
            if (res.ok) {
                setMessage({ type: 'success', text: 'Organization details updated' })
                fetchData()
            } else {
                setMessage({ type: 'error', text: 'Failed to update organization' })
            }
        } catch (e) {
            setMessage({ type: 'error', text: e.message })
        }
    }

    if (loading) return <div className="p-8 text-center text-muted">Loading profile...</div>

    return (
        <div className="p-8 max-w-4xl mx-auto space-y-8">
            <h1 className="text-2xl font-bold mb-6">Account Settings</h1>

            {message && (
                <div className={`p-4 rounded-lg flex items-center gap-3 ${message.type === 'success' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                    }`}>
                    {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
                    {message.text}
                </div>
            )}

            {/* Personal Info */}
            <div className="card p-6">
                <div className="flex items-center gap-3 mb-6 border-b border-glass-border pb-4">
                    <User className="text-accent" />
                    <h2 className="text-lg font-semibold">Personal Information</h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="text-xs text-muted mb-1 block">Email Address (Read-Only)</label>
                        <input className="input w-full opacity-60 cursor-not-allowed" value={profile?.email} disabled />
                    </div>
                    <div>
                        <label className="text-xs text-muted mb-1 block">Full Name</label>
                        <input className="input w-full" value={fullName} onChange={e => setFullName(e.target.value)} />
                    </div>
                </div>

                <div className="mt-6 flex justify-end">
                    <button className="btn btn-primary flex items-center gap-2" onClick={handleUpdateProfile}>
                        <Save size={16} /> Save Changes
                    </button>
                </div>
            </div>

            {/* Organization Settings */}
            <div className="card p-6">
                <div className="flex items-center gap-3 mb-6 border-b border-glass-border pb-4">
                    <Building className="text-accent" />
                    <h2 className="text-lg font-semibold">Organization Details</h2>
                    {profile?.role !== 'admin' && <span className="text-xs bg-gray-700 px-2 py-1 rounded">ReadOnly</span>}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="text-xs text-muted mb-1 block">Company Name</label>
                        <input
                            className="input w-full"
                            value={orgName}
                            onChange={e => setOrgName(e.target.value)}
                            disabled={profile?.role !== 'admin'}
                        />
                    </div>
                    <div>
                        <label className="text-xs text-muted mb-1 block">GSTIN</label>
                        <input
                            className="input w-full"
                            value={gstin}
                            onChange={e => setGstin(e.target.value)}
                            disabled={profile?.role !== 'admin'}
                        />
                    </div>
                </div>

                {profile?.role === 'admin' && (
                    <div className="mt-6 flex justify-end">
                        <button className="btn btn-primary flex items-center gap-2" onClick={handleUpdateOrg}>
                            <Save size={16} /> Update Organization
                        </button>
                    </div>
                )}
            </div>

            {/* Lender Sharing */}
            {profile?.role === 'admin' && (
                <div className="card p-6">
                    <div className="flex items-center gap-3 mb-6 border-b border-glass-border pb-4">
                        <ShieldCheck className="text-accent" />
                        <h2 className="text-lg font-semibold">Lender Access</h2>
                    </div>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium mb-1">Public Profile Link</p>
                            <p className="text-sm text-muted">Generate a secure, temporary link for lenders to view your financial health report.</p>
                        </div>
                        <button className="btn btn-secondary flex items-center gap-2" onClick={async () => {
                            try {
                                const res = await fetch(`${API_BASE}/lender/access-token`, {
                                    method: 'POST',
                                    headers: { 'Authorization': `Bearer ${token}` }
                                })
                                const data = await res.json()
                                if (res.ok) {
                                    const url = `${window.location.origin}${data.share_url}`
                                    navigator.clipboard.writeText(url)
                                    setMessage({ type: 'success', text: 'Link copied to clipboard! (Valid for 24h)' })
                                }
                            } catch (e) {
                                setMessage({ type: 'error', text: 'Failed to generate link' })
                            }
                        }}>
                            Generate & Copy Link
                        </button>
                    </div>
                </div>
            )}

            {/* Password Security */}
            <div className="card p-6">
                <div className="flex items-center gap-3 mb-6 border-b border-glass-border pb-4">
                    <Lock className="text-accent" />
                    <h2 className="text-lg font-semibold">Security</h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="text-xs text-muted mb-1 block">Current Password</label>
                        <input
                            type="password"
                            className="input w-full"
                            value={passwordData.old}
                            onChange={e => setPasswordData({ ...passwordData, old: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="text-xs text-muted mb-1 block">New Password</label>
                        <input
                            type="password"
                            className="input w-full"
                            value={passwordData.new}
                            onChange={e => setPasswordData({ ...passwordData, new: e.target.value })}
                        />
                    </div>
                </div>

                <div className="mt-6 flex justify-end">
                    <button className="btn btn-secondary flex items-center gap-2" onClick={handleChangePassword}>
                        Update Password
                    </button>
                </div>
            </div>
        </div>
    )
}
