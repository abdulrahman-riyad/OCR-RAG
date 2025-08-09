'use client'

import { useRouter } from 'next/navigation'
import { Upload, Search, FileText } from 'lucide-react'

export default function HomePage() {
  const router = useRouter()

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          OCR Notes Digitizer
        </h1>
        <p className="text-xl text-gray-600">
          Transform your handwritten notes into searchable, structured PDFs
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="card text-center">
          <Upload className="w-12 h-12 mx-auto mb-4 text-blue-600" />
          <h3 className="text-lg font-semibold mb-2">Upload</h3>
          <p className="text-gray-600 text-sm">
            Drag and drop your handwritten notes or photos
          </p>
        </div>
        
        <div className="card text-center">
          <FileText className="w-12 h-12 mx-auto mb-4 text-green-600" />
          <h3 className="text-lg font-semibold mb-2">Process</h3>
          <p className="text-gray-600 text-sm">
            AI extracts text, equations, and diagrams
          </p>
        </div>
        
        <div className="card text-center">
          <Search className="w-12 h-12 mx-auto mb-4 text-purple-600" />
          <h3 className="text-lg font-semibold mb-2">Search</h3>
          <p className="text-gray-600 text-sm">
            Find any information instantly
          </p>
        </div>
      </div>

      <div className="text-center">
        <button
          onClick={() => router.push('/upload')}
          className="btn-primary text-lg px-8 py-3"
        >
          Start Uploading Notes
        </button>
      </div>
    </div>
  )
}