import { useState } from 'react'
import { useAuth } from '../AuthContext'
import { Building2, Upload, CheckCircle, ArrowRight } from 'lucide-react'

const API_BASE = '/api'

export default function OnboardingWizard({ entityId: passedEntityId, onComplete }) {
    const { token, user } = useAuth()
    const [step, setStep] = useState(1)
    const [loading, setLoading] = useState(false)

    // Step 1: Organization Details
    const [orgName, setOrgName] = useState('')
    const [industry, setIndustry] = useState('')
    const [entityId, setEntityId] = useState(passedEntityId || null)

    // Step 2: File Upload
    const [file, setFile] = useState(null)

    const handleCreateOrg = async () => {
        setLoading(true)
        try {
            // First updates the existing default entity or creates a new one
            // consistently using the Organization API
            const res = await fetch(`${API_BASE}/org/`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: orgName, industry })
            })
            if (res.ok) {
                const data = await res.json()
                setEntityId(data.id)
                setStep(2)
            } else {
                alert("Failed to save organization details")
            }
        } catch (e) {
            console.error(e)
            alert("Error saving details")
        }
        setLoading(false)
    }

    const handleUpload = async () => {
        if (!file) {
            onComplete() // Skip if no file
            return
        }

        setLoading(true)
        try {
            const formData = new FormData()
            formData.append('file', file)
            // Fix: Backend expects entity_id in form data
            if (entityId) formData.append('entity_id', entityId)
            else if (user?.entity_id) formData.append('entity_id', user.entity_id)

            // Fix: Correct endpoint is /ingest/bank, not /ingest/bank-statement
            const res = await fetch(`${API_BASE}/ingest/bank`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            })
            if (res.ok) {
                setStep(3)
            } else {
                alert("Upload failed")
            }
        } catch (e) {
            console.error(e)
            alert("Error uploading file")
        }
        setLoading(false)
    }

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 100,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(4px)'
        }}>
            <div className="card" style={{
                width: '100%',
                maxWidth: 480,
                padding: 32,
                position: 'relative',
                overflow: 'hidden',
                background: '#ffffff',
                borderRadius: 16,
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
            }}>
                {/* Background decorative elements */}
                <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: 4, background: 'linear-gradient(to right, var(--accent-primary), var(--accent-orange))' }} />

                <div className="mb-8 text-center">
                    <h1 className="text-2xl font-bold mb-2">Welcome to SmartFlow</h1>
                    <p className="text-muted text-sm">Let's get your financial operating system ready.</p>
                </div>

                {/* Step Indicators */}
                <div className="flex items-center justify-center gap-4 mb-8">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${step >= 1 ? 'bg-accent-primary text-white' : 'bg-glass-border text-muted-foreground'}`}>1</div>
                    <div className={`w-12 h-0.5 ${step >= 2 ? 'bg-accent-primary' : 'bg-glass-border'}`} />
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${step >= 2 ? 'bg-accent-primary text-white' : 'bg-glass-border text-muted-foreground'}`}>2</div>
                    <div className={`w-12 h-0.5 ${step >= 3 ? 'bg-accent-primary' : 'bg-glass-border'}`} />
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${step >= 3 ? 'bg-accent-primary text-white' : 'bg-glass-border text-muted-foreground'}`}>3</div>
                </div>

                {/* Step 1: Organization */}
                {step === 1 && (
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 mb-4">
                            <Building2 className="text-accent-primary" />
                            <h3 className="font-semibold">Setup Organization</h3>
                        </div>
                        <div>
                            <label className="text-xs text-muted mb-1 block">Company Name</label>
                            <input
                                className="input w-full"
                                placeholder="e.g. Acme Corp"
                                value={orgName}
                                onChange={e => setOrgName(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="text-xs text-muted mb-1 block">Industry</label>
                            <select
                                className="input w-full"
                                value={industry}
                                onChange={e => setIndustry(e.target.value)}
                            >
                                <option value="">Select Industry</option>
                                <option value="retail">Retail / D2C</option>
                                <option value="saas">SaaS / Technology</option>
                                <option value="manufacturing">Manufacturing</option>
                                <option value="services">Agency / Services</option>
                            </select>
                        </div>
                        <button
                            className="btn btn-primary w-full mt-6 flex justify-center items-center gap-2"
                            onClick={handleCreateOrg}
                            disabled={!orgName || loading}
                        >
                            {loading ? 'Saving...' : <>Next Step <ArrowRight size={16} /></>}
                        </button>
                    </div>
                )}

                {/* Step 2: Upload Data */}
                {step === 2 && (
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 mb-4">
                            <Upload className="text-accent-primary" />
                            <h3 className="font-semibold">Import Financial Data</h3>
                        </div>
                        <div className="border-2 border-dashed border-glass-border rounded-lg p-8 text-center hover:border-accent-primary transition-colors">
                            <input
                                type="file"
                                id="onboard-file"
                                className="hidden"
                                onChange={e => setFile(e.target.files[0])}
                                accept=".xlsx,.xls,.csv"
                            />
                            <label htmlFor="onboard-file" className="cursor-pointer block">
                                <Upload className="mx-auto mb-3 text-muted" size={32} />
                                <p className="text-sm font-medium">{file ? file.name : "Upload Bank Statement"}</p>
                                <p className="text-xs text-muted mt-1">Supports HDFC, ICICI, SBI (XLS/CSV)</p>
                            </label>
                        </div>
                        <button
                            className="btn btn-primary w-full mt-6"
                            onClick={handleUpload}
                            disabled={loading}
                        >
                            {loading ? 'Processing...' : (file ? 'Upload & Continue' : 'Skip for Now')}
                        </button>
                    </div>
                )}

                {/* Step 3: Success */}
                {step === 3 && (
                    <div className="text-center py-8">
                        <div className="w-16 h-16 bg-green-500/20 text-green-400 rounded-full flex items-center justify-center mx-auto mb-4">
                            <CheckCircle size={32} />
                        </div>
                        <h3 className="text-xl font-bold mb-2">All Set!</h3>
                        <p className="text-muted text-sm mb-8">Your financial dashboard is ready.</p>
                        <button
                            className="btn btn-primary w-full"
                            onClick={onComplete}
                        >
                            Go to Dashboard
                        </button>
                    </div>
                )}
            </div>
        </div>
    )
}
