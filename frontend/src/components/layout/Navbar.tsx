import type React from 'react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { GraduationCap, Sparkles } from 'lucide-react';

export interface NavbarProps {
  systemStatus?: 'connected' | 'checking' | 'error';
  onStartPractice?: () => void;
  onSignIn?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  systemStatus = 'connected',
  onStartPractice,
  onSignIn,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full bg-[#FAF6ED]/90 backdrop-blur-md border-b border-[#E8E0D2] transition-colors">
      <div className="max-w-[1240px] mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand Identity */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#292444] text-[#FAF6ED] flex items-center justify-center font-bold shadow-sm">
            <GraduationCap className="w-5 h-5 text-[#FF5B3D]" />
          </div>
          <div>
            <span className="text-lg font-bold tracking-tight text-[#292444] block leading-none font-display">
              Placement Portal
            </span>
            <span className="text-[11px] font-medium text-[#5E5875] tracking-wide block mt-1">
              Behavior & Outcome Analytics
            </span>
          </div>
        </div>

        {/* Navigation Items (Desktop) */}
        <nav className="hidden md:flex items-center gap-1 bg-[#F5EFE3]/80 p-1.5 rounded-full border border-[#E8E0D2]">
          <a
            href="#overview"
            className="px-4 py-1.5 rounded-full text-xs font-semibold text-[#292444] bg-white shadow-xs"
          >
            Overview
          </a>
          <a
            href="#modules"
            className="px-4 py-1.5 rounded-full text-xs font-semibold text-[#5E5875] hover:text-[#292444] transition-colors"
          >
            Practice Tracks
          </a>
          <a
            href="#architecture"
            className="px-4 py-1.5 rounded-full text-xs font-semibold text-[#5E5875] hover:text-[#292444] transition-colors"
          >
            Architecture
          </a>
          <a
            href="#database"
            className="px-4 py-1.5 rounded-full text-xs font-semibold text-[#5E5875] hover:text-[#292444] transition-colors"
          >
            PostgreSQL Status
          </a>
        </nav>

        {/* System Indicator & Primary CTA */}
        <div className="flex items-center gap-3">
          <Badge
            variant={systemStatus === 'connected' ? 'success' : systemStatus === 'checking' ? 'warning' : 'error'}
            hasDot
            className="hidden sm:inline-flex"
          >
            {systemStatus === 'connected' ? 'PostgreSQL Active' : systemStatus === 'checking' ? 'Checking...' : 'DB Offline'}
          </Badge>

          <Button variant="secondary" size="sm" onClick={onSignIn} className="hidden sm:inline-flex">
            Sign In
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={onStartPractice}
            rightIcon={<Sparkles className="w-3.5 h-3.5" />}
          >
            Start Practice
          </Button>
        </div>
      </div>
    </header>
  );
};
