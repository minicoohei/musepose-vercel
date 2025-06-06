interface VideoInputProps {
  value: string
  onChange: (value: string) => void
}

export default function VideoInput({ value, onChange }: VideoInputProps) {
  return (
    <div className="card p-6">
      <h3 className="text-xl font-semibold mb-4">📹 Input Settings</h3>
      
      <div className="space-y-2">
        <label htmlFor="tiktok-url" className="block text-sm font-medium">
          TikTok Video URL
        </label>
        <input
          id="tiktok-url"
          type="url"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="https://www.tiktok.com/@username/video/..."
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-background"
        />
        <p className="text-sm text-muted-foreground">
          Enter the URL of the TikTok video you want to process
        </p>
      </div>
    </div>
  )
}