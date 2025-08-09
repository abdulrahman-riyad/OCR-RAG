interface PDFViewerProps {
  pdfUrl: string
}

export default function PDFViewer({ pdfUrl }: PDFViewerProps) {
  return (
    <div className="w-full h-[600px] border rounded-lg overflow-hidden">
      <iframe
        src={pdfUrl}
        className="w-full h-full"
        title="PDF Viewer"
      />
    </div>
  )
}