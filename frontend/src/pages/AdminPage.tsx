import { useState, useEffect } from 'react'
import { documentService } from '../services/documentService'
import toast from 'react-hot-toast'
import { useDropzone } from 'react-dropzone'
import DocumentList from '../components/admin/DocumentList'
import DocumentPreview from '../components/admin/DocumentPreview'

export default function AdminPage() {
  const [documents, setDocuments] = useState<any[]>([])
  const [selectedDocument, setSelectedDocument] = useState<any>(null)
  const [isUploading, setIsUploading] = useState(false)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const response = await documentService.getDocuments()
      setDocuments(response.documents)
    } catch (error) {
      toast.error('Failed to load documents')
    }
  }

  const onDrop = async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      setIsUploading(true)
      try {
        await documentService.uploadDocument(file)
        toast.success(`Uploaded: ${file.name}`)
        toast.success('Processing document...')
        
        // Wait a moment for processing to complete
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Reload documents
        await loadDocuments()
      } catch (error) {
        toast.error(`Failed to upload: ${file.name}`)
      } finally {
        setIsUploading(false)
      }
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    multiple: true,
  })

  const handleSelectDocument = async (doc: any) => {
    try {
      // API returns lowercase status values: ocr_completed, preview, committed
      const status = doc.status.toLowerCase()
      if (status === 'ocr_completed' || status === 'preview' || status === 'committed') {
        const preview = await documentService.getDocumentPreview(doc.id)
        console.log('📄 Preview data received:', preview)
        console.log('📄 Pages count:', preview.pages?.length)
        setSelectedDocument({ ...doc, preview })
      } else {
        setSelectedDocument(doc)
      }
    } catch (error) {
      console.error('❌ Preview load error:', error)
      toast.error('Failed to load document preview')
    }
  }

  const handleCommit = async (documentId: string) => {
    try {
      await documentService.commitDocument(documentId)
      toast.success('Document committed successfully')
      await loadDocuments()
      setSelectedDocument(null)
    } catch (error) {
      toast.error('Failed to commit document')
    }
  }

  return (
    <div className="h-full flex">
      <div className="w-64 border-r border-gray-200 p-3 overflow-y-auto bg-gray-50">
        <h2 className="text-lg font-bold mb-3">Documents</h2>
        
        {/* Upload area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer mb-3 ${
            isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'
          }`}
        >
          <input {...getInputProps()} />
          {isUploading ? (
            <p className="text-sm">Uploading...</p>
          ) : isDragActive ? (
            <p className="text-sm">Drop files here...</p>
          ) : (
            <div>
              <svg className="mx-auto h-8 w-8 text-gray-400 mb-2" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <p className="text-xs text-gray-600">PDF, DOCX, or TXT</p>
              <p className="text-xs text-gray-400 mt-1">Drop or click to upload</p>
            </div>
          )}
        </div>

        {/* Document list */}
        <DocumentList
          documents={documents}
          selectedDocument={selectedDocument}
          onSelect={handleSelectDocument}
        />
      </div>

      <div className="flex-1 overflow-y-auto">
        {selectedDocument ? (
          <DocumentPreview
            document={selectedDocument}
            onCommit={handleCommit}
            onClose={() => setSelectedDocument(null)}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            <p>Select a document to preview</p>
          </div>
        )}
      </div>
    </div>
  )
}

