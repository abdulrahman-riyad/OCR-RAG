import Link from 'next/link'
import { FileText, ArrowRight } from 'lucide-react'

interface ResultsListProps {
  results: any[]
}

export default function ResultsList({ results }: ResultsListProps) {
  if (results.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No results found. Try a different search term.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-600 mb-4">
        Found {results.length} result{results.length !== 1 ? 's' : ''}
      </p>
      
      {results.map((result) => (
        <div key={result.document_id} className="card hover:shadow-lg transition-shadow">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-gray-400" />
              <h3 className="font-semibold text-gray-900">
                {result.title}
              </h3>
            </div>
            <span className="text-xs text-gray-500">
              Score: {(result.score * 100).toFixed(0)}%
            </span>
          </div>
          
          <p className="text-sm text-gray-600 mb-4">
            {result.snippet}
          </p>
          
          <Link
            href={`/documents/${result.document_id}`}
            className="flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm"
          >
            View Document
            <ArrowRight size={16} />
          </Link>
        </div>
      ))}
    </div>
  )
}