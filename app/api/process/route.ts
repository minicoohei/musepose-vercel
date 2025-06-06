import { NextRequest, NextResponse } from 'next/server'
import Replicate from 'replicate'

const replicate = new Replicate({
  auth: process.env.REPLICATE_API_TOKEN!,
})

export async function POST(request: NextRequest) {
  try {
    const { videoUrl, imageUrl, videoInfo } = await request.json()

    if (!videoUrl || !imageUrl) {
      return NextResponse.json(
        { error: 'Video URL and image URL are required' },
        { status: 400 }
      )
    }

    // Check if Replicate API is configured
    if (!process.env.REPLICATE_API_TOKEN) {
      // Return demo video for development
      return NextResponse.json({
        outputUrl: 'https://replicate.delivery/pbxt/pGhU1BDVZXrLDVl2wvQs77YPjYm6wu2ZH7dGrh0XGB4JGMvE/video_and_audio.mp4',
        processingParams: {
          max_frames: Math.min(videoInfo.frame_count, 300),
          image_resolution: Math.min(videoInfo.height, 720),
          detect_resolution: 512
        },
        demo: true
      })
    }

    // Calculate processing parameters
    const maxFrames = Math.min(videoInfo.frame_count, 300)
    const imageResolution = Math.min(videoInfo.height, 720)
    const detectResolution = 512

    // Start Replicate prediction
    const prediction = await replicate.predictions.create({
      version: "56b9a43be4bdd701bfc4bbdc91b6d0410c81da51e7e7037c790449f34277f84d",
      input: {
        vidfn: videoUrl,
        imgfn_refer: imageUrl,
        detect_resolution: detectResolution,
        image_resolution: imageResolution,
        align_frame: 0,
        max_frame: maxFrames
      }
    })

    // Poll for completion
    let output = null
    let attempts = 0
    const maxAttempts = 150 // 5 minutes with 2-second intervals

    while (attempts < maxAttempts) {
      const updatedPrediction = await replicate.predictions.get(prediction.id)
      
      if (updatedPrediction.status === 'succeeded') {
        output = updatedPrediction.output
        break
      } else if (updatedPrediction.status === 'failed') {
        throw new Error(updatedPrediction.error || 'Processing failed')
      } else if (updatedPrediction.status === 'canceled') {
        throw new Error('Processing was canceled')
      }

      // Wait 2 seconds before next check
      await new Promise(resolve => setTimeout(resolve, 2000))
      attempts++
    }

    if (!output) {
      throw new Error('Processing timeout')
    }

    return NextResponse.json({
      outputUrl: output,
      processingParams: {
        max_frames: maxFrames,
        image_resolution: imageResolution,
        detect_resolution: detectResolution
      }
    })

  } catch (error) {
    console.error('Processing error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to process video' },
      { status: 500 }
    )
  }
}