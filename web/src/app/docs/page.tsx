'use client'

import { useState, useEffect } from 'react'
import { Book, FileText, Download, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

type DocItem = {
    id: string
    title: string
}

export default function Docs() {
    const [docs, setDocs] = useState<DocItem[]>([])
    const [activeDoc, setActiveDoc] = useState<string>('')
    const [content, setContent] = useState<string>('')
    const [isLoadingList, setIsLoadingList] = useState(true)
    const [isLoadingDoc, setIsLoadingDoc] = useState(false)

    useEffect(() => {
        const fetchDocs = async () => {
            try {
                const res = await fetch(`${API_BASE}/api/docs`)
                if (!res.ok) {
                    console.error("HTTP Error:", res.status, res.statusText)
                    throw new Error(`HTTP Error: ${res.status}`)
                }
                const data = await res.json()
                console.log("Raw docs data from API:", data)
                setDocs(data)
                if (data.length > 0) {
                    setActiveDoc(data[0].id)
                }
            } catch (err) {
                console.error("Failed to fetch documents list:", err)
            } finally {
                setIsLoadingList(false)
            }
        }
        fetchDocs()
    }, [])

    useEffect(() => {
        if (!activeDoc) return

        const fetchContent = async () => {
            setIsLoadingDoc(true)
            setContent('')
            try {
                const res = await fetch(`${API_BASE}/api/docs/${activeDoc}`)
                const data = await res.json()
                if (res.ok) {
                    setContent(data.content || '')
                } else {
                    setContent('Failed to load document content.')
                }
            } catch (err) {
                console.error("Failed to fetch markdown:", err)
                setContent('Error loading document.')
            } finally {
                setIsLoadingDoc(false)
            }
        }
        fetchContent()
    }, [activeDoc])

    const handleDownload = () => {
        if (!content || !activeDoc) return
        const blob = new Blob([content], { type: 'text/markdown' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = activeDoc
        a.click()
    }

    return (
        <div className="content-area" style={{ flexDirection: 'column' }}>
            <div style={{ marginBottom: '2rem' }}>
                <h2 style={{ marginBottom: '0.5rem', color: 'white', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <Book size={24} color="var(--primary)" /> Project Knowledge Base
                </h2>
                <p style={{ color: '#8b949e', fontSize: '0.9rem', maxWidth: '800px', lineHeight: 1.5 }}>
                    Access the complete repository of technical documentation, architectural guides, and system manuals. The Agent Cortex uses these documents as reference material when brainstorming verification methods for your complex requirements.
                </p>
            </div>

            <div style={{ display: 'flex', gap: '2rem', flex: 1, height: 'calc(100vh - 150px)' }}>
                {/* Navigation Sidebar */}
                <div className="glass-panel" style={{ width: '300px', display: 'flex', flexDirection: 'column', padding: '1rem', overflowY: 'auto' }}>
                    <h3 style={{ fontSize: '0.85rem', color: '#8b949e', textTransform: 'uppercase', marginBottom: '1rem', paddingLeft: '0.5rem' }}>
                        Available Documents
                    </h3>

                    {isLoadingList ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#8b949e', padding: '1rem' }}>
                            <Loader2 className="spin" size={16} /> Loading docs...
                        </div>
                    ) : docs.length === 0 ? (
                        <div style={{ color: '#8b949e', padding: '1rem', fontSize: '0.85rem' }}>No documentation found in root project directory.</div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            {docs.map(doc => (
                                <button
                                    key={doc.id}
                                    onClick={() => setActiveDoc(doc.id)}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.75rem',
                                        padding: '0.75rem',
                                        border: 'none',
                                        backgroundColor: activeDoc === doc.id ? 'rgba(88, 166, 255, 0.1)' : 'transparent',
                                        color: activeDoc === doc.id ? 'var(--primary)' : 'var(--foreground)',
                                        borderRadius: '6px',
                                        textAlign: 'left',
                                        cursor: 'pointer',
                                        transition: 'background-color 0.2s',
                                        fontWeight: activeDoc === doc.id ? 600 : 400
                                    }}
                                >
                                    <FileText size={18} />
                                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{doc.title}</span>
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Document Viewer */}
                <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                    <div style={{ padding: '1.25rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h3 style={{ fontSize: '1.1rem', color: 'white', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            {activeDoc || 'Select a document'}
                        </h3>
                        <button
                            className="secondary-btn"
                            onClick={handleDownload}
                            disabled={!content}
                            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
                            <Download size={16} /> Download Source
                        </button>
                    </div>

                    <div style={{ flex: 1, padding: '2rem', overflowY: 'auto' }} className="markdown-body">
                        {isLoadingDoc ? (
                            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#8b949e' }}>
                                <Loader2 className="spin" size={32} style={{ marginBottom: '1rem' }} />
                            </div>
                        ) : content ? (
                            <ReactMarkdown>{content}</ReactMarkdown>
                        ) : (
                            <div style={{ color: '#8b949e', textAlign: 'center', marginTop: '4rem' }}>
                                <Book size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
                                <p>No content to display.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
