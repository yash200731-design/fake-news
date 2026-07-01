import React, { useEffect } from 'react';
import { X, CheckCircle2, AlertCircle, Info } from 'lucide-react';

export default function Toast({ toasts, onClose }) {
  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 w-full max-w-[340px] pointer-events-none px-4 sm:px-0">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onClose={onClose} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onClose }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(toast.id);
    }, 3500);
    return () => clearTimeout(timer);
  }, [toast.id, onClose]);

  const { id, message, type } = toast;

  const styles = {
    success: {
      border: 'border-brand-green/30',
      icon: <CheckCircle2 className="w-5 h-5 text-brand-green flex-shrink-0" />,
      bg: 'bg-emerald-950/20'
    },
    error: {
      border: 'border-red-500/30',
      icon: <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />,
      bg: 'bg-red-950/20'
    },
    info: {
      border: 'border-brand-blue/30',
      icon: <Info className="w-5 h-5 text-brand-blue-light flex-shrink-0" />,
      bg: 'bg-blue-950/20'
    }
  };

  const currentStyle = styles[type] || styles.info;

  return (
    <div className={`pointer-events-auto flex items-start justify-between p-4 rounded-xl border glass-panel glow-green animate-slideIn ${currentStyle.border} ${currentStyle.bg} shadow-lg shadow-black/20`}>
      <div className="flex items-start gap-3">
        {currentStyle.icon}
        <p className="text-xs font-semibold text-text-primary leading-normal pr-2">
          {message}
        </p>
      </div>
      <button
        onClick={() => onClose(id)}
        className="text-text-muted hover:text-text-primary p-0.5 rounded transition-colors cursor-pointer"
        aria-label="Close notification"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
