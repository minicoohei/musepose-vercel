import { ProcessingResult } from '@/lib/types'

interface VideoResultProps {
  result: ProcessingResult
  onReset: () => void
}

export default function VideoResult({ result, onReset }: VideoResultProps) {
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h3 className="text-xl font-semibold mb-4">✅ Generation Result</h3>
        
        {result.usedS3 ? (
          <div className="alert alert-success mb-4">
            <span>✅</span>
            <div>🌐 Processed using S3 storage</div>
          </div>
        ) : (
          <div className="alert alert-info mb-4">
            <span>💻</span>
            <div>Processed in demo mode</div>
          </div>
        )}
        
        <div className="aspect-video bg-black rounded-lg overflow-hidden">
          <video
            src={result.outputVideo}
            controls
            className="w-full h-full"
          />
        </div>
        
        <div className="mt-4 space-y-3">
          <a
            href={result.outputVideo}
            download
            className="block w-full px-6 py-3 rounded-lg font-medium text-center btn-primary"
          >
            📥 Download Video
          </a>
          
          <button
            onClick={onReset}
            className="w-full px-6 py-3 rounded-lg font-medium btn-secondary"
          >
            🔄 Process New Video
          </button>
        </div>
      </div>
      
      <div className="card p-6">
        <h4 className="text-lg font-semibold mb-4">📊 Processing Information</h4>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-muted-foreground">Frame Count</div>
            <div className="text-2xl font-semibold">{result.videoInfo.frame_count}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">FPS</div>
            <div className="text-2xl font-semibold">{result.videoInfo.fps.toFixed(2)}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Resolution</div>
            <div className="text-2xl font-semibold">{result.videoInfo.width}x{result.videoInfo.height}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Duration</div>
            <div className="text-2xl font-semibold">{result.videoInfo.duration.toFixed(1)}s</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Processed Frames</div>
            <div className="text-2xl font-semibold">{result.processingParams.max_frames}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Output Resolution</div>
            <div className="text-2xl font-semibold">{result.processingParams.image_resolution}px</div>
          </div>
        </div>
      </div>
    </div>
  )
}