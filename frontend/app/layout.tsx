import './globals.css'
import type { Metadata } from 'next'
import Navigation from '@/components/Navigation'

export const metadata: Metadata = {
  title: 'OCR Notes Digitizer',
  description: 'Convert handwritten notes to searchable documents',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          {children}
        </main>
      </body>
    </html>
  )
}