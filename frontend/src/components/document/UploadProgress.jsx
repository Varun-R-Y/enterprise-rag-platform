export default function UploadProgress({ uploadingFiles }) {
  if (!uploadingFiles || uploadingFiles.length === 0) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-4 space-y-3">
      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
        Upload Queue
      </h4>
      <div className="space-y-3 max-h-60 overflow-y-auto">
        {uploadingFiles.map((file) => (
          <div key={file.id} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-slate-700 truncate max-w-[70%]" title={file.name}>
                {file.name}
              </span>
              <span className={`text-xs font-semibold ${
                file.status === 'failed' ? 'text-rose-600' :
                file.status === 'completed' ? 'text-emerald-600' :
                'text-indigo-600 animate-pulse'
              }`}>
                {file.status === 'failed' ? 'Failed' :
                 file.status === 'completed' ? 'Success' :
                 `${file.progress}%`}
              </span>
            </div>
            
            {/* Progress Bar */}
            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full transition-all duration-200 rounded-full ${
                  file.status === 'failed' ? 'bg-rose-500' :
                  file.status === 'completed' ? 'bg-emerald-500' :
                  'bg-indigo-600'
                }`}
                style={{ width: `${file.progress}%` }}
              />
            </div>
            
            {file.error && (
              <p className="text-rose-500 text-xs mt-0.5 font-medium leading-tight">
                {file.error}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
