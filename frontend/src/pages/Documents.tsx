import { useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { UploadCloud, File, Trash2, Loader2 } from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'

type DocumentItem = {
  id: string
  filename: string
  file_size: number
  page_count: number
  status: string
  error_message: string | null
  created_at: string
  updated_at: string | null
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function Documents() {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Fetch documents
  const { data: docs = [], isLoading, error: fetchError } = useQuery<DocumentItem[]>({
    queryKey: ['documents'],
    queryFn: async () => {
      const res = await api.get('/documents/')
      return res.data
    },
  })

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async (file: globalThis.File) => {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (documentId: string) => {
      await api.delete(`/documents/${documentId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      uploadMutation.mutate(file)
      // Reset the input so the same file can be selected again
      e.target.value = ''
    }
  }

  const handleDelete = (docId: string) => {
    deleteMutation.mutate(docId)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
          <p className="text-muted-foreground mt-2">Manage your uploaded knowledge base.</p>
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={handleFileChange}
      />

      <Card>
        <CardContent className="pt-6">
          <div
            className="border-2 border-dashed rounded-lg p-12 text-center hover:bg-muted/50 transition-colors cursor-pointer"
            onClick={handleUploadClick}
          >
            {uploadMutation.isPending ? (
              <div className="flex flex-col items-center">
                <Loader2 className="mx-auto h-12 w-12 text-primary mb-4 animate-spin" />
                <h3 className="text-lg font-medium">Uploading & processing…</h3>
                <p className="text-sm text-muted-foreground mt-2">This may take a moment for large PDFs.</p>
                <div className="mt-6 max-w-sm mx-auto space-y-2">
                  <Progress value={undefined} className="animate-pulse" />
                </div>
              </div>
            ) : (
              <>
                <UploadCloud className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">Click or drag file to this area to upload</h3>
                <p className="text-sm text-muted-foreground mt-2">Supports PDF files up to 25MB.</p>
              </>
            )}
          </div>
          {uploadMutation.isError && (
            <div className="mt-4 rounded-md bg-destructive/10 border border-destructive/20 px-4 py-3 text-sm text-destructive">
              Upload failed: {(uploadMutation.error as any)?.response?.data?.detail || 'Unknown error'}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Uploaded Documents</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : fetchError ? (
            <div className="text-center py-12 text-destructive">
              Failed to load documents. Please try again.
            </div>
          ) : (
            <div className="space-y-4">
              {docs.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className="bg-primary/10 p-2 rounded-lg">
                      <File className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <h4 className="font-medium">{doc.filename}</h4>
                      <p className="text-sm text-muted-foreground">
                        {formatFileSize(doc.file_size)} • {doc.page_count} pages • Uploaded on {new Date(doc.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      doc.status === 'ready'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                        : doc.status === 'error'
                        ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                    }`}>
                      {doc.status}
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive hover:bg-destructive/10 hover:text-destructive"
                      onClick={() => handleDelete(doc.id)}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
              {docs.length === 0 && (
                <div className="text-center py-12 text-muted-foreground">
                  No documents uploaded yet.
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
