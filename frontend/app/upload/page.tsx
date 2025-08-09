'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import DropZone from '@/components/upload/DropZone'
import ProcessingStatus from '@/components/upload/ProcessingStatus'
import { uploadFiles, processDocument } from '@/lib/api-client'

export default function UploadPage() {
  const router = useRouter()
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([])
  const [processing, setProcessing] = useState(false)
  const [currentStatus, setCurrentStatus] = useState('')

  const handleFilesAccepted = async (files: File[]) => {
    setProcessing(true)
    setCurrentStatus('Uploading files...')

    try {
      // Upload files
      const uploadResults = await uploadFiles(files)
      setUploadedFiles(uploadResults)
      
      // Process each uploaded file
      for (const result of uploadResults) {
        if (result.document_id) {
          setCurrentStatus(`Processing ${result.filename}...`)
          await processDocument(result.document_id)
        }
      }
      
      setCurrentStatus('All files processed!')
      setTimeout(() => {
        router.push('/documents')
      }, 2000)
      
    } catch (error) {
      console.error('Error:', error)
      setCurrentStatus('Error processing files')
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Upload Your Notes</h1>
      
      {!processing ? (
        <DropZone onFilesAccepted={handleFilesAccepted} />
      ) : (
        <ProcessingStatus 
          status={currentStatus}
          files={uploadedFiles}
        />
      )}
      
      <div className="mt-8 card">
        <h2 className="text-lg font-semibold mb-4">Tips for best results:</h2>
        <ul className="list-disc list-inside space-y-2 text-gray-600">
          <li>Use good lighting when taking photos</li>
          <li>Ensure text is clearly visible</li>
          <li>Avoid blurry or angled shots</li>
          <li>Upload JPG, PNG, or PDF files</li>
        </ul>
      </div>
    </div>
  )
}