import type React from 'react';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'neutral' | 'success' | 'warning' | 'error' | 'coral';
  hasDot?: boolean;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  hasDot = false,
  className = '',
}) => {
  const variantStyles = {
    neutral: 'bg-[#F5EFE3] text-[#292444] border-[#E8E0D2]',
    success: 'bg-[#F0FDF4] text-[#15803D] border-[#BBF7D0]',
    warning: 'bg-[#FFFBEB] text-[#B45309] border-[#FDE68A]',
    error: 'bg-[#FEF2F2] text-[#B91C1C] border-[#FECACA]',
    coral: 'bg-[#FFF1EE] text-[#FF5B3D] border-[#FFD5CC]',
  };

  const dotColors = {
    neutral: 'bg-[#292444]',
    success: 'bg-[#15803D]',
    warning: 'bg-[#F59E0B]',
    error: 'bg-[#EF4444]',
    coral: 'bg-[#FF5B3D]',
  };

  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border select-none ${variantStyles[variant]} ${className}`}
    >
      {hasDot && (
        <span
          className={`w-2 h-2 rounded-full mr-2 shrink-0 ${dotColors[variant]} animate-pulse`}
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  );
};
