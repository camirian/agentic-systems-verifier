'use client'

import { useState, useEffect, useRef } from 'react'
import { FileSearch, Play, RefreshCw, AlertTriangle, Download, Upload, Server, Sparkles, Activity, Trash2 } from 'lucide-react'

// Types based on FastAPI Schema
type Requirement = {
  id: string
  req_name: string
  text: string
  status: string
  priority: string
  source_type: string
  verification_method: string
  rationale: string
  generated_code: string
  verification_status: string
  execution_log: string
}

type Project = {
  filename: string
  title: string
  req_count: number
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('All Projects')
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [selectedReq, setSelectedReq] = useState<Requirement | null>(null)

  const [isLoading, setIsLoading] = useState(true)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isExecuting, setIsExecuting] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [isBrainstormingAll, setIsBrainstormingAll] = useState(false)
  const [isGeneratingAll, setIsGeneratingAll] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [brainstormProgress, setBrainstormProgress] = useState({ current: 0, total: 0 })
  const [generateAllProgress, setGenerateAllProgress] = useState({ current: 0, total: 0 })
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [apiKey, setApiKey] = useState('')

  useEffect(() => {
    setApiKey(localStorage.getItem('google_api_key') || '')
  }, [])

  const handleKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value
    setApiKey(val)
    localStorage.setItem('google_api_key', val)
  }

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('All')
  const [filterPriority, setFilterPriority] = useState<string>('All')
  const [filterMethod, setFilterMethod] = useState<string>('All')

  // Fetch Projects
  useEffect(() => {
    fetch(`${API_BASE}/projects`)
      .then(res => res.json())
      .then(data => {
        setProjects(data)
        if (data.length > 0) {
          // Default to first project if none selected
          setSelectedProject(data[0].filename)
        }
      })
      .catch(err => console.error("Failed to fetch projects:", err))
  }, [])

  // Fetch Requirements when Project changes
  useEffect(() => {
    const fetchReqs = async () => {
      setIsLoading(true)
      try {
        const url = selectedProject && selectedProject !== 'All Projects'
          ? `${API_BASE}/requirements?source_file=${selectedProject}`
          : `${API_BASE}/requirements`

        const res = await fetch(url)
        const data = await res.json()
        setRequirements(data)

        // Auto-select first req if list changed
        if (data.length > 0) {
          setSelectedReq(data[0])
        } else {
          setSelectedReq(null)
        }
      } catch (err) {
        console.error("Failed to fetch requirements:", err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchReqs()
  }, [selectedProject])

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      const key = apiKey || localStorage.getItem('google_api_key') || 'DEMO_KEY'
      formData.append('api_key', key)

      const res = await fetch(`${API_BASE}/ingest`, {
        method: 'POST',
        body: formData
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Upload failed')
      }

      // Refresh projects
      const projRes = await fetch(`${API_BASE}/projects`)
      const projData = await projRes.json()
      setProjects(projData)
      setSelectedProject(file.name) // Auto select the new project
      alert(`Success! Extracted requirements from ${file.name} to the database.`)

    } catch (err: any) {
      console.error("Upload failed:", err)
      alert(`Upload Failed: ${err.message || 'Ensure backend is running and API key is correct.'}`)
    } finally {
      setIsUploading(false)
      // Reset file input
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleBrainstormAll = async () => {
    let pendingReqs = requirements.filter(r => r.status === 'Pending')
    if (pendingReqs.length === 0) {
      alert("No pending requirements to brainstorm in this view.")
      return
    }

    // Since Gemini free tier enforces 15 Requests Per Minute, processing all 400 at once will crash the API.
    // We will batch process a maximum of 10 items at a time to ensure a flawless demo experience.
    const BATCH_LIMIT = 10;
    const isLimited = pendingReqs.length > BATCH_LIMIT;
    if (isLimited) {
      pendingReqs = pendingReqs.slice(0, BATCH_LIMIT);
    }

    setIsBrainstormingAll(true)
    setBrainstormProgress({ current: 0, total: pendingReqs.length })
    const key = apiKey || localStorage.getItem('google_api_key') || 'DEMO_KEY'

    try {
      // Execute sequentially to preserve API quota
      for (let i = 0; i < pendingReqs.length; i++) {
        const req = pendingReqs[i];
        setBrainstormProgress(prev => ({ ...prev, current: i + 1 }))
        const formData = new FormData()
        formData.append('api_key', key)
        await fetch(`${API_BASE}/analyze/${req.id}`, {
          method: 'POST',
          body: formData
        })
      }

      // Refresh data completely
      const url = selectedProject && selectedProject !== 'All Projects'
        ? `${API_BASE}/requirements?source_file=${selectedProject}`
        : `${API_BASE}/requirements`
      const reqRes = await fetch(url)
      const data = await reqRes.json()
      setRequirements(data)

      if (selectedReq) {
        const updated = data.find((r: Requirement) => r.id === selectedReq.id)
        if (updated) setSelectedReq(updated)
      }

      if (isLimited) {
        alert(`Successfully auto-analyzed ${BATCH_LIMIT} requirements!\n\nTo protect your free-tier Google API rate limits, batch generation pauses after 10 requests. You can click the button again in a minute to do the next batch!`)
      }

    } catch (err) {
      console.error("Batch analyze failed:", err)
      alert("Batch brainstorm failed mid-process. Ensure your API key is correct and not rate-limited.")
    } finally {
      setIsBrainstormingAll(false)
      setBrainstormProgress({ current: 0, total: 0 })
    }
  }

  const handleGenerateAll = async () => {
    // Find all analyzed requirements that don't have generated code yet
    let eligibleReqs = requirements.filter(r => r.status === 'Analyzed' && (!r.generated_code || r.generated_code.trim() === ''))
    if (eligibleReqs.length === 0) {
      // Also allow re-generating for all analyzed reqs that already have code
      eligibleReqs = requirements.filter(r => r.status === 'Analyzed')
    }
    if (eligibleReqs.length === 0) {
      alert("No analyzed requirements found. Run 'Brainstorm All Pending' first to analyze requirements.")
      return
    }

    const BATCH_LIMIT = 10;
    const isLimited = eligibleReqs.length > BATCH_LIMIT;
    if (isLimited) {
      eligibleReqs = eligibleReqs.slice(0, BATCH_LIMIT);
    }

    setIsGeneratingAll(true)
    setGenerateAllProgress({ current: 0, total: eligibleReqs.length })
    const key = apiKey || localStorage.getItem('google_api_key') || 'DEMO_KEY'

    try {
      for (let i = 0; i < eligibleReqs.length; i++) {
        const req = eligibleReqs[i];
        setGenerateAllProgress(prev => ({ ...prev, current: i + 1 }))
        const formData = new FormData()
        formData.append('api_key', key)
        await fetch(`${API_BASE}/generate/${req.id}`, {
          method: 'POST',
          body: formData
        })
      }

      // Refresh requirements data
      const url = selectedProject && selectedProject !== 'All Projects'
        ? `${API_BASE}/requirements?source_file=${selectedProject}`
        : `${API_BASE}/requirements`
      const reqRes = await fetch(url)
      const data = await reqRes.json()
      setRequirements(data)

      if (selectedReq) {
        const updated = data.find((r: Requirement) => r.id === selectedReq.id)
        if (updated) setSelectedReq(updated)
      }

      if (isLimited) {
        alert(`Successfully generated pytest scripts for ${BATCH_LIMIT} requirements!\n\nClick the button again in a minute to generate the next batch.`)
      }
    } catch (err) {
      console.error("Batch generate failed:", err)
      alert("Batch code generation failed mid-process. Ensure your API key is correct and not rate-limited.")
    } finally {
      setIsGeneratingAll(false)
      setGenerateAllProgress({ current: 0, total: 0 })
    }
  }

  const handleDeleteProject = () => {
    if (selectedProject === 'All Projects') {
      alert("Please select a specific project to delete first.");
      return;
    }
    setShowDeleteModal(true);
  }

  const confirmDeleteProject = async () => {
    setShowDeleteModal(false);
    setIsDeleting(true);
    try {
      const res = await fetch(`${API_BASE}/projects/${selectedProject}`, {
        method: 'DELETE'
      });

      if (!res.ok) {
        throw new Error("Failed to delete project");
      }

      // Refresh projects
      const projRes = await fetch(`${API_BASE}/projects`);
      const projData = await projRes.json();
      setProjects(projData);
      setSelectedProject(projData.length > 0 ? projData[0].filename : 'All Projects');
    } catch (err) {
      console.error("Delete failed:", err);
      alert("Failed to delete project. Please ensure the backend server is running.");
    } finally {
      setIsDeleting(false);
    }
  }

  const handleAnalyze = async () => {
    if (!selectedReq) return
    setIsAnalyzing(true)

    try {
      const formData = new FormData()
      formData.append('api_key', apiKey || localStorage.getItem('google_api_key') || 'DEMO_KEY')

      const res = await fetch(`${API_BASE}/analyze/${selectedReq.id}`, {
        method: 'POST',
        body: formData
      })

      if (!res.ok) {
        throw new Error("Analysis failed")
      }

      // Refresh requirements to get the updated status and rationale
      const url = selectedProject && selectedProject !== 'All Projects'
        ? `${API_BASE}/requirements?source_file=${selectedProject}`
        : `${API_BASE}/requirements`
      const reqRes = await fetch(url)
      const data = await reqRes.json()
      setRequirements(data)

      const updated = data.find((r: Requirement) => r.id === selectedReq.id)
      if (updated) setSelectedReq(updated)

    } catch (err) {
      console.error("Analysis failed:", err)
      alert("Failed to analyze requirement. Ensure your API key is correct.")
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleGenerateCode = async () => {
    if (!selectedReq) return
    setIsGenerating(true)

    try {
      const formData = new FormData()
      formData.append('api_key', localStorage.getItem('google_api_key') || 'DEMO_KEY')

      const res = await fetch(`${API_BASE}/generate/${selectedReq.id}`, {
        method: 'POST',
        body: formData
      })

      const data = await res.json()

      // Update local state
      const updatedReq = { ...selectedReq, generated_code: data.code }
      setSelectedReq(updatedReq)
      setRequirements(reqs => reqs.map(r => r.id === updatedReq.id ? updatedReq : r))

    } catch (err) {
      console.error("Code gen failed:", err)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleExecuteTest = async () => {
    if (!selectedReq || !selectedReq.generated_code) return
    setIsExecuting(true)

    try {
      const res = await fetch(`${API_BASE}/execute/${selectedReq.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: selectedReq.generated_code })
      })

      const data = await res.json()

      // Update local state
      const updatedReq = {
        ...selectedReq,
        verification_status: data.status,
        execution_log: data.log
      }
      setSelectedReq(updatedReq)
      setRequirements(reqs => reqs.map(r => r.id === updatedReq.id ? updatedReq : r))

    } catch (err) {
      console.error("Execution failed:", err)
    } finally {
      setIsExecuting(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const s = status.toLowerCase()
    return <span className={`badge ${s}`}>{status}</span>
  }

  const filteredReqs = requirements.filter(req => {
    const matchSearch = req.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (req.req_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (req.text || '').toLowerCase().includes(searchQuery.toLowerCase())

    const matchStatus = filterStatus === 'All' || req.status === filterStatus
    const matchPri = filterPriority === 'All' || req.priority === filterPriority
    const matchMethod = filterMethod === 'All' || req.verification_method === filterMethod

    return matchSearch && matchStatus && matchPri && matchMethod
  })

  const exportCSV = () => {
    const headers = ["ID", "Method", "Requirement", "Status", "Priority"]
    const rows = filteredReqs.map(r => [
      r.id,
      r.verification_method || 'Pending',
      `"${(r.text || '').replace(/"/g, '""')}"`,
      r.status,
      r.priority
    ].join(','))
    const csv = [headers.join(','), ...rows].join('\\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `requirements_trace_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
  }

  return (
    <div className="content-area">

      {/* LEFT PANEL: The Traceability Matrix or Welcome Dashboard */}
      <section className="matrix-view glass-panel" style={{ display: 'flex', flexDirection: 'column', position: 'relative' }}>

        {/* Welcome Dashboard (Empty State) */}
        {!isLoading && projects.length === 0 && (
          <div style={{ position: 'absolute', inset: 0, backgroundColor: 'var(--background)', zIndex: 10, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem', borderRadius: '12px' }}>
            <div style={{ textAlign: 'center', maxWidth: '800px' }}>
              <h1 style={{ fontSize: '2.5rem', fontWeight: 700, color: 'white', marginBottom: '1rem', background: 'linear-gradient(90deg, #58a6ff, #3fb950)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Agentic Systems Verifier
              </h1>
              <p style={{ fontSize: '1.2rem', color: '#8b949e', marginBottom: '3rem' }}>
                Your AI-Powered Systems Engineering Co-Pilot. Automate the V-Model workflow from raw document ingestion to executable test generation.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '2rem', marginBottom: '3rem', textAlign: 'left' }}>
                <div style={{ padding: '1.5rem', backgroundColor: 'rgba(22, 27, 34, 0.6)', border: '1px solid var(--border)', borderRadius: '12px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '8px', backgroundColor: 'rgba(88, 166, 255, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
                    <Server size={20} color="var(--primary)" />
                  </div>
                  <h3 style={{ fontSize: '1.1rem', color: 'white', marginBottom: '0.5rem' }}>1. Ingest Documents</h3>
                  <p style={{ fontSize: '0.9rem', color: '#8b949e' }}>Upload your raw PDF specifications. The Agent Cortex will semantically extract and standardize the requirements.</p>
                </div>

                <div style={{ padding: '1.5rem', backgroundColor: 'rgba(22, 27, 34, 0.6)', border: '1px solid var(--border)', borderRadius: '12px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '8px', backgroundColor: 'rgba(210, 153, 34, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
                    <Sparkles size={20} color="var(--warning)" />
                  </div>
                  <h3 style={{ fontSize: '1.1rem', color: 'white', marginBottom: '0.5rem' }}>2. Brainstorm Strategies</h3>
                  <p style={{ fontSize: '0.9rem', color: '#8b949e' }}>Select an extracted requirement. The AI will determine the optimal verification method and generate exact test code.</p>
                </div>

                <div style={{ padding: '1.5rem', backgroundColor: 'rgba(22, 27, 34, 0.6)', border: '1px solid var(--border)', borderRadius: '12px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '8px', backgroundColor: 'rgba(35, 134, 54, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
                    <Activity size={20} color="var(--success)" />
                  </div>
                  <h3 style={{ fontSize: '1.1rem', color: 'white', marginBottom: '0.5rem' }}>3. Execute & Verify</h3>
                  <p style={{ fontSize: '0.9rem', color: '#8b949e' }}>Securely run the generated Pytest scripts against the backend and watch your Project Intelligence metrics climb.</p>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', width: '100%', maxWidth: '300px', gap: '0.5rem' }}>
                  <label style={{ fontSize: '0.85rem', color: '#8b949e', textAlign: 'left', display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <FileSearch size={14} /> Google Gemini API Key
                  </label>
                  <input
                    type="password"
                    placeholder="Paste your API key here..."
                    className="secondary-btn"
                    style={{ width: '100%', padding: '0.75rem', marginBottom: '0.5rem' }}
                    value={apiKey}
                    onChange={handleKeyChange}
                  />
                  <input
                    type="file"
                    accept=".pdf"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    onChange={handleFileUpload}
                  />
                  <button
                    className="premium-btn"
                    onClick={() => {
                      if (!apiKey && !(localStorage.getItem('google_api_key'))) {
                        alert("Please enter a Google API Key first.");
                        return;
                      }
                      fileInputRef.current?.click();
                    }}
                    disabled={isUploading}
                    style={{ padding: '1rem', fontSize: '1.05rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', boxShadow: '0 0 20px rgba(88, 166, 255, 0.2)' }}
                  >
                    {isUploading ? <RefreshCw className="spin" size={20} /> : <Upload size={20} />}
                    {isUploading ? 'Ingesting Document...' : 'Upload First PDF'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Toolbar */}
        <div style={{ padding: '1rem', borderBottom: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <select
              className="secondary-btn"
              style={{ minWidth: '250px' }}
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
            >
              <option value="All Projects">🌍 All Projects ({projects.reduce((acc, p) => acc + p.req_count, 0)} Reqs)</option>
              {projects.map(p => (
                <option key={p.filename} value={p.filename}>
                  📄 {p.title || p.filename} ({p.req_count})
                </option>
              ))}
            </select>

            <button
              className="secondary-btn"
              onClick={handleDeleteProject}
              disabled={isDeleting || selectedProject === 'All Projects'}
              style={{
                padding: '0.5rem 1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                color: selectedProject === 'All Projects' ? '#8b949e' : 'var(--danger)',
                borderColor: selectedProject === 'All Projects' ? 'var(--border)' : 'rgba(218, 54, 51, 0.4)',
                opacity: selectedProject === 'All Projects' ? 0.5 : 1,
                fontSize: '0.85rem'
              }}
              title="Remove this project and all its requirements from the database"
            >
              {isDeleting ? <RefreshCw className="spin" size={16} /> : <Trash2 size={16} />}
              <span>Remove Project</span>
            </button>

            <input
              type="password"
              placeholder="Google API Key..."
              className="secondary-btn"
              style={{ marginLeft: 'auto', width: '200px' }}
              value={apiKey}
              onChange={handleKeyChange}
            />

            <input
              type="file"
              accept=".pdf"
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={handleFileUpload}
            />
            <button
              className="premium-btn"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              style={{ padding: '0.5rem 1rem', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              {isUploading ? <RefreshCw className="spin" size={16} /> : <Upload size={16} />}
              {isUploading ? 'Ingesting...' : 'Upload PDF'}
            </button>
          </div>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <FileSearch size={16} color="#8b949e" style={{ position: 'absolute', left: '10px', top: '10px' }} />
              <input
                type="text"
                placeholder="Search ID, Name, Text..."
                className="secondary-btn"
                style={{ width: '100%', paddingLeft: '35px' }}
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
            </div>
            <select className="secondary-btn" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
              <option value="All">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Analyzed">Analyzed</option>
              <option value="Verified">Verified</option>
              <option value="Failed">Failed</option>
            </select>
            <select className="secondary-btn" value={filterMethod} onChange={e => setFilterMethod(e.target.value)}>
              <option value="All">All Methods</option>
              <option value="Inspection">Inspection</option>
              <option value="Analysis">Analysis</option>
              <option value="Test">Test</option>
              <option value="Demonstration">Demonstration</option>
            </select>
            <button
              className="premium-btn"
              onClick={handleBrainstormAll}
              disabled={isBrainstormingAll || requirements.filter(r => r.status === 'Pending').length === 0}
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem' }}
            >
              {isBrainstormingAll ? <RefreshCw className="spin" size={16} /> : <Sparkles size={16} />}
              {isBrainstormingAll
                ? `Brainstorming (${brainstormProgress.current}/${brainstormProgress.total})...`
                : 'Analyze Next 10 Pending'}
            </button>
            <button
              className="premium-btn"
              onClick={handleGenerateAll}
              disabled={isGeneratingAll || requirements.filter(r => r.status === 'Analyzed').length === 0}
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem', background: 'linear-gradient(135deg, #238636, #2ea043)' }}
            >
              {isGeneratingAll ? <RefreshCw className="spin" size={16} /> : <Play size={16} />}
              {isGeneratingAll
                ? `Generating (${generateAllProgress.current}/${generateAllProgress.total})...`
                : 'Generate Next 10 Scripts'}
            </button>
            <button className="secondary-btn" onClick={exportCSV} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Download size={16} /> Export CSV
            </button>
          </div>

          {/* Rate Limit Information Banner */}
          <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', backgroundColor: 'rgba(88, 166, 255, 0.08)', border: '1px solid rgba(88, 166, 255, 0.2)', borderRadius: '6px', fontSize: '0.85rem', color: '#c9d1d9', display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
            <span style={{ fontSize: '1.2rem', lineHeight: 1 }}>💡</span>
            <div>
              <strong style={{ color: 'var(--primary)' }}>Free-Tier Rate Limiting Active:</strong> To prevent Google Gemini's strict 15 Requests-Per-Minute quota from crashing your app, the batch queue automatically limits processing to the <strong>first 10 eligible requirements (top-down)</strong> per click. Wait 60 seconds between clicks to clear the queue safely.
            </div>
          </div>
        </div>

        {/* Data Table */}
        <div className="data-table-container" style={{ flex: 1, border: 'none', borderRadius: 0 }}>
          {isLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#8b949e' }}>
              <RefreshCw className="spin" style={{ marginRight: '8px', animation: 'spin 1s linear infinite' }} /> Loading requirements matrix...
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Method</th>
                  <th>Requirement</th>
                  <th>Status</th>
                  <th>Priority</th>
                </tr>
              </thead>
              <tbody>
                {filteredReqs.map(req => (
                  <tr
                    key={req.id}
                    className={selectedReq?.id === req.id ? 'selected' : ''}
                    onClick={() => setSelectedReq(req)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td style={{ fontWeight: 500, color: 'var(--primary)' }}>{req.id}</td>
                    <td>{req.verification_method || 'Pending'}</td>
                    <td style={{ maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {req.text}
                    </td>
                    <td>{getStatusBadge(req.status)}</td>
                    <td>
                      <span style={{ color: req.priority === 'Critical' ? 'var(--danger)' : '#c9d1d9' }}>
                        {req.priority}
                      </span>
                    </td>
                  </tr>
                ))}
                {filteredReqs.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{ textAlign: 'center', padding: '3rem', color: '#8b949e' }}>
                      <AlertTriangle size={32} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                      <br />
                      No requirements found. Run the batch ingestion script to populate the database.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      </section>

      {/* RIGHT PANEL: Requirement Inspector */}
      <section className="inspector-panel glass-panel" style={{ overflowY: 'auto' }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border)', backgroundColor: 'var(--secondary)' }}>
          <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#c9d1d9' }}>
            <FileSearch size={18} color="var(--primary)" /> Requirement Inspector
          </h3>
        </div>

        {!selectedReq ? (
          <div style={{ padding: '3rem 2rem', textAlign: 'center', color: '#8b949e', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
            {projects.length === 0 ? (
              <>
                <Upload size={32} style={{ opacity: 0.5 }} />
                <h4 style={{ color: 'white', fontSize: '1.1rem' }}>Welcome to ASV</h4>
                <p style={{ fontSize: '0.9rem', lineHeight: 1.5 }}>Upload a PDF specification using the <strong style={{ color: 'var(--primary)' }}>Upload PDF</strong> button to get started. The AI will extract all testable requirements automatically.</p>
              </>
            ) : (
              <>
                <Sparkles size={32} style={{ opacity: 0.5 }} />
                <h4 style={{ color: 'white', fontSize: '1.1rem' }}>Select a Requirement</h4>
                <p style={{ fontSize: '0.9rem', lineHeight: 1.5 }}>Click on any requirement row in the table to inspect its verification details and execute the 3-step process.</p>
                <div style={{ textAlign: 'left', padding: '1rem', backgroundColor: 'rgba(88, 166, 255, 0.05)', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '0.85rem', lineHeight: 1.8, width: '100%', maxWidth: '320px' }}>
                  <strong style={{ color: 'white', display: 'block', marginBottom: '0.5rem' }}>Verification Pipeline</strong>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><span style={{ background: 'var(--primary)', color: 'white', borderRadius: '50%', width: '18px', height: '18px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem', fontWeight: 700, flexShrink: 0 }}>1</span> AI determines verification method</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><span style={{ background: 'var(--primary)', color: 'white', borderRadius: '50%', width: '18px', height: '18px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem', fontWeight: 700, flexShrink: 0 }}>2</span> AI generates pytest script</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><span style={{ background: 'var(--primary)', color: 'white', borderRadius: '50%', width: '18px', height: '18px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem', fontWeight: 700, flexShrink: 0 }}>3</span> Execute test & verify compliance</div>
                </div>
              </>
            )}
          </div>
        ) : (
          <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

            {/* ── HEADER: Requirement Identity ── */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <span className="badge analyzed" style={{ fontSize: '0.8rem', fontWeight: 700 }}>{selectedReq.id}</span>
                {selectedReq.verification_method && (
                  <span className={`badge ${selectedReq.verification_method.toLowerCase() === 'test' ? 'verified' : 'pending'}`} style={{ fontSize: '0.75rem' }}>
                    {selectedReq.verification_method}
                  </span>
                )}
                {selectedReq.verification_status === 'Pass' && (
                  <span className="badge verified" style={{ fontSize: '0.75rem' }}>✓ Verified</span>
                )}
              </div>
              <h4 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'white', marginBottom: '0.75rem', lineHeight: 1.3 }}>
                {selectedReq.req_name || 'Untitled Requirement'}
              </h4>
              <div style={{ padding: '0.85rem 1rem', backgroundColor: 'rgba(88, 166, 255, 0.05)', borderLeft: '3px solid var(--primary)', borderRadius: '0 6px 6px 0', fontSize: '0.9rem', lineHeight: 1.6, color: '#c9d1d9' }}>
                {selectedReq.text}
              </div>
            </div>

            <hr style={{ borderColor: 'var(--border)', margin: '0.25rem 0' }} />

            {/* ── STEP 1: AI Verification Strategy ── */}
            <div>
              <div className={`step-label ${selectedReq.status !== 'Pending' ? 'completed' : ''}`}>
                <span className="step-number">1</span>
                AI Verification Strategy
              </div>
              <p className="step-description">
                The AI reads the requirement text and determines the optimal verification method: <strong>Test</strong> (automated pytest), <strong>Analysis</strong> (mathematical/design review), or <strong>Inspection</strong> (manual document check).
              </p>

              {selectedReq.status === 'Pending' ? (
                <div>
                  <button
                    className="premium-btn"
                    onClick={handleAnalyze}
                    disabled={isAnalyzing}
                    style={{ justifyContent: 'center', width: '100%', padding: '0.85rem', fontSize: '0.95rem' }}
                  >
                    {isAnalyzing ? <RefreshCw className="spin" size={18} /> : <span style={{ fontSize: '1.1rem' }}>✨</span>}
                    {isAnalyzing ? 'Analyzing Requirement...' : 'Run AI Analysis'}
                  </button>
                </div>
              ) : (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                    <strong style={{ color: 'white', fontSize: '0.9rem' }}>Assigned Method:</strong>
                    <span className={`badge ${selectedReq.verification_method?.toLowerCase() === 'test' ? 'verified' : 'analyzed'}`}>
                      {selectedReq.verification_method || 'Analysis'}
                    </span>
                  </div>
                  {selectedReq.rationale && (
                    <div style={{ padding: '0.75rem 1rem', backgroundColor: 'rgba(88, 166, 255, 0.04)', border: '1px solid var(--border)', borderRadius: '6px', fontSize: '0.85rem', color: '#adbac7', lineHeight: 1.6, fontStyle: 'italic' }}>
                      <strong style={{ fontStyle: 'normal', color: '#8b949e', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px', display: 'block', marginBottom: '0.25rem' }}>AI Rationale</strong>
                      {selectedReq.rationale}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Only show Steps 2 & 3 for Test method */}
            {selectedReq.status !== 'Pending' && selectedReq.verification_method?.toLowerCase() === 'test' && (
              <>
                <hr style={{ borderColor: 'var(--border)', margin: '0.25rem 0' }} />

                {/* ── STEP 2: Generated Test Code ── */}
                <div>
                  <div className={`step-label ${selectedReq.generated_code ? 'completed' : ''}`}>
                    <span className="step-number">2</span>
                    Generated Pytest Script
                  </div>
                  <p className="step-description">
                    The AI writes a complete, executable Python test that validates this specific requirement using pytest and mock frameworks.
                  </p>

                  {!selectedReq.generated_code ? (
                    <button
                      className="premium-btn"
                      onClick={handleGenerateCode}
                      disabled={isGenerating}
                      style={{ justifyContent: 'center', width: '100%', padding: '0.85rem', fontSize: '0.95rem', background: 'linear-gradient(135deg, #238636, #2ea043)' }}
                    >
                      {isGenerating ? <RefreshCw className="spin" size={18} /> : <Play size={18} />}
                      {isGenerating ? 'Generating Script...' : 'Generate Pytest Script'}
                    </button>
                  ) : (
                    <div>
                      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                        <button className="secondary-btn" style={{ flex: 1, fontSize: '0.8rem', padding: '0.5rem' }} onClick={handleGenerateCode} disabled={isGenerating}>
                          {isGenerating ? 'Regenerating...' : '↻ Regenerate'}
                        </button>
                        <button className="secondary-btn" style={{ flex: 1, fontSize: '0.8rem', padding: '0.5rem' }} onClick={() => { navigator.clipboard.writeText(selectedReq.generated_code); alert('Code copied to clipboard!') }}>
                          📋 Copy Code
                        </button>
                      </div>
                      <div style={{ position: 'relative' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                          <span style={{ fontSize: '0.75rem', color: '#6e7681' }}>Python · pytest</span>
                          <span style={{ fontSize: '0.75rem', color: '#6e7681' }}>{selectedReq.generated_code.split('\n').length} lines</span>
                        </div>
                        <pre style={{ maxHeight: '400px', overflowY: 'auto', fontSize: '13px', lineHeight: 1.55 }}>
                          {selectedReq.generated_code}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>

                <hr style={{ borderColor: 'var(--border)', margin: '0.25rem 0' }} />

                {/* ── STEP 3: Execution Results ── */}
                <div>
                  <div className={`step-label ${selectedReq.verification_status === 'Pass' ? 'completed' : ''}`}>
                    <span className="step-number">3</span>
                    Test Execution Results
                  </div>
                  <p className="step-description">
                    The generated script is executed in a sandboxed Python environment on the server. A passing result means this requirement is independently verified.
                  </p>

                  {selectedReq.generated_code && (
                    <button
                      className="premium-btn"
                      style={{ justifyContent: 'center', width: '100%', padding: '0.85rem', fontSize: '0.95rem', backgroundColor: 'var(--success)', marginBottom: '0.75rem' }}
                      onClick={handleExecuteTest}
                      disabled={isExecuting}
                    >
                      {isExecuting ? <RefreshCw className="spin" size={18} /> : <Play size={18} />}
                      {isExecuting ? 'Executing Test...' : 'Execute Test'}
                    </button>
                  )}

                  {selectedReq.execution_log && (
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                        <span style={{ fontSize: '0.75rem', color: '#6e7681' }}>Terminal Output</span>
                        {getStatusBadge(selectedReq.verification_status)}
                      </div>
                      <pre style={{
                        maxHeight: '200px',
                        overflowY: 'auto',
                        fontSize: '13px',
                        borderColor: selectedReq.verification_status === 'Pass' ? 'rgba(35, 134, 54, 0.4)' : 'rgba(218, 54, 51, 0.4)'
                      }}>
                        {selectedReq.execution_log}
                      </pre>
                    </div>
                  )}

                  {selectedReq.verification_status === 'Pass' && (
                    <div className="verified-banner" style={{ marginTop: '0.75rem' }}>
                      <span style={{ fontSize: '1.4rem' }}>✅</span>
                      <div>
                        <div style={{ fontWeight: 700 }}>REQUIREMENT VERIFIED</div>
                        <div style={{ fontSize: '0.8rem', color: '#8b949e', fontWeight: 400 }}>This requirement has been independently verified through automated testing.</div>
                      </div>
                    </div>
                  )}

                  {selectedReq.verification_status === 'Fail' && (
                    <div style={{ marginTop: '0.75rem', padding: '1rem 1.25rem', background: 'rgba(218, 54, 51, 0.1)', border: '1px solid rgba(218, 54, 51, 0.3)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <span style={{ fontSize: '1.4rem' }}>❌</span>
                      <div>
                        <div style={{ fontWeight: 700, color: '#ff7b72' }}>TEST FAILED</div>
                        <div style={{ fontSize: '0.8rem', color: '#8b949e' }}>The generated test did not pass. Review the terminal output above and click "Regenerate" to try a different approach.</div>
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}

            {/* Non-Test Methods: Show closure explanation */}
            {selectedReq.status !== 'Pending' && selectedReq.verification_method?.toLowerCase() !== 'test' && (
              <div style={{ padding: '1rem', backgroundColor: 'rgba(210, 153, 34, 0.08)', border: '1px solid rgba(210, 153, 34, 0.2)', borderRadius: '8px', fontSize: '0.9rem', color: '#c9d1d9', lineHeight: 1.6 }}>
                <strong style={{ color: '#d29922' }}>No executable test required.</strong><br />
                This requirement is verified via <strong>{selectedReq.verification_method}</strong> — a manual or document-based process that does not require automated testing. The AI has provided its rationale above explaining why this method was selected.
              </div>
            )}

          </div>
        )}
      </section>

      {/* Native keyframe for spinner */}
      <style dangerouslySetInnerHTML={{
        __html: `
        @keyframes spin { 100% { transform: rotate(360deg); } }
        .spin { animation: spin 1s linear infinite; }
      `}} />

      {/* Delete Project Confirmation Modal */}
      {showDeleteModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.75)', zIndex: 1000,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          backdropFilter: 'blur(4px)'
        }}>
          <div className="glass-panel" style={{
            width: '520px', maxWidth: '90vw', padding: '2rem', position: 'relative'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '8px', backgroundColor: 'rgba(218, 54, 51, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--danger)', flexShrink: 0 }}>
                <Trash2 size={20} />
              </div>
              <h2 style={{ fontSize: '1.1rem', color: 'white' }}>Remove Project from Database</h2>
            </div>

            <div style={{ padding: '1rem', backgroundColor: 'rgba(218, 54, 51, 0.08)', border: '1px solid rgba(218, 54, 51, 0.3)', borderRadius: '6px', marginBottom: '1.5rem' }}>
              <p style={{ fontSize: '0.9rem', color: '#f0c9c9', fontWeight: 600, marginBottom: '0.5rem' }}>
                ⚠️ You are about to permanently delete:
              </p>
              <p style={{ fontSize: '0.9rem', color: 'white', fontWeight: 600, marginBottom: '0.75rem', wordBreak: 'break-word' }}>
                "{selectedProject}"
              </p>
              <ul style={{ fontSize: '0.85rem', color: '#c9d1d9', paddingLeft: '1.25rem', lineHeight: 1.8 }}>
                <li>All <strong>parsed requirements</strong> extracted from this PDF</li>
                <li>All <strong>AI-generated verification strategies</strong> and rationale</li>
                <li>All <strong>generated Pytest scripts</strong> associated with this project</li>
                <li>All <strong>execution logs</strong> and test results</li>
              </ul>
            </div>

            <p style={{ fontSize: '0.85rem', color: '#8b949e', marginBottom: '1.5rem', lineHeight: 1.5 }}>
              This action is <strong style={{ color: 'var(--danger)' }}>permanent and cannot be undone</strong>. The original PDF file will not be affected—only the database records will be removed. You can always re-upload and re-process the PDF later.
            </p>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
              <button
                className="secondary-btn"
                onClick={() => setShowDeleteModal(false)}
                style={{ padding: '0.75rem 1.5rem' }}
              >
                Cancel
              </button>
              <button
                className="secondary-btn"
                onClick={confirmDeleteProject}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: 'rgba(218, 54, 51, 0.2)',
                  color: 'var(--danger)',
                  borderColor: 'var(--danger)',
                  fontWeight: 600
                }}
              >
                Yes, Permanently Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
