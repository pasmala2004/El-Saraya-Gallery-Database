import { useState, useRef, useEffect } from 'react';
import { Check, X, Edit2 } from 'lucide-react';

interface InlineEditProps {
  value: string;
  onSave: (value: string) => void;
  type?: 'text' | 'date' | 'number' | 'textarea';
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  displayFormat?: (value: string) => string;
}

export default function InlineEdit({
  value,
  onSave,
  type = 'text',
  placeholder = '-',
  disabled = false,
  className = '',
  displayFormat,
}: InlineEditProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isEditing]);

  const handleSave = () => {
    if (editValue !== value) {
      onSave(editValue);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditValue(value);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && type !== 'textarea') {
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  if (disabled) {
    return (
      <span className={className}>
        {displayFormat ? displayFormat(value) : value || placeholder}
      </span>
    );
  }

  if (isEditing) {
    const commonProps = {
      ref: inputRef as any,
      value: editValue,
      onChange: (e: any) => setEditValue(e.target.value),
      onKeyDown: handleKeyDown,
      onBlur: handleSave,
      className: `px-2 py-1 border border-blue-500 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`,
    };

    return (
      <div className="flex items-center gap-2">
        {type === 'textarea' ? (
          <textarea {...commonProps} rows={3} />
        ) : (
          <input {...commonProps} type={type} />
        )}
        <button
          onClick={handleSave}
          className="p-1 text-green-600 hover:bg-green-50 rounded"
          type="button"
        >
          <Check className="w-4 h-4" />
        </button>
        <button
          onClick={handleCancel}
          className="p-1 text-red-600 hover:bg-red-50 rounded"
          type="button"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={() => setIsEditing(true)}
      className={`group flex items-center gap-2 hover:text-blue-600 transition-colors ${className}`}
    >
      <span>{displayFormat ? displayFormat(value) : value || placeholder}</span>
      <Edit2 className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
    </button>
  );
}
