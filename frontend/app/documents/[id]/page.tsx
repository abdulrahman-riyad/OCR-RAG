'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Download, FileText, Eye, CheckCircle, XCircle } from 'lucide-react'
import { getDocument, getProcessingStatus } from '@/lib/api-client'

export default function DocumentDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [document, setDocument] = useState<any>(null)
  const [processingStatus, setProcessingStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (params.id) {
      fetchDocumentDetails(params.id as string)
    }
  }, [params.id])

  const fetchDocumentDetails = async (id: string) => {
    try {
      // Get document info
      const doc = await getDocument(id)
      setDocument(doc)
      
      // Get processing status
      const status = await getProcessingStatus(id)
      setProcessingStatus(status)
      
    } catch (error) {
      console.error('Error fetching document:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStepIcon = (status: string) => {
    if (status === 'completed') return <CheckCircle className="w-5 h-5 text-green-500" />
    if (status === 'failed') return <XCircle className="w-5 h-5 text-red-500" />
    return <div className="w-5 h-5 rounded-full bg-gray-300 animate-pulse" />
  }

  const handleDownload = async (fileType: string) => {
    const url = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/process/${params.id}/download/${fileType}`
    window.open(url, '_blank')
  }

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  if (!document) {
    return <div className="text-center py-8">Document not found</div>
  }

  return (
    <div className="max-w-6xl mx-auto">
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft size={20} />
        Back
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h1 className="text-2xl font-bold mb-4">{document.title}</h1>
            
            <div className="flex gap-4 mb-6">
              <button
                onClick={() => handleDownload('pdf')}
                className="btn-primary flex items-center gap-2"
              >
                <Download size={16} />
                Download PDF
              </button>
              
              <button
                onClick={() => handleDownload('text')}
                className="btn-secondary flex items-center gap-2"
              >
                <FileText size={16} />
                Download Text
              </button>
            </div>

            {document.ocr_text && (
              <div>
                <h2 className="text-lg font-semibold mb-3">Extracted Text</h2>
                <div className="bg-gray-50 p-4 rounded-md max-h-96 overflow-y-auto">
                  <pre className="whitespace-pre-wrap font-mono text-sm">
                    {document.ocr_text}
                  </pre>
                </div>
              </div>
            )}
          </div>

          {/* PDF Preview */}
          {processingStatus?.summary?.pdf_url && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-3">PDF Preview</h2>
              <div className="bg-gray-100 rounded-md h-96 flex items-center justify-center">
                <p className="text-gray-500">
                  PDF preview would be displayed here
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar - Processing Status */}
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Processing Status</h2>
            
            {processingStatus && (
              <div className="space-y-3">
                {Object.entries(processingStatus.steps || {}).map(([step, details]: [string, any]) => (
                  <div key={step} className="flex items-start gap-3">
                    {getStepIcon(details.status)}
                    <div className="flex-1">
                      <p className="font-medium capitalize">{step.replace('_', ' ')}</p>
                      <p className="text-sm text-gray-600">
                        {details.status}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Document Info */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Document Info</h2>
            
            <dl className="space-y-2 text-sm">
              <div>
                <dt className="font-medium text-gray-600">Created</dt>
                <dd>{new Date(document.created_at).toLocaleString()}</dd>
              </div>
              
              {processingStatus?.summary && (
                <>
                  <div>
                    <dt className="font-medium text-gray-600">Confidence</dt>
                    <dd>{(processingStatus.summary.confidence * 100).toFixed(1)}%</dd>
                  </div>
                  
                  <div>
                    <dt className="font-medium text-gray-600">Text Length</dt>
                    <dd>{processingStatus.summary.text_length} characters</dd>
                  </div>
                  
                  <div>
                    <dt className="font-medium text-gray-600">Has Math</dt>
                    <dd>{processingStatus.summary.has_math ? 'Yes' : 'No'}</dd>
                  </div>
                </>
              )}
            </dl>
          </div>
        </div>
      </div>
    </div>
  )
}