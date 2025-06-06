'use client'

import { useEffect, useState } from 'react'

interface S3Status {
  configured: boolean
  bucketName?: string
  region?: string
}

export default function S3StatusCard() {
  const [status, setStatus] = useState<S3Status>({ configured: false })

  useEffect(() => {
    // Check S3 configuration from environment
    const configured = !!(
      process.env.NEXT_PUBLIC_AWS_ACCESS_KEY_ID &&
      process.env.NEXT_PUBLIC_AWS_SECRET_ACCESS_KEY &&
      process.env.NEXT_PUBLIC_S3_BUCKET_NAME
    )

    setStatus({
      configured,
      bucketName: process.env.NEXT_PUBLIC_S3_BUCKET_NAME,
      region: process.env.NEXT_PUBLIC_AWS_REGION || 'us-east-1'
    })
  }, [])

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        🔧 Configuration Status
      </h3>
      
      {status.configured ? (
        <div className="alert alert-success">
          <span>✅</span>
          <div>
            <strong>S3 configured correctly</strong>
            <div className="text-sm mt-1">
              <div>Bucket: {status.bucketName}</div>
              <div>Region: {status.region}</div>
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="alert alert-warning mb-4">
            <span>⚠️</span>
            <div>
              <strong>S3 not configured</strong>
              <div className="text-sm">Running in demo mode</div>
            </div>
          </div>
          
          <div className="alert alert-info">
            <span>💡</span>
            <div>
              <strong className="block mb-2">Required environment variables:</strong>
              <ul className="text-sm space-y-1">
                <li>• AWS_ACCESS_KEY_ID</li>
                <li>• AWS_SECRET_ACCESS_KEY</li>
                <li>• S3_BUCKET_NAME</li>
                <li>• AWS_REGION (optional)</li>
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  )
}