import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import path from 'path'
import fs from 'fs/promises'
import os from 'os'

const execAsync = promisify(exec)

export async function POST(request: NextRequest) {
  try {
    const { url } = await request.json()

    if (!url) {
      return NextResponse.json(
        { error: 'URL is required' },
        { status: 400 }
      )
    }

    // Create temp directory
    const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'musepose-'))
    const outputPath = path.join(tempDir, 'video.mp4')

    // Download video using yt-dlp
    const formatOptions = [
      'best[height<=720][ext=mp4]/best[height<=720]',
      'best[height<=1080][ext=mp4]/best[height<=1080]',
      'best[ext=mp4]/best',
      'worst[ext=mp4]/worst',
      'best/worst'
    ]

    let downloadSuccess = false
    let videoInfo: any = {}

    for (const format of formatOptions) {
      try {
        const command = `yt-dlp -f "${format}" -o "${outputPath}" --no-warnings --quiet --print-json "${url}"`
        const { stdout, stderr } = await execAsync(command)
        
        if (stdout) {
          videoInfo = JSON.parse(stdout)
          downloadSuccess = true
          break
        }
      } catch (error) {
        console.log(`Format ${format} failed, trying next...`)
        continue
      }
    }

    if (!downloadSuccess) {
      throw new Error('Failed to download video with any format')
    }

    // Get video information using ffprobe
    const ffprobeCommand = `ffprobe -v quiet -print_format json -show_streams "${outputPath}"`
    const { stdout: ffprobeOutput } = await execAsync(ffprobeCommand)
    const ffprobeData = JSON.parse(ffprobeOutput)
    const videoStream = ffprobeData.streams.find((s: any) => s.codec_type === 'video')

    const videoData = {
      frame_count: parseInt(videoStream.nb_frames || '0'),
      fps: eval(videoStream.r_frame_rate),
      width: videoStream.width,
      height: videoStream.height,
      duration: parseFloat(videoStream.duration || '0')
    }

    // For Vercel deployment, we'll need to upload this to S3 or return as base64
    // For now, we'll simulate with a public URL
    const videoUrl = videoInfo.webpage_url || url

    // Clean up temp files
    await fs.rm(tempDir, { recursive: true, force: true })

    return NextResponse.json({
      videoUrl,
      videoInfo: videoData
    })

  } catch (error) {
    console.error('Download error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to download video' },
      { status: 500 }
    )
  }
}