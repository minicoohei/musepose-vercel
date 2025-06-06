import { ProcessingState } from '@/lib/types'

interface ProcessingStatusProps {
  state: ProcessingState
  onCancel: () => void
}

export default function ProcessingStatus({ state, onCancel }: ProcessingStatusProps) {
  return (
    <div className="card p-6">
      <h3 className="text-xl font-semibold mb-6">🔄 Processing</h3>
      
      <div className="space-y-6">
        <div className="alert alert-info">
          <span>📥</span>
          <div>{state.currentStep}</div>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress</span>
            <span>{Math.round(state.progress * 100)}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
            <div 
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${state.progress * 100}%` }}
            />
          </div>
        </div>
        
        {state.details && (
          <div className="status-badge">
            {state.details}
          </div>
        )}
        
        <div className="flex justify-center">
          <button
            onClick={onCancel}
            className="px-6 py-2 rounded-lg font-medium btn-destructive"
          >
            ❌ Cancel
          </button>
        </div>
      </div>
    </div>
  )
}