export interface VideoInfo {
  frame_count: number
  fps: number
  width: number
  height: number
  duration: number
}

export interface ProcessingParams {
  max_frames: number
  image_resolution: number
  detect_resolution: number
}

export interface ProcessingState {
  isProcessing: boolean
  currentStep: string
  progress: number
  details: string
}

export interface ProcessingResult {
  outputVideo: string
  videoInfo: VideoInfo
  processingParams: ProcessingParams
  usedS3: boolean
}