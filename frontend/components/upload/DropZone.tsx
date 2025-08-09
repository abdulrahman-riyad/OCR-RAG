'use client'

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Image as ImageIcon } from 'lucide-react'

interface DropZoneProps {
  onFilesAccepted: (files: File[]) => void
}

export default function DropZone({ onFilesAccepted }: DropZoneProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    onFilesAccepted(acceptedFiles)
  }, [onFilesAccepted])

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.webp'],
      'application/pdf': ['.pdf']
    },
    multiple: true,
    maxSize: 10 * 1024 * 1024 // 10MB
  })

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200 ease-in-out
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          }
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center">
          <Upload className={`w-12 h-12 mb-4 ${
            isDragActive ? 'text-blue-500' : 'text-gray-400'
          }`} />
          
          {isDragActive ? (
            <p className="text-lg font-medium text-blue-600">
              Drop your files here...
            </p>
          ) : (
            <>
              <p className="text-lg font-medium text-gray-700 mb-1">
                Drag & drop your notes here
              </p>
              <p className="text-sm text-gray-500">
                or click to browse files
              </p>
            </>
          )}
          
          <p className="text-xs text-gray-400 mt-4">
            Supports JPG, PNG, WebP, PDF (max 10MB)
          </p>
        </div>
      </div>

      {acceptedFiles.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2">
            Ready to upload:
          </h3>
          <ul className="space-y-1">
            {acceptedFiles.map((file, index) => (
              <li key={index} className="flex items-center text-sm text-gray-600">
                <ImageIcon className="w-4 h-4 mr-2 text-gray-400" />
                {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}