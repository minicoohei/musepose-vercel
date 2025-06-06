'use client'

import { useCallback, useState } from 'react'
import Image from 'next/image'

interface ImageUploadProps {
  file: File | null
  onChange: (file: File | null) => void
}

export default function ImageUpload({ file, onChange }: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null)

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      onChange(selectedFile)
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(selectedFile)
    }
  }, [onChange])

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      onChange(droppedFile)
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(droppedFile)
    }
  }, [onChange])

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
  }, [])

  return (
    <div className="card p-6">
      <h3 className="text-xl font-semibold mb-4">🖼️ Reference Image</h3>
      
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary hover:bg-primary/5 transition-all cursor-pointer"
      >
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
          id="image-upload"
        />
        <label htmlFor="image-upload" className="cursor-pointer">
          {preview ? (
            <div className="space-y-4">
              <div className="relative w-full h-48">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full h-full object-contain rounded"
                />
              </div>
              <p className="text-sm text-muted-foreground">
                {file?.name}
              </p>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault()
                  onChange(null)
                  setPreview(null)
                }}
                className="text-sm text-destructive hover:underline"
              >
                Remove image
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="text-4xl">📤</div>
              <p className="font-medium">Click to upload or drag and drop</p>
              <p className="text-sm text-muted-foreground">
                PNG, JPG or JPEG (max. 10MB)
              </p>
            </div>
          )}
        </label>
      </div>
      
      <p className="text-sm text-muted-foreground mt-2">
        Upload an image of the character you want to apply the pose to
      </p>
    </div>
  )
}