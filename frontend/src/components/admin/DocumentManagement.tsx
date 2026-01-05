import { useState, useEffect } from 'react'
import { documentService } from '../../services/documentService'
import toast from 'react-hot-toast'
import { useDropzone } from 'react-dropzone'
import DocumentList from './DocumentList'
import DocumentPreview from './DocumentPreview'

export default function DocumentManagement() {
  const [documents, setDocuments] = useState<any[]>([])
  const [selectedDocument, setSelectedDocument] = useState<any>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      setIsLoading(true)
      const response = await documentService.getDocuments()
      setDocuments(response.documents)
    } catch (error) {
      console.error('Failed to load documents:', error)
      toast.error('Failed to load documents')
    } finally {
      setIsLoading(false)
    }
  }

  const onDrop = async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      setIsUploading(true)
      try {
        await documentService.uploadDocument(file)
        toast.success(`Uploaded: ${file.name}`)
        toast.success('Processing document...')
        
        // Wait a moment for processing to start
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Reload documents
        await loadDocuments()
      } catch (error) {
        console.error('Upload error:', error)
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
      const status = doc.status.toLowerCase()
      if (status === 'ocr_completed' || status === 'preview' || status === 'committed') {
        const preview = await documentService.getDocumentPreview(doc.id)
        setSelectedDocument({ ...doc, preview })
      } else {
        setSelectedDocument(doc)
      }
    } catch (error) {
      console.error('Preview load error:', error)
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
      console.error('Commit error:', error)
      toast.error('Failed to commit document')
    }
  }

  return (
    <div className="h-full flex">
      {/* Documents sidebar */}
      <div className="w-80 border-r border-gray-200 p-4 overflow-y-auto bg-gray-50">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">Documents</h2>
          <button
            onClick={loadDocuments}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            title="Refresh"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
        
        {/* Upload area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer mb-4 transition-colors ${
            isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'
          }`}
        >
          <input {...getInputProps()} />
          {isUploading ? (
            <div className="flex flex-col items-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mb-2"></div>
              <p className="text-sm text-gray-600">Uploading...</p>
            </div>
          ) : isDragActive ? (
            <p className="text-sm text-primary-600">Drop files here...</p>
          ) : (
            <div>
              <svg className="mx-auto h-10 w-10 text-gray-400 mb-2" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <p className="text-sm text-gray-600 font-medium">Upload Documents</p>
              <p className="text-xs text-gray-500 mt-1">PDF, DOCX, or TXT</p>
              <p className="text-xs text-gray-400 mt-1">Drop or click to upload</p>
            </div>
          )}
        </div>

        {/* Document list */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mb-2"></div>
            <p className="text-sm text-gray-600">Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-8">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-sm text-gray-600">No documents yet</p>
            <p className="text-xs text-gray-500 mt-1">Upload your first document above</p>
          </div>
        ) : (
          <DocumentList
            documents={documents}
            selectedDocument={selectedDocument}
            onSelect={handleSelectDocument}
          />
        )}
      </div>

      {/* Preview area */}
      <div className="flex-1 overflow-y-auto bg-white">
        {selectedDocument ? (
          <DocumentPreview
            document={selectedDocument}
            onCommit={handleCommit}
            onClose={() => setSelectedDocument(null)}
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <svg className="h-20 w-20 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-lg font-medium">No document selected</p>
            <p className="text-sm mt-1">Select a document from the list to preview</p>
          </div>
        )}
      </div>
    </div>
  )
}

