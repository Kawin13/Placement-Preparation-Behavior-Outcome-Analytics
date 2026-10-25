import React, { useState } from 'react';
import { Button } from '../common/Button';
import {
  GraduationCap,
  Sparkles,
  LogOut,
  User as UserIcon,
  Menu,
  X,
  Compass,
  Layers,
  HelpCircle,
  Building2,
} from 'lucide-react';
import type { UserSummary } from '../../services/auth';

export interface NavbarProps {
  systemStatus?: 'connected' | 'checking' | 'error';
  currentUser?: UserSummary | null;
  currentView?:
    | 'workspace'
    | 'practice'
    | 'running'
    | 'results'
    | 'mistakes'
    | 'analytics'
    | 'readiness'
    | 'outcomes'
    | 'training'
    | 'cohort-analytics'
    | 'admin'
    | 'catalog';
  onViewChange?: (
    view:
      | 'workspace'
      | 'practice'
      | 'running'
      | 'results'
      | 'mistakes'
      | 'analytics'
      | 'readiness'
      | 'outcomes'
      | 'training'
      | 'cohort-analytics'
      | 'admin'
      | 'catalog'
  ) => void;
  onStartPractice?: () => void;
  onSignIn?: () => void;
  onSignOut?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentUser,
  currentView = 'workspace',
  onViewChange,
  onStartPractice,
  onSignIn,
  onSignOut,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const scrollToSection = (id: string) => {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleNavClick = (
    view:
      | 'workspace'
      | 'practice'
      | 'mistakes'
      | 'analytics'
      | 'readiness'
      | 'outcomes'
      | 'training'
      | 'cohort-analytics'
      | 'admin'
      | 'catalog'
  ) => {
    setMobileMenuOpen(false);
    onViewChange?.(view);
  };

  return (
    <header className="sticky top-0 z-40 w-full bg-[#FAF6ED]/95 backdrop-blur-md border-b border-[#E8E0D2] transition-colors">
      <div className="max-w-[1240px] mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand Identity */}
        <div
          className="flex items-center gap-3 cursor-pointer select-none"
          onClick={() => handleNavClick('workspace')}
        >
          <div className="w-10 h-10 rounded-xl bg-[#292444] text-[#FAF6ED] flex items-center justify-center font-bold shadow-xs">
            <GraduationCap className="w-5 h-5 text-[#FF5B3D]" />
          </div>
          <div>
            <span className="text-lg font-bold tracking-tight text-[#292444] block leading-none font-display">
              Placement Portal
            </span>
            <span className="text-[11px] font-medium text-[#5E5875] tracking-wide block mt-1">
              Career Readiness & Outcomes
            </span>
          </div>
        </div>

        {/* Navigation Items (Desktop - Signed In) */}
        {currentUser ? (
          <nav className="hidden lg:flex items-center gap-1 bg-[#F5EFE3]/80 p-1.5 rounded-full border border-[#E8E0D2]">
            <button
              onClick={() => handleNavClick('workspace')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'workspace'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Workspace
            </button>
            <button
              onClick={() => handleNavClick('practice')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'practice'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Practice Engine
            </button>
            <button
              onClick={() => handleNavClick('mistakes')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'mistakes'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Mistake Notebook
            </button>
            <button
              onClick={() => handleNavClick('analytics')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'analytics'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Skill Analytics
            </button>
            <button
              onClick={() => handleNavClick('readiness')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${
                currentView === 'readiness'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              <span>Role Readiness</span>
              <span className="w-1.5 h-1.5 rounded-full bg-[#FF5B3D]" />
            </button>
            <button
              onClick={() => handleNavClick('outcomes')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'outcomes'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Placement Ledger
            </button>
            <button
              onClick={() => handleNavClick('training')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'training'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Training Impact
            </button>
            {currentUser.role !== 'STUDENT' && (
              <>
                <button
                  onClick={() => handleNavClick('cohort-analytics')}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                    currentView === 'cohort-analytics'
                      ? 'text-[#292444] bg-white shadow-xs'
                      : 'text-[#5E5875] hover:text-[#292444]'
                  }`}
                >
                  Cohort Insights
                </button>
                <button
                  onClick={() => handleNavClick('admin')}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
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
              onClick={() => handleNavClick('catalog')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                currentView === 'catalog'
                  ? 'text-[#292444] bg-white shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Curriculum
            </button>
          </nav>
        ) : (
          /* Public Navigation Links (Desktop - Signed Out) */
          <nav className="hidden md:flex items-center gap-8">
            <button
              onClick={() => scrollToSection('features')}
              className="text-xs font-semibold text-[#5E5875] hover:text-[#292444] transition-colors flex items-center gap-1.5"
            >
              <Compass className="w-3.5 h-3.5 text-[#FF5B3D]" />
              Features
            </button>
            <button
              onClick={() => scrollToSection('how-it-works')}
              className="text-xs font-semibold text-[#5E5875] hover:text-[#292444] transition-colors flex items-center gap-1.5"
            >
              <HelpCircle className="w-3.5 h-3.5 text-[#5E5875]" />
              How It Works
            </button>
            <button
              onClick={() => scrollToSection('tracks')}
              className="text-xs font-semibold text-[#5E5875] hover:text-[#292444] transition-colors flex items-center gap-1.5"
            >
              <Layers className="w-3.5 h-3.5 text-[#5E5875]" />
              Practice Tracks
            </button>
            <button
              onClick={() => scrollToSection('institutions')}
              className="text-xs font-semibold text-[#5E5875] hover:text-[#292444] transition-colors flex items-center gap-1.5"
            >
              <Building2 className="w-3.5 h-3.5 text-[#5E5875]" />
              For Institutions
            </button>
          </nav>
        )}

        {/* Header Actions */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {currentUser ? (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-full border border-[#E8E0D2] shadow-xs">
                <div className="w-6 h-6 rounded-full bg-[#FAF6ED] flex items-center justify-center text-[#292444]">
                  <UserIcon className="w-3.5 h-3.5" />
                </div>
                <div className="text-left hidden xl:block">
                  <span className="text-xs font-bold text-[#292444] block leading-none">
                    {currentUser.full_name}
                  </span>
                  <span className="text-[10px] font-semibold text-[#FF5B3D] uppercase tracking-wider block mt-0.5">
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
            <Button
              variant="secondary"
              size="sm"
              onClick={onSignIn}
              className="hidden sm:inline-flex font-semibold"
            >
              Sign In
            </Button>
          )}

          <Button
            variant="primary"
            size="sm"
            onClick={onStartPractice}
            rightIcon={<Sparkles className="w-3.5 h-3.5" />}
            className="shadow-xs font-semibold"
          >
            Start Practising
          </Button>

          {/* Mobile Menu Toggle Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
            className="p-2 rounded-xl text-[#292444] hover:bg-[#F5EFE3] transition-colors md:hidden"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Accessible Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-[#E8E0D2] bg-[#FAF6ED] px-4 pt-3 pb-6 shadow-warm-lg animate-in fade-in slide-in-from-top-2 duration-150">
          {currentUser ? (
            <div className="space-y-1 py-2">
              <div className="px-3 py-2 mb-2 bg-white rounded-2xl border border-[#E8E0D2] flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-[#292444] block">
                    {currentUser.full_name}
                  </span>
                  <span className="text-[10px] font-semibold text-[#FF5B3D] uppercase">
                    {currentUser.role}
                  </span>
                </div>
                <button
                  onClick={onSignOut}
                  className="text-xs text-[#5E5875] hover:text-[#B91C1C] font-semibold flex items-center gap-1"
                >
                  <LogOut className="w-3.5 h-3.5" /> Sign Out
                </button>
              </div>

              <button
                onClick={() => handleNavClick('workspace')}
                className={`w-full text-left px-3.5 py-2 rounded-xl text-xs font-semibold ${
                  currentView === 'workspace'
                    ? 'bg-[#292444] text-white'
                    : 'text-[#292444] hover:bg-white'
                }`}
              >
                Preparation Workspace
              </button>
              <button
                onClick={() => handleNavClick('practice')}
                className={`w-full text-left px-3.5 py-2 rounded-xl text-xs font-semibold ${
                  currentView === 'practice'
                    ? 'bg-[#292444] text-white'
                    : 'text-[#292444] hover:bg-white'
                }`}
              >
                Practice Engine
              </button>
              <button
                onClick={() => handleNavClick('mistakes')}
                className={`w-full text-left px-3.5 py-2 rounded-xl text-xs font-semibold ${
                  currentView === 'mistakes'
                    ? 'bg-[#292444] text-white'
                    : 'text-[#292444] hover:bg-white'
                }`}
              >
                Mistake Notebook
              </button>
              <button
                onClick={() => handleNavClick('analytics')}
                className={`w-full text-left px-3.5 py-2 rounded-xl text-xs font-semibold ${
                  currentView === 'analytics'
                    ? 'bg-[#292444] text-white'
                    : 'text-[#292444] hover:bg-white'
                }`}
              >
                Skill Analytics
              </button>
              <button
                onClick={() => handleNavClick('readiness')}
                className={`w-full text-left px-3.5 py-2 rounded-xl text-xs font-semibold ${
                  currentView === 'readiness'
                    ? 'bg-[#292444] text-white'
                    : 'text-[#292444] hover:bg-white'
                }`}
              >
                Role Readiness
              </button>
              <button
                onClick={() => handleNavClick('outcomes')}
                className={`w-full text-left px-3.5 py-2 rounded-xl text-xs font-semibold ${
                  currentView === 'outcomes'
                    ? 'bg-[#292444] text-white'
                    : 'text-[#292444] hover:bg-white'
                }`}
              >
                Placement Ledger
              </button>
              <button
                onClick={() => handleNavClick('training')}
                className={`w-full text-left px-3.5 py-2 rounded-xl text-xs font-semibold ${
                  currentView === 'training'
                    ? 'bg-[#292444] text-white'
                    : 'text-[#292444] hover:bg-white'
                }`}
              >
                Training Impact
              </button>
              {currentUser.role !== 'STUDENT' && (
                <>
                  <button
                    onClick={() => handleNavClick('cohort-analytics')}
                    className={`w-full text-left px-3.5 py-2 rounded-xl text-xs font-semibold ${
                      currentView === 'cohort-analytics'
                        ? 'bg-[#292444] text-white'
                        : 'text-[#292444] hover:bg-white'
                    }`}
                  >
                    Cohort Insights
                  </button>
                  <button
                    onClick={() => handleNavClick('admin')}
                    className={`w-full text-left px-3.5 py-2 rounded-xl text-xs font-semibold ${
                      currentView === 'admin'
                        ? 'bg-[#292444] text-white'
                        : 'text-[#292444] hover:bg-white'
                    }`}
                  >
                    College Admin
                  </button>
                </>
              )}
            </div>
          ) : (
            <div className="space-y-2 py-2">
              <button
                onClick={() => scrollToSection('features')}
                className="w-full text-left px-3.5 py-2.5 rounded-xl text-sm font-semibold text-[#292444] hover:bg-white flex items-center gap-2"
              >
                <Compass className="w-4 h-4 text-[#FF5B3D]" />
                Features & Capabilities
              </button>
              <button
                onClick={() => scrollToSection('how-it-works')}
                className="w-full text-left px-3.5 py-2.5 rounded-xl text-sm font-semibold text-[#292444] hover:bg-white flex items-center gap-2"
              >
                <HelpCircle className="w-4 h-4 text-[#5E5875]" />
                How It Works
              </button>
              <button
                onClick={() => scrollToSection('tracks')}
                className="w-full text-left px-3.5 py-2.5 rounded-xl text-sm font-semibold text-[#292444] hover:bg-white flex items-center gap-2"
              >
                <Layers className="w-4 h-4 text-[#5E5875]" />
                Curated Practice Tracks
              </button>
              <button
                onClick={() => scrollToSection('institutions')}
                className="w-full text-left px-3.5 py-2.5 rounded-xl text-sm font-semibold text-[#292444] hover:bg-white flex items-center gap-2"
              >
                <Building2 className="w-4 h-4 text-[#5E5875]" />
                For Colleges & Placement Cells
              </button>

              <div className="pt-3 border-t border-[#E8E0D2] flex flex-col gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onSignIn?.();
                  }}
                  className="w-full justify-center"
                >
                  Sign In
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onStartPractice?.();
                  }}
                  rightIcon={<Sparkles className="w-3.5 h-3.5" />}
                  className="w-full justify-center"
                >
                  Start Practising
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </header>
  );
};
