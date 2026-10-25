import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, leftIcon, rightIcon, className = '', id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full text-left">
        {label && (
          <label htmlFor={inputId} className="block text-xs font-bold uppercase tracking-wider text-[#5E5875] mb-2">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {leftIcon && (
            <span className="absolute left-3.5 text-[#8E879E] pointer-events-none">
              {leftIcon}
            </span>
          )}
          <input
            id={inputId}
            ref={ref}
            className={`w-full bg-white text-[#292444] border ${
              error ? 'border-[#B91C1C] focus:ring-[#B91C1C]/20' : 'border-[#E8E0D2] focus:border-[#FF5B3D] focus:ring-[#FF5B3D]/20'
            } rounded-xl px-4 py-3 text-sm placeholder-[#8E879E] focus:outline-none focus:ring-4 transition-all duration-150 ${
              leftIcon ? 'pl-10' : ''
            } ${rightIcon ? 'pr-10' : ''} ${className}`}
            {...props}
          />
          {rightIcon && (
            <span className="absolute right-3.5 text-[#8E879E] pointer-events-none">
              {rightIcon}
            </span>
          )}
        </div>
        {error ? (
          <p className="mt-1.5 text-xs text-[#B91C1C] font-medium">{error}</p>
        ) : helperText ? (
          <p className="mt-1.5 text-xs text-[#8E879E]">{helperText}</p>
        ) : null}
      </div>
    );
  }
);

Input.displayName = 'Input';
