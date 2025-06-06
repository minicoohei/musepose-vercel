export default function Header() {
  return (
    <header className="border-b">
      <div className="container mx-auto px-4 py-12 text-center">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent mb-2">
          🎬 MusePose
        </h1>
        <p className="text-lg text-muted-foreground">
          Generate pose-driven videos from TikTok dance videos
        </p>
      </div>
    </header>
  )
}