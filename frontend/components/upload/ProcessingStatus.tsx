import { CheckCircle, XCircle, Loader2 } from 'lucide-react'

interface ProcessingStatusProps {
  status: string
  files: any[]
}

export default function ProcessingStatus({ status, files }: ProcessingStatusProps) {
  return (
    <div className="card">
      <div className="flex items-center justify-center mb-6">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
      
      <h2 className="text-xl font-semibold text-center mb-4">
        Processing Your Documents
      </h2>
      
      <p className="text-center text-gray-600 mb-6">
        {status}
      </p>
      
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <span className="text-sm font-medium">{file.filename}</span>
              {file.error ? (
                <XCircle className="w-5 h-5 text-red-500" />
              ) : file.document_id ? (
                <CheckCircle className="w-5 h-5 text-green-500" />
              ) : (
                <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
              )}
            </div>
          ))}
        </div>
      )}
      
      <div className="mt-6 text-center text-sm text-gray-500">
        This may take a few moments depending on the size and number of files.
      </div>
    </div>
  )
}