# MusePose - AI-Powered Pose Animation Tool

MusePose is a powerful AI tool that allows you to animate images by applying poses from TikTok dance videos. Upload an image of your character and a TikTok dance video URL, and watch as your character comes to life!

## Features

- 🎥 Direct TikTok video download support
- 🖼️ Easy image upload interface
- 🤖 Powered by state-of-the-art AI models
- 🔄 Real-time processing status updates
- 📱 Mobile-friendly interface
- 🌐 AWS S3 integration for file storage
- ⚡ Deployed on Vercel for optimal performance

## Demo

![MusePose Demo](demo.gif)

## Tech Stack

- **Frontend**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **API Routes**: Next.js API Routes
- **AI Model**: Replicate's MusePose model
- **Storage**: AWS S3
- **Deployment**: Vercel

## Quick Start

### Prerequisites

- Node.js 18 or higher
- AWS account (for S3 storage)
- Replicate API token

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/musepose.git
cd musepose
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` file with your credentials:
```
REPLICATE_API_TOKEN=your_replicate_api_token
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=your_s3_bucket_name
AWS_REGION=us-east-1

# Public environment variables (for client-side)
NEXT_PUBLIC_AWS_ACCESS_KEY_ID=your_aws_access_key
NEXT_PUBLIC_AWS_SECRET_ACCESS_KEY=your_aws_secret_key
NEXT_PUBLIC_S3_BUCKET_NAME=your_s3_bucket_name
NEXT_PUBLIC_AWS_REGION=us-east-1
```

### Running the Application

#### Quick Start (Recommended)
Use the automated startup script that handles port conflicts and CORS:
```bash
./start_local.sh
```

This script will:
- Automatically detect and avoid port conflicts
- Set up proper CORS configuration
- Start both Next.js and Streamlit applications
- Display access URLs when ready

#### Manual Start
Development mode:
```bash
npm run dev
```

Production build:
```bash
npm run build
npm start
```

#### Access URLs
- **Main Application**: http://localhost:3001 (or next available port)
- **Backend Dashboard**: http://localhost:8503 (or next available port)

#### Port Configuration
The application automatically detects port conflicts and uses alternative ports:
- Next.js: 3001, 3002, 3003 (fallback)
- Streamlit: 8503, 8504, 8505 (fallback)

## Deployment on Vercel

### One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/musepose)

### Manual Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy to Vercel:
```bash
vercel
```

3. Set environment variables in Vercel dashboard:
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add all variables from `.env.example`

### Important Notes for Vercel Deployment

- **API Route Limitations**: The download API route has a 30-second timeout limit on Vercel
- **Video Processing**: Heavy video processing is handled by external services (Replicate)
- **File Storage**: All files are stored in S3, not on Vercel's filesystem

## Usage

1. **Enter TikTok URL**: Paste a TikTok video URL in the input field
2. **Upload Reference Image**: Upload an image of the character you want to animate
3. **Generate**: Click the "Generate Video" button
4. **Wait**: The processing typically takes 2-5 minutes
5. **Download**: Once complete, download your animated video!

## AWS S3 Setup

### Create S3 Bucket

1. Create an S3 bucket with public read access
2. Configure CORS for your bucket:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

3. Use the provided `bucket-policy.json` for bucket permissions

## Project Structure

```
musepose/
├── app/
│   ├── api/
│   │   ├── download/    # TikTok download endpoint
│   │   ├── process/     # Replicate processing endpoint
│   │   └── upload/      # S3 upload endpoint
│   ├── globals.css      # Global styles
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Main page
├── components/          # React components
├── lib/                 # Utility functions and types
├── public/              # Static assets
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── tailwind.config.ts   # Tailwind CSS config
├── next.config.js       # Next.js config
└── vercel.json          # Vercel deployment config
```

## API Routes

### POST /api/download
Downloads TikTok video and returns video information

### POST /api/upload
Uploads files to S3 and returns public URL

### POST /api/process
Processes video with Replicate's MusePose model

## Development

### Running Tests
```bash
npm test
```

### Linting
```bash
npm run lint
```

### Type Checking
```bash
npm run type-check
```

## Troubleshooting

### Common Issues

1. **Vercel Deployment Errors**
   - Ensure all environment variables are set in Vercel dashboard
   - Check function timeout limits in `vercel.json`
   - Monitor Vercel function logs for errors

2. **API Route Timeouts**
   - Vercel has a 10-second timeout for hobby plan, 60 seconds for pro
   - Consider using Edge Functions for longer operations
   - Implement webhook-based async processing for long tasks

3. **CORS Issues**
   - Verify S3 CORS configuration
   - Check `next.config.js` headers configuration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Replicate](https://replicate.com) for the MusePose AI model
- [Next.js](https://nextjs.org) for the React framework
- [Vercel](https://vercel.com) for hosting and deployment
- [Tailwind CSS](https://tailwindcss.com) for styling