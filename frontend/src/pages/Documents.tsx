import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { UploadCloud, File, Trash2 } from 'lucide-react'
import { Progress } from '@/components/ui/progress'

const dummyDocs = [
  { id: '1', name: 'Q3_Financial_Report.pdf', size: '2.4 MB', pages: 45, status: 'ready', date: '2023-10-15' },
  { id: '2', name: 'Employee_Handbook.pdf', size: '1.1 MB', pages: 20, status: 'ready', date: '2023-10-14' },
]

export function Documents() {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [docs, setDocs] = useState(dummyDocs)

  const handleUploadClick = () => {
    setUploading(true)
    let p = 0
    const interval = setInterval(() => {
      p += 10
      setProgress(p)
      if (p >= 100) {
        clearInterval(interval)
        setUploading(false)
        setProgress(0)
        setDocs([{ id: Date.now().toString(), name: 'New_Document.pdf', size: '1.5 MB', pages: 12, status: 'ready', date: new Date().toISOString().split('T')[0] }, ...docs])
      }
    }, 200)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
          <p className="text-muted-foreground mt-2">Manage your uploaded knowledge base.</p>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="border-2 border-dashed rounded-lg p-12 text-center hover:bg-muted/50 transition-colors cursor-pointer" onClick={handleUploadClick}>
            <UploadCloud className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">Click or drag file to this area to upload</h3>
            <p className="text-sm text-muted-foreground mt-2">Supports PDF files up to 25MB.</p>
            {uploading && (
              <div className="mt-6 max-w-sm mx-auto space-y-2">
                <Progress value={progress} />
                <p className="text-sm text-muted-foreground">Uploading... {progress}%</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Uploaded Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {docs.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="bg-primary/10 p-2 rounded-lg">
                    <File className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-medium">{doc.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      {doc.size} • {doc.pages} pages • Uploaded on {doc.date}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                    {doc.status}
                  </span>
                  <Button variant="ghost" size="icon" className="text-destructive hover:bg-destructive/10 hover:text-destructive">
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
        </CardContent>
      </Card>
    </div>
  )
}
