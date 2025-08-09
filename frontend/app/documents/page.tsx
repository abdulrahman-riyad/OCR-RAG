'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { FileText, Trash2, Eye } from 'lucide-react'
import DocumentCard from '@/components/documents/DocumentCard'
import { getDocuments, deleteDocument } from '@/lib/api-client'

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const docs = await getDocuments()
      setDocuments(docs)
    } catch (error) {
      console.error('Error fetching documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return
    
    try {
      await deleteDocument(documentId)
      await fetchDocuments()
    } catch (error) {
      console.error('Error deleting document:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-gray-500">Loading documents...</p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Your Documents</h1>
        <Link href="/upload" className="btn-primary">
          Upload New
        </Link>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 mb-4">No documents yet</p>
          <Link href="/upload" className="btn-primary">
            Upload your first document
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.map((doc) => (
            <DocumentCard
              key={doc.id}
              document={doc}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  )
}