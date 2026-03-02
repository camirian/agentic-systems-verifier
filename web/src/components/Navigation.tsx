'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Rocket, ShieldCheck, FileText, Database, BookOpen, X } from 'lucide-react'

export function Sidebar() {
    const pathname = usePathname()

    const navItems = [
        { name: 'Verification Matrix', href: '/', icon: Rocket },
        { name: 'Project Intelligence', href: '/projects', icon: Database },
        { name: 'Documentation', href: '/docs', icon: FileText },
    ]

    return (
        <aside className="sidebar">
            <div style={{ padding: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem', borderBottom: '1px solid var(--border)' }}>
                <ShieldCheck size={28} color="var(--primary)" />
                <div>
                    <h1 style={{ fontSize: '1.2rem', fontWeight: 600 }}>ASV</h1>
                    <p style={{ fontSize: '0.75rem', color: '#8b949e' }}>Mission Control</p>
                </div>
            </div>

            <nav style={{ padding: '1.5rem 1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {navItems.map((item) => {
                    const isActive = pathname === item.href
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '1rem',
                                padding: '0.75rem',
                                borderRadius: '6px',
                                backgroundColor: isActive ? 'rgba(88, 166, 255, 0.1)' : 'transparent',
                                color: isActive ? 'var(--foreground)' : '#8b949e',
                                transition: 'all 0.2s'
                            }}
                        >
                            <item.icon size={18} />
                            <span>{item.name}</span>
                        </Link>
                    )
                })}
            </nav>

            <div style={{ marginTop: 'auto', padding: '1.5rem 1.5rem 2.5rem', borderTop: '1px solid var(--border)', fontSize: '0.7rem', color: '#484f58' }}>
                <p style={{ marginBottom: '0.35rem' }}>© 2026 Agentic Systems Verifier</p>
                <p style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    Built by{' '}
                    <a href="https://github.com/camirian" target="_blank" rel="noopener noreferrer" style={{ color: '#8b949e', textDecoration: 'none', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                        camirian
                        <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" /></svg>
                    </a>
                </p>
            </div>
        </aside>
    )
}

export function TopNav() {
    const pathname = usePathname()
    const [isHelpOpen, setIsHelpOpen] = useState(false)

    const getPageTitle = () => {
        if (pathname === '/projects') return 'Project Intelligence'
        if (pathname === '/docs') return 'Documentation'
        return 'Traceability Matrix'
    }

    return (
        <>
            <header className="top-nav">
                <h2 style={{ fontSize: '1.1rem', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ color: '#8b949e' }}>Projects /</span> {getPageTitle()}
                </h2>
                <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <button
                        className="secondary-btn"
                        style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)', borderColor: 'rgba(88, 166, 255, 0.3)' }}
                        onClick={() => setIsHelpOpen(true)}
                        title="Learn how to use this application step by step"
                    >
                        <BookOpen size={16} />
                        <span>How It Works</span>
                    </button>
                </div>
            </header>

            {/* Help Modal */}
            {isHelpOpen && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.7)', zIndex: 1000,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    backdropFilter: 'blur(4px)'
                }}>
                    <div className="glass-panel" style={{
                        width: '600px', maxWidth: '90vw', padding: '2rem', position: 'relative'
                    }}>
                        <button
                            onClick={() => setIsHelpOpen(false)}
                            style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', color: '#8b949e', cursor: 'pointer' }}
                        >
                            <X size={24} />
                        </button>
                        <h2 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <ShieldCheck size={24} color="var(--primary)" />
                            How It Works
                        </h2>
                        <p style={{ color: '#8b949e', marginBottom: '2rem', fontSize: '0.9rem' }}>
                            ASV automates the Systems Engineering V-Model. Upload a specification PDF and watch the AI extract requirements, determine verification methods, and generate executable test scripts—all in three steps.
                        </p>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                            <div style={{ display: 'flex', gap: '1rem' }}>
                                <div style={{ width: '40px', height: '40px', borderRadius: '8px', backgroundColor: 'rgba(88, 166, 255, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)', flexShrink: 0, fontWeight: 700 }}>
                                    1
                                </div>
                                <div>
                                    <h3 style={{ fontSize: '1rem', marginBottom: '0.25rem', color: 'white' }}>Ingest Documents</h3>
                                    <p style={{ fontSize: '0.85rem', color: '#8b949e', lineHeight: 1.5 }}>
                                        Upload your raw PDF specifications in the <strong>Verification Matrix</strong> tab. The Agent Cortex will semantically extract and standardize the requirements.
                                    </p>
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '1rem' }}>
                                <div style={{ width: '40px', height: '40px', borderRadius: '8px', backgroundColor: 'rgba(210, 168, 255, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#d2a8ff', flexShrink: 0, fontWeight: 700 }}>
                                    2
                                </div>
                                <div>
                                    <h3 style={{ fontSize: '1rem', marginBottom: '0.25rem', color: 'white' }}>Brainstorm Strategies</h3>
                                    <p style={{ fontSize: '0.85rem', color: '#8b949e', lineHeight: 1.5 }}>
                                        Select a Pending requirement or click <strong>"Brainstorm All Pending"</strong> to let the AI determine the optimal verification method (Test, Analysis, Inspection) and generate exact test code.
                                    </p>
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '1rem' }}>
                                <div style={{ width: '40px', height: '40px', borderRadius: '8px', backgroundColor: 'rgba(63, 185, 80, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--success)', flexShrink: 0, fontWeight: 700 }}>
                                    3
                                </div>
                                <div>
                                    <h3 style={{ fontSize: '1rem', marginBottom: '0.25rem', color: 'white' }}>Execute & Verify</h3>
                                    <p style={{ fontSize: '0.85rem', color: '#8b949e', lineHeight: 1.5 }}>
                                        Run the generated Pytest scripts against the backend and track your overall progress on the <strong>Project Intelligence</strong> dashboard.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: 'rgba(88, 166, 255, 0.05)', border: '1px solid var(--border)', borderRadius: '6px' }}>
                            <p style={{ fontSize: '0.8rem', color: '#8b949e', lineHeight: 1.6 }}>
                                <strong style={{ color: '#c9d1d9' }}>Sidebar Pages:</strong><br />
                                <strong>Verification Matrix</strong> — The main workspace. Upload PDFs, view requirements, brainstorm strategies, and execute tests.<br />
                                <strong>Project Intelligence</strong> — Live dashboard tracking verification progress, test coverage metrics, and system logs.<br />
                                <strong>Documentation</strong> — Browse the project's technical documentation and architectural guides.
                            </p>
                        </div>

                        <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end' }}>
                            <button className="primary-btn" onClick={() => setIsHelpOpen(false)}>
                                Got it
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}
