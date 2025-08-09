import Link from 'next/link'
import { Home, Upload, FileText, Search } from 'lucide-react'

export default function Navigation() {
  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="font-bold text-xl text-gray-900">
            OCR Notes
          </Link>
          
          <div className="flex gap-6">
            <Link 
              href="/" 
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <Home size={20} />
              <span className="hidden md:inline">Home</span>
            </Link>
            
            <Link 
              href="/upload" 
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <Upload size={20} />
              <span className="hidden md:inline">Upload</span>
            </Link>
            
            <Link 
              href="/documents" 
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <FileText size={20} />
              <span className="hidden md:inline">Documents</span>
            </Link>
            
            <Link 
              href="/search" 
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <Search size={20} />
              <span className="hidden md:inline">Search</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}