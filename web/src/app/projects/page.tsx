'use client'

import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Activity, Database, AlertCircle, CheckCircle } from 'lucide-react'

type Requirement = {
    id: string
    status: string
    priority: string
    verification_method: string
}

type SystemLog = {
    id: number
    timestamp: string
    level: string
    message: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

// Colors based on Nord Theme
const COLORS = ['#88C0D0', '#4C566A'] // Analyzed vs Pending
const PRIORITY_COLORS: Record<string, string> = {
    Critical: '#BF616A',
    High: '#D08770',
    Medium: '#EBCB8B',
    Low: '#81A1C1'
}
const LEVEL_COLORS: Record<string, string> = {
    INFO: '#88C0D0',
    ANALYSIS: '#A3BE8C',
    WARN: '#EBCB8B',
    ERROR: '#BF616A'
}

export default function Projects() {
    const [requirements, setRequirements] = useState<Requirement[]>([])
    const [logs, setLogs] = useState<SystemLog[]>([])
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [reqRes, logRes] = await Promise.all([
                    fetch(`${API_BASE}/requirements`),
                    fetch(`${API_BASE}/logs`)
                ])
                const reqData = await reqRes.json()
                const logData = await logRes.json()

                setRequirements(reqData)
                setLogs(logData)
            } catch (e) {
                console.error("Failed to fetch data:", e)
            } finally {
                setIsLoading(false)
            }
        }
        fetchData()
    }, [])

    if (isLoading) {
        return <div className="content-area" style={{ justifyContent: 'center', alignItems: 'center' }}>Loading Intelligence Data...</div>
    }

    // --- Calculate Metrics ---
    const total = requirements.length
    const analyzed = requirements.filter(r => r.status === 'Analyzed' || r.status === 'Verified' || r.status === 'Failed').length
    const pending = requirements.filter(r => r.status === 'Pending').length

    const planningProgress = total > 0 ? (analyzed / total) * 100 : 0

    const testCount = requirements.filter(r => r.verification_method?.toLowerCase() === 'test').length
    const nonCodeCount = requirements.filter(r =>
        r.verification_method?.toLowerCase() === 'analysis' ||
        r.verification_method?.toLowerCase() === 'inspection' ||
        r.verification_method?.toLowerCase() === 'demonstration'
    ).length

    // --- Prepare Chart Data ---
    const pieData = [
        { name: 'Analyzed', value: analyzed },
        { name: 'Pending', value: pending }
    ]

    // Group by Method and Priority for Stacked Bar Chart
    const methodPriorities: Record<string, Record<string, number>> = {}
    requirements.forEach(r => {
        const method = r.verification_method || 'Unassigned'
        if (!methodPriorities[method]) {
            methodPriorities[method] = { Critical: 0, High: 0, Medium: 0, Low: 0 }
        }
        const prio = r.priority || 'Medium'
        if (methodPriorities[method][prio] !== undefined) {
            methodPriorities[method][prio]++
        }
    })

    const barData = Object.keys(methodPriorities).map(method => ({
        name: method,
        Critical: methodPriorities[method].Critical,
        High: methodPriorities[method].High,
        Medium: methodPriorities[method].Medium,
        Low: methodPriorities[method].Low,
    }))

    return (
        <div className="content-area" style={{ flexDirection: 'column' }}>
            <div style={{ marginBottom: '2rem' }}>
                <h2 style={{ marginBottom: '0.5rem', color: 'white' }}>Verification Report & Intelligence</h2>
                <p style={{ color: '#8b949e', fontSize: '0.9rem', maxWidth: '800px', lineHeight: 1.5 }}>
                    Track the live verification progress of your ingested specifications. This dashboard aggregates the status of all parsed requirements, calculates the planning progress, and categorizes the automated test generation workloads versus manual inspection workloads.
                </p>
            </div>

            {/* Metrics Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                    <div style={{ color: '#8b949e', fontSize: '0.9rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Activity size={16} /> Planning Progress
                    </div>
                    <div style={{ fontSize: '2rem', fontWeight: 600, color: 'white' }}>{planningProgress.toFixed(0)}%</div>
                    <div style={{ fontSize: '0.8rem', color: '#c9d1d9', marginTop: '0.5rem' }}>Requirements with a Verification Plan</div>
                </div>

                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                    <div style={{ color: '#8b949e', fontSize: '0.9rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Database size={16} /> Tests Identified
                    </div>
                    <div style={{ fontSize: '2rem', fontWeight: 600, color: 'white' }}>{testCount}</div>
                    <div style={{ fontSize: '0.8rem', color: '#c9d1d9', marginTop: '0.5rem' }}>Require automated script generation</div>
                </div>

                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                    <div style={{ color: '#8b949e', fontSize: '0.9rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <CheckCircle size={16} /> Non-Code Verification
                    </div>
                    <div style={{ fontSize: '2rem', fontWeight: 600, color: 'white' }}>{nonCodeCount}</div>
                    <div style={{ fontSize: '0.8rem', color: '#c9d1d9', marginTop: '0.5rem' }}>Verified via Inspection/Analysis</div>
                </div>
            </div>

            {/* Charts Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem', height: '350px', marginBottom: '2rem' }}>
                <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'white' }}>Coverage Status</h3>
                    <div style={{ flex: 1, position: 'relative' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie data={pieData} innerRadius={80} outerRadius={110} dataKey="value" stroke="none">
                                    {pieData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip contentStyle={{ backgroundColor: '#161b22', borderColor: '#30363d', color: 'white' }} />
                            </PieChart>
                        </ResponsiveContainer>
                        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontSize: '2rem', fontWeight: 600, color: 'white' }}>
                            {planningProgress.toFixed(0)}%
                        </div>
                    </div>
                </div>

                <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'white' }}>Test Complexity & Risk</h3>
                    <div style={{ flex: 1 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={barData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                                <XAxis dataKey="name" stroke="#8b949e" />
                                <YAxis stroke="#8b949e" />
                                <Tooltip contentStyle={{ backgroundColor: '#161b22', borderColor: '#30363d', color: 'white' }} />
                                <Legend />
                                <Bar dataKey="Low" stackId="a" fill={PRIORITY_COLORS.Low} />
                                <Bar dataKey="Medium" stackId="a" fill={PRIORITY_COLORS.Medium} />
                                <Bar dataKey="High" stackId="a" fill={PRIORITY_COLORS.High} />
                                <Bar dataKey="Critical" stackId="a" fill={PRIORITY_COLORS.Critical} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Agent Cortex System Logs */}
            <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', flex: 1, minHeight: '400px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h3 style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'white' }}>
                        <AlertCircle size={18} color="var(--primary)" /> Agent Cortex - System Audit Log
                    </h3>
                    <span style={{ fontSize: '0.8rem', color: '#8b949e' }}>Immutable "Flight Data Recorder"</span>
                </div>

                <div style={{ flex: 1, overflowY: 'auto', backgroundColor: '#0d1117', borderRadius: '6px', border: '1px solid var(--border)', padding: '1rem' }}>
                    {logs.map((log) => (
                        <div key={log.id} style={{ display: 'flex', padding: '0.5rem 0', borderBottom: '1px solid #21262d', fontSize: '0.85rem', fontFamily: 'monospace' }}>
                            <div style={{ minWidth: '180px', color: '#6e7681' }}>{new Date(log.timestamp).toLocaleString()}</div>
                            <div style={{ minWidth: '90px', fontWeight: 'bold', color: LEVEL_COLORS[log.level] || '#8b949e' }}>[{log.level}]</div>
                            <div style={{ flex: 1, color: '#c9d1d9', wordBreak: 'break-word' }}>{log.message}</div>
                        </div>
                    ))}
                    {logs.length === 0 && (
                        <div style={{ textAlign: 'center', padding: '2rem', color: '#8b949e' }}>No system logs found.</div>
                    )}
                </div>
            </div>
        </div>
    )
}
