interface Props {
  documents: any[]
  selectedDocument: any
  onSelect: (doc: any) => void
}

export default function DocumentList({ documents, selectedDocument, onSelect }: Props) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMMITTED':
        return 'bg-green-100 text-green-800'
      case 'OCR_COMPLETED':
      case 'PREVIEW':
        return 'bg-blue-100 text-blue-800'
      case 'OCR_PROCESSING':
        return 'bg-yellow-100 text-yellow-800'
      case 'OCR_FAILED':
      case 'FAILED':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.id}
          onClick={() => onSelect(doc)}
          className={`card cursor-pointer hover:shadow-md transition-shadow ${
            selectedDocument?.id === doc.id ? 'ring-2 ring-primary-500' : ''
          }`}
        >
          <h3 className="text-sm font-medium text-gray-900 truncate">
            {doc.original_filename}
          </h3>
          <div className="mt-2 flex items-center justify-between">
            <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(doc.status)}`}>
              {doc.status}
            </span>
            {doc.total_pages && (
              <span className="text-xs text-gray-500">
                {doc.total_pages} pages
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {new Date(doc.created_at).toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  )
}

