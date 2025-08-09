import Link from 'next/link'
import { FileText, Trash2, Eye, Clock } from 'lucide-react'

interface DocumentCardProps {
  document: any
  onDelete: (id: string) => void
}

export default function DocumentCard({ document, onDelete }: DocumentCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50'
      case 'processing':
        return 'text-yellow-600 bg-yellow-50'
      case 'failed':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <FileText className="w-8 h-8 text-gray-400" />
        <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(document.status)}`}>
          {document.status}
        </span>
      </div>
      
      <h3 className="font-semibold text-gray-900 mb-2 truncate">
        {document.title}
      </h3>
      
      <div className="flex items-center text-sm text-gray-500 mb-4">
        <Clock className="w-4 h-4 mr-1" />
        {new Date(document.created_at).toLocaleDateString()}
      </div>
      
      {document.ocr_text && (
        <p className="text-sm text-gray-600 mb-4 line-clamp-3">
          {document.ocr_text.substring(0, 150)}...
        </p>
      )}
      
      <div className="flex items-center justify-between">
        <Link
          href={`/documents/${document.id}`}
          className="flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm"
        >
          <Eye size={16} />
          View
        </Link>
        
        <button
          onClick={() => onDelete(document.id)}
          className="flex items-center gap-1 text-red-600 hover:text-red-700 text-sm"
        >
          <Trash2 size={16} />
          Delete
        </button>
      </div>
    </div>
  )
}