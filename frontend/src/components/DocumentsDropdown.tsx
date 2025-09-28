import { useState, useEffect } from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { useDocuments, useDiscovery } from '@/lib/queries'
import { Skeleton } from '@/components/ui/skeleton'
import { schemaRegistry } from '@/lib/schemaRegistry'

interface DocumentsDropdownProps {
  onSelect: (documentRef: { id: string | number; label: string }) => void
  value?: string | number
  disabled?: boolean
}

export default function DocumentsDropdown({ onSelect, value, disabled }: DocumentsDropdownProps) {
  const { data: documents, isLoading, error } = useDocuments()
  const { data: discovery } = useDiscovery()
  const [selectedValue, setSelectedValue] = useState<string>(value?.toString() || '')

  useEffect(() => {
    console.log('DocumentsDropdown - documents:', documents)
    console.log('DocumentsDropdown - session uploads:', schemaRegistry.getSessionUploads())
  }, [documents])

  const handleValueChange = (newValue: string) => {
    setSelectedValue(newValue)
    const document = documents?.find(doc => doc.id.toString() === newValue)
    if (document) {
      onSelect({ id: document.id, label: document.label })
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Label>Document</Label>
        <Skeleton className="h-10 w-full" />
      </div>
    )
  }

  if (error || !documents || documents.length === 0) {
    return (
      <div className="space-y-2">
        <Label>Document</Label>
        <div className="text-sm text-muted-foreground">
          {!discovery?.documents ? (
            <span className="text-amber-600">
              No documents available. Upload a document first.
            </span>
          ) : (
            <span className="text-red-600">
              Failed to load documents. Please try again.
            </span>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <Label>Document</Label>
      <Select value={selectedValue} onValueChange={handleValueChange} disabled={disabled}>
        <SelectTrigger>
          <SelectValue placeholder="Select a document" />
        </SelectTrigger>
        <SelectContent>
          {documents.map((doc) => (
            <SelectItem key={doc.id} value={doc.id.toString()}>
              {doc.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {!discovery?.documents && (
        <p className="text-xs text-muted-foreground">
          Showing recent uploads (no list endpoint detected)
        </p>
      )}
    </div>
  )
}
