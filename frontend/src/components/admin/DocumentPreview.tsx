import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { toast } from 'react-hot-toast'
import api from '../../lib/api'

interface Props {
  document: any
  onCommit: (documentId: string, correctedText?: string) => void
  onClose: () => void
}

export default function DocumentPreview({ document, onCommit, onClose }: Props) {
  const [correctedText, setCorrectedText] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [language, setLanguage] = useState<string>('auto')

  useEffect(() => {
    // Initialize corrected text from OCR
    console.log('🔍 DocumentPreview useEffect:', {
      hasDocument: !!document,
      hasPreview: !!document?.preview,
      pagesCount: document?.preview?.pages?.length,
      firstPageSample: document?.preview?.pages?.[0]?.ocr_text?.substring(0, 100)
    })
    
    if (document?.preview?.pages) {
      const allText = document.preview.pages
        .map((page: any) => {
          return page.corrected_text || page.ocr_text || ''
        })
        .join('\n\n---\n\n')
      console.log('📝 Setting corrected text, length:', allText.length)
      setCorrectedText(allText)
    }
  }, [document])

  const handleSaveCorrections = async () => {
    setIsSaving(true)
    try {
      // Save corrected text to backend using API client
      await api.post(`/admin/documents/${document.id}/corrected-text`, { 
        corrected_text: correctedText,
        language: language 
      })
      
      toast.success('Corrections saved successfully')
      setIsEditing(false)
    } catch (error) {
      console.error('Save error:', error)
      toast.error('Failed to save corrections')
    } finally {
      setIsSaving(false)
    }
  }

  const handleCommitToVectorDB = async () => {
    try {
      await onCommit(document.id, correctedText)
    } catch (error) {
      toast.error('Failed to commit to vector DB')
    }
  }

  // API returns lowercase status values
  const status = document.status?.toLowerCase() || ''
  const canCommit = status === 'ocr_completed' || status === 'preview'
  
  // Detect if text contains RTL characters (Arabic, Hebrew, etc.)
  const isRTL = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/.test(correctedText)

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 p-4 flex items-center justify-between bg-gray-50">
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-bold text-gray-900 truncate">
            {document.original_filename}
          </h2>
          <div className="flex items-center gap-3 mt-1">
            <span className={`text-xs px-2 py-1 rounded-full ${
              status === 'committed' ? 'bg-green-100 text-green-800' :
              status === 'ocr_completed' ? 'bg-blue-100 text-blue-800' :
              'bg-yellow-100 text-yellow-800'
            }`}>
              {document.status}
            </span>
            <span className="text-xs text-gray-500">{document.total_pages} pages</span>
            
            {/* Language selector */}
            <select 
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="text-xs border border-gray-300 rounded px-2 py-1"
            >
              <option value="auto">Auto-detect</option>
              <option value="en">English</option>
              <option value="ar">العربية (Arabic)</option>
              <option value="fr">Français</option>
              <option value="es">Español</option>
              <option value="de">Deutsch</option>
              <option value="zh">中文</option>
              <option value="pt">Português</option>
            </select>
          </div>
        </div>
        
        <div className="flex items-center gap-2 ml-4">
          {isEditing ? (
            <>
              <button
                onClick={handleSaveCorrections}
                disabled={isSaving}
                className="px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
              >
                {isSaving ? 'Saving...' : 'Save Corrections'}
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="px-3 py-1.5 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setIsEditing(true)}
                className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Edit Text
              </button>
              {canCommit && (
                <button
                  onClick={handleCommitToVectorDB}
                  className="px-3 py-1.5 text-sm bg-primary-600 text-white rounded hover:bg-primary-700"
                >
                  Commit to Vector DB
                </button>
              )}
            </>
          )}
          <button
            onClick={onClose}
            className="px-3 py-1.5 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          >
            Close
          </button>
        </div>
      </div>

      {/* Split view content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Original Document Preview */}
        <div className="w-1/2 border-r border-gray-200 overflow-y-auto bg-gray-100 p-4">
          <div className="sticky top-0 bg-gray-100 pb-2 mb-2 z-10">
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
              Original Document
            </h3>
          </div>
          
          {document.preview?.pages ? (
            <div className="space-y-4">
              {document.preview.pages.map((page: any) => (
                <div key={page.page_number} className="bg-white rounded-lg shadow-sm overflow-hidden">
                  <div className="bg-gray-50 px-3 py-2 border-b border-gray-200">
                    <span className="text-xs font-medium text-gray-600">
                      Page {page.page_number}
                      {page.ocr_confidence && (
                        <span className="ml-2 text-gray-400">
                          • Confidence: {(page.ocr_confidence * 100).toFixed(0)}%
                        </span>
                      )}
                    </span>
                  </div>
                  {page.image_url ? (
                    <img
                      src={page.image_url}
                      alt={`Page ${page.page_number}`}
                      className="w-full"
                    />
                  ) : (
                    <div className="p-4 bg-gray-50">
                      <div className="text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed">
                        {page.ocr_text || page.corrected_text || 'No text extracted'}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-400">
                <svg className="mx-auto h-12 w-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-sm">No preview available</p>
                <p className="text-xs mt-1">Status: {document.status}</p>
              </div>
            </div>
          )}
        </div>

        {/* Right: AI-Extracted Text (Editable Markdown) */}
        <div className="w-1/2 overflow-y-auto p-4">
          <div className="sticky top-0 bg-white pb-2 mb-2 z-10">
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
              AI-Extracted Text {isEditing && <span className="text-blue-600">(Editing)</span>}
            </h3>
            <p className="text-xs text-gray-500 mt-1">
              Review and correct the extracted text before committing to vector database
            </p>
          </div>

          {isEditing ? (
            <textarea
              value={correctedText}
              onChange={(e) => setCorrectedText(e.target.value)}
              className={`w-full h-full min-h-[600px] p-4 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                isRTL ? 'text-right' : 'text-left'
              }`}
              dir={isRTL ? 'rtl' : 'ltr'}
              style={{ 
                lineHeight: '1.6',
                fontFamily: isRTL ? 'Arial, sans-serif' : 'monospace'
              }}
              placeholder="Edit the extracted text here..."
            />
          ) : (
            <div 
              className={`prose prose-sm max-w-none ${isRTL ? 'text-right' : 'text-left'}`}
              dir={isRTL ? 'rtl' : 'ltr'}
              style={{
                fontFamily: isRTL ? 'Arial, sans-serif' : 'inherit'
              }}
            >
              <ReactMarkdown>{correctedText || 'No text extracted yet.'}</ReactMarkdown>
            </div>
          )}

          {/* Helper text */}
          {document.preview?.pages && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-xs text-blue-800">
                <strong>💡 Tip:</strong> Review the AI-extracted text carefully. Compare it with the original document on the left. 
                Make any necessary corrections, then save and commit to the vector database.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
