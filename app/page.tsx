'use client'

import { useState, useCallback } from 'react'
import Image from 'next/image'
import Header from '@/components/Header'
import S3StatusCard from '@/components/S3StatusCard'
import VideoInput from '@/components/VideoInput'
import ImageUpload from '@/components/ImageUpload'
import ProcessingStatus from '@/components/ProcessingStatus'
import VideoResult from '@/components/VideoResult'
import { ProcessingState, ProcessingResult } from '@/lib/types'

export default function Home() {
  const [tiktokUrl, setTiktokUrl] = useState('')
  const [referenceImage, setReferenceImage] = useState<File | null>(null)
  const [processingState, setProcessingState] = useState<ProcessingState>({
    isProcessing: false,
    currentStep: '',
    progress: 0,
    details: ''
  })
  const [result, setResult] = useState<ProcessingResult | null>(null)

  const handleProcess = useCallback(async () => {
    if (!tiktokUrl || !referenceImage) return

    setProcessingState({
      isProcessing: true,
      currentStep: 'Initializing',
      progress: 0,
      details: 'Starting video processing...'
    })
    setResult(null)

    try {
      // Step 1: Download TikTok video
      setProcessingState(prev => ({
        ...prev,
        currentStep: 'Downloading TikTok video',
        progress: 0.1,
        details: 'Fetching video from TikTok...'
      }))

      const downloadResponse = await fetch('/api/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: tiktokUrl })
      })

      if (!downloadResponse.ok) {
        throw new Error('Failed to download TikTok video')
      }

      const { videoUrl, videoInfo } = await downloadResponse.json()

      // Step 2: Upload reference image
      setProcessingState(prev => ({
        ...prev,
        currentStep: 'Uploading reference image',
        progress: 0.3,
        details: 'Uploading your reference image...'
      }))

      const formData = new FormData()
      formData.append('file', referenceImage)
      formData.append('type', 'image')

      const uploadResponse = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload reference image')
      }

      const { url: imageUrl } = await uploadResponse.json()

      // Step 3: Process with Replicate
      setProcessingState(prev => ({
        ...prev,
        currentStep: 'Generating pose-driven video',
        progress: 0.5,
        details: 'Processing with MusePose AI model...'
      }))

      const processResponse = await fetch('/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          videoUrl,
          imageUrl,
          videoInfo
        })
      })

      if (!processResponse.ok) {
        throw new Error('Failed to process video')
      }

      const { outputUrl, processingParams } = await processResponse.json()

      // Set result
      setResult({
        outputVideo: outputUrl,
        videoInfo,
        processingParams,
        usedS3: true
      })

      setProcessingState({
        isProcessing: false,
        currentStep: 'Complete',
        progress: 1,
        details: 'Video generated successfully!'
      })

    } catch (error) {
      console.error('Processing error:', error)
      setProcessingState({
        isProcessing: false,
        currentStep: 'Error',
        progress: 0,
        details: error instanceof Error ? error.message : 'An error occurred'
      })
    }
  }, [tiktokUrl, referenceImage])

  const handleCancel = useCallback(() => {
    setProcessingState({
      isProcessing: false,
      currentStep: '',
      progress: 0,
      details: ''
    })
  }, [])

  const handleReset = useCallback(() => {
    setTiktokUrl('')
    setReferenceImage(null)
    setResult(null)
    setProcessingState({
      isProcessing: false,
      currentStep: '',
      progress: 0,
      details: ''
    })
  }, [])

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            <S3StatusCard />
            
            <div className="card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                💡 TikTok Video Tips
              </h3>
              <div className="alert alert-info">
                <div>
                  <strong className="block mb-2">Recommended video features:</strong>
                  <ul className="text-sm space-y-1">
                    <li>• Public videos only</li>
                    <li>• Short videos (15-60 seconds)</li>
                    <li>• Clear dance movements</li>
                    <li>• Single person in frame</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {!processingState.isProcessing && !result && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-6">
                  <VideoInput 
                    value={tiktokUrl}
                    onChange={setTiktokUrl}
                  />
                  
                  <ImageUpload
                    file={referenceImage}
                    onChange={setReferenceImage}
                  />
                </div>

                <div className="space-y-6">
                  {(!tiktokUrl || !referenceImage) && (
                    <div className="alert alert-warning">
                      <span>⚠️</span>
                      <div>Please provide both TikTok URL and reference image</div>
                    </div>
                  )}

                  <button
                    onClick={handleProcess}
                    disabled={!tiktokUrl || !referenceImage}
                    className="w-full px-6 py-3 rounded-lg font-medium btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    🎬 Generate Video
                  </button>
                </div>
              </div>
            )}

            {processingState.isProcessing && (
              <ProcessingStatus
                state={processingState}
                onCancel={handleCancel}
              />
            )}

            {result && !processingState.isProcessing && (
              <VideoResult
                result={result}
                onReset={handleReset}
              />
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t mt-12">
        <div className="container mx-auto px-4 py-8 text-center text-muted-foreground">
          <p className="text-sm">
            Powered by MusePose & Replicate | Built with ❤️ using Next.js
          </p>
        </div>
      </footer>
    </div>
  )
}