import type { Metadata } from 'next'
import './globals.css'
import { Sidebar, TopNav } from '../components/Navigation'

export const metadata: Metadata = {
  title: 'ASV: Agentic Systems Verifier',
  description: 'Automating the Systems Engineering V-Model using Agentic AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <div className="app-layout">
          {/* Main Sidebar Menu */}
          <Sidebar />

          {/* Main Content Area */}
          <main className="main-content">
            {/* Top Navigation Bar */}
            <TopNav />

            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
