import type React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: 'default' | 'subtle' | 'contrast';
  isHoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  isHoverable = false,
  className = '',
  ...props
}) => {
  const variants = {
    default: 'bg-white border-[#E8E0D2] text-[#292444]',
    subtle: 'bg-[#F5EFE3]/60 border-[#E8E0D2] text-[#292444]',
    contrast: 'bg-[#292444] border-[#3B345E] text-white',
  };

  const hoverStyle = isHoverable
    ? 'transition-all duration-200 hover:border-[#D5CBBA] hover:shadow-warm cursor-pointer active:scale-[0.99]'
    : '';

  return (
    <div
      className={`rounded-2xl border p-6 md:p-8 ${variants[variant]} ${hoverStyle} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
