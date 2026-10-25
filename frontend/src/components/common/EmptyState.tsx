import type React from 'react';
import { Button } from './Button';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionText,
  onAction,
  className = '',
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center text-center p-8 md:p-12 border border-dashed border-[#E8E0D2] rounded-2xl bg-[#FAF6ED]/40 ${className}`}
    >
      {icon && (
        <div className="w-12 h-12 rounded-full bg-[#F5EFE3] border border-[#E8E0D2] flex items-center justify-center text-[#292444] mb-4">
          {icon}
        </div>
      )}
      <h3 className="text-base font-bold text-[#292444] mb-1.5">{title}</h3>
      <p className="text-sm text-[#5E5875] max-w-sm mb-6 leading-relaxed">{description}</p>
      {actionText && onAction && (
        <Button variant="primary" size="sm" onClick={onAction}>
          {actionText}
        </Button>
      )}
    </div>
  );
};
