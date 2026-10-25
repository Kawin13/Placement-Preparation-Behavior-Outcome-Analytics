import type React from 'react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { GraduationCap, Sparkles, LogOut, User as UserIcon } from 'lucide-react';
import type { UserSummary } from '../../services/auth';

export interface NavbarProps {
  systemStatus?: 'connected' | 'checking' | 'error';
  currentUser?: UserSummary | null;
  currentView?: 'workspace' | 'practice' | 'mistakes' | 'analytics' | 'readiness' | 'outcomes' | 'training' | 'cohort-analytics' | 'admin' | 'catalog';
  onViewChange?: (view: 'workspace' | 'practice' | 'mistakes' | 'analytics' | 'readiness' | 'outcomes' | 'training' | 'cohort-analytics' | 'admin' | 'catalog') => void;
  onStartPractice?: () => void;
  onSignIn?: () => void;
  onSignOut?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  systemStatus = 'connected',
  currentUser,
  currentView = 'workspace',
  onViewChange,
  onStartPractice,
  onSignIn,
  onSignOut,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full bg-[#FAF6ED]/90 backdrop-blur-md border-b border-[#E8E0D2] transition-colors">
      <div className="max-w-[1240px] mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand Identity */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => onViewChange?.('workspace')}>
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
        {currentUser && (
          <nav className="hidden md:flex items-center gap-1 bg-[#F5EFE3]/80 p-1.5 rounded-full border border-[#E8E0D2]">
            <button
              onClick={() => onViewChange?.('workspace')}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'workspace'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Workspace
            </button>
            <button
              onClick={() => onViewChange?.('practice')}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'practice'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Practice Engine
            </button>
            <button
              onClick={() => onViewChange?.('mistakes')}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'mistakes'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Mistake Notebook
            </button>
            {/* Student Analytics Tab */}
            <button
              onClick={() => onViewChange?.('analytics')}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'analytics'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Skill Analytics
            </button>
            {/* Role Readiness Tab */}
            <button
              onClick={() => onViewChange?.('readiness')}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${
                currentView === 'readiness'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              <span>Role Readiness</span>
              <span className="w-1.5 h-1.5 rounded-full bg-[#FF5B3D]" />
            </button>
            {/* Placement Ledger Tab */}
            <button
              onClick={() => onViewChange?.('outcomes')}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'outcomes'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Placement Ledger
            </button>
            {/* Training Impact Tab */}
            <button
              onClick={() => onViewChange?.('training')}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'training'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Training Impact
            </button>
            {/* Institutional Cohort Analytics Tab for Staff / Trainers / Admins */}
            {currentUser.role !== 'STUDENT' && (
              <>
                <button
                  onClick={() => onViewChange?.('cohort-analytics')}
                  className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                    currentView === 'cohort-analytics'
                      ? 'text-[#292444] bg-white shadow-xs'
                      : 'text-[#5E5875] hover:text-[#292444]'
                  }`}
                >
                  Cohort Telemetry
                </button>
                <button
                  onClick={() => onViewChange?.('admin')}
                  className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                    currentView === 'admin'
                      ? 'text-[#292444] bg-white shadow-xs'
                      : 'text-[#5E5875] hover:text-[#292444]'
                  }`}
                >
                  College Admin
                </button>
              </>
            )}
            <button
              onClick={() => onViewChange?.('catalog')}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'catalog'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Curriculum Overview
            </button>
          </nav>
        )}

        {/* System Indicator, User Profile & Actions */}
        <div className="flex items-center gap-3">
          <Badge
            variant={systemStatus === 'connected' ? 'success' : systemStatus === 'checking' ? 'warning' : 'error'}
            hasDot
            className="hidden sm:inline-flex"
          >
            {systemStatus === 'connected' ? 'PostgreSQL Active' : systemStatus === 'checking' ? 'Checking...' : 'DB Offline'}
          </Badge>

          {currentUser ? (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-full border border-[#E8E0D2] shadow-xs">
                <div className="w-6 h-6 rounded-full bg-[#FAF6ED] flex items-center justify-center text-[#292444]">
                  <UserIcon className="w-3.5 h-3.5" />
                </div>
                <div className="text-left hidden lg:block">
                  <span className="text-xs font-bold text-[#292444] block leading-none">
                    {currentUser.full_name}
                  </span>
                  <span className="text-[10px] font-semibold text-[#FF5B3D] uppercase tracking-wider block">
                    {currentUser.role}
                  </span>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={onSignOut}
                title="Sign Out"
                leftIcon={<LogOut className="w-3.5 h-3.5" />}
              >
                <span className="hidden sm:inline">Sign Out</span>
              </Button>
            </div>
          ) : (
            <Button variant="secondary" size="sm" onClick={onSignIn} className="hidden sm:inline-flex">
              Sign In
            </Button>
          )}

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
