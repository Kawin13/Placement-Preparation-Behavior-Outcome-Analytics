import React, { useState, useEffect } from 'react';
import {
  GraduationCap,
  LayoutDashboard,
  Brain,
  BookOpen,
  TrendingUp,
  Target,
  Award,
  Building2,
  Compass,
  ShieldCheck,
  LogOut,
  Menu,
  X,
  Sparkles,
  ChevronRight,
} from 'lucide-react';
import { Button } from '../common/Button';
import type { UserSummary } from '../../services/auth';

export type ViewMode =
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

export interface NavItemConfig {
  id: ViewMode;
  label: string;
  icon: React.ReactNode;
  badge?: string;
}

interface AppShellProps {
  currentUser: UserSummary;
  currentView: ViewMode;
  onViewChange: (view: ViewMode) => void;
  onSignOut: () => void;
  onStartPractice?: () => void;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({
  currentUser,
  currentView,
  onViewChange,
  onSignOut,
  onStartPractice,
  children,
}) => {
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  // Close mobile drawer when pressing Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setMobileDrawerOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Define role-specific navigation configurations
  const getNavItems = (): NavItemConfig[] => {
    const role = currentUser.role?.toUpperCase();

    if (role === 'STUDENT') {
      return [
        {
          id: 'workspace',
          label: 'Overview',
          icon: <LayoutDashboard className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'practice',
          label: 'Practice',
          icon: <Brain className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'mistakes',
          label: 'Mistake Notebook',
          icon: <BookOpen className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'analytics',
          label: 'Skill Progress',
          icon: <TrendingUp className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'readiness',
          label: 'Role Readiness',
          icon: <Target className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'outcomes',
          label: 'Placement Journey',
          icon: <Award className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'training',
          label: 'Training Progress',
          icon: <Building2 className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'catalog',
          label: 'Learning Resources',
          icon: <Compass className="w-4 h-4 shrink-0" />,
        },
      ];
    }

    if (role === 'TRAINER') {
      return [
        {
          id: 'training',
          label: 'Training Programmes',
          icon: <Building2 className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'cohort-analytics',
          label: 'Cohort Insights',
          icon: <TrendingUp className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'practice',
          label: 'Practice Bank',
          icon: <Brain className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'catalog',
          label: 'Curriculum Resources',
          icon: <Compass className="w-4 h-4 shrink-0" />,
        },
      ];
    }

    if (role === 'PLACEMENT_OFFICER') {
      return [
        {
          id: 'outcomes',
          label: 'Placement Ledger',
          icon: <Award className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'cohort-analytics',
          label: 'Cohort Outcomes',
          icon: <TrendingUp className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'readiness',
          label: 'Student Readiness',
          icon: <Target className="w-4 h-4 shrink-0" />,
        },
        {
          id: 'training',
          label: 'Training Progress',
          icon: <Building2 className="w-4 h-4 shrink-0" />,
        },
      ];
    }

    // Default: ADMIN
    return [
      {
        id: 'admin',
        label: 'Executive Dossier',
        icon: <ShieldCheck className="w-4 h-4 shrink-0" />,
      },
      {
        id: 'cohort-analytics',
        label: 'Cohort Insights',
        icon: <TrendingUp className="w-4 h-4 shrink-0" />,
      },
      {
        id: 'outcomes',
        label: 'Placement Ledger',
        icon: <Award className="w-4 h-4 shrink-0" />,
      },
      {
        id: 'training',
        label: 'Training Impact',
        icon: <Building2 className="w-4 h-4 shrink-0" />,
      },
      {
        id: 'practice',
        label: 'Assessment Catalog',
        icon: <Brain className="w-4 h-4 shrink-0" />,
      },
      {
        id: 'catalog',
        label: 'Curriculum Overview',
        icon: <Compass className="w-4 h-4 shrink-0" />,
      },
    ];
  };

  const navItems = getNavItems();

  const handleItemClick = (id: ViewMode) => {
    onViewChange(id);
    setMobileDrawerOpen(false);
  };

  const getCurrentPageTitle = (): { section: string; title: string } => {
    switch (currentView) {
      case 'workspace':
        return { section: 'Student Portal', title: 'Preparation Overview' };
      case 'practice':
        return { section: 'Practice Engine', title: 'Diagnostic Assessments' };
      case 'results':
        return { section: 'Practice Engine', title: 'Attempt Evaluation' };
      case 'mistakes':
        return { section: 'Learning Diagnostics', title: 'Mistake Notebook' };
      case 'analytics':
        return { section: 'Analytics', title: 'Skill Progress & Analytics' };
      case 'readiness':
        return { section: 'Career Pathways', title: 'Role Readiness' };
      case 'outcomes':
        return { section: 'Institutional Records', title: 'Placement Journey' };
      case 'training':
        return { section: 'Institutional Records', title: 'Training Progress' };
      case 'cohort-analytics':
        return { section: 'Department Intelligence', title: 'Cohort Insights' };
      case 'admin':
        return { section: 'Administration', title: 'College Intelligence Console' };
      case 'catalog':
        return { section: 'Curriculum', title: 'Learning Resources' };
      default:
        return { section: 'Placement Portal', title: 'Workspace' };
    }
  };

  const pageInfo = getCurrentPageTitle();

  return (
    <div className="min-h-screen bg-[#FAF6ED] flex flex-col font-sans text-[#292444] selection:bg-[#FF5B3D]/20 selection:text-[#292444]">
      {/* ========================================================================= */}
      {/* DESKTOP SIDEBAR (Fixed left, width 260px)                                  */}
      {/* ========================================================================= */}
      <aside
        className="hidden lg:flex flex-col fixed top-0 bottom-0 left-0 w-[260px] bg-white border-r border-[#E8E0D2] z-30"
        aria-label="Sidebar Navigation"
      >
        {/* Brand Header */}
        <div className="h-16 px-5 border-b border-[#E8E0D2] flex items-center gap-3 shrink-0">
          <div className="w-9 h-9 rounded-xl bg-[#292444] text-[#FAF6ED] flex items-center justify-center font-bold shadow-xs">
            <GraduationCap className="w-5 h-5 text-[#FF5B3D]" />
          </div>
          <div>
            <span className="text-sm font-bold tracking-tight text-[#292444] block leading-tight font-display">
              Placement Portal
            </span>
            <span className="text-[11px] font-medium text-[#5E5875] tracking-wide block">
              Career Preparation
            </span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-[#5E5875]/80">
            Navigation
          </div>
          {navItems.map((item) => {
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleItemClick(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all group ${
                  isActive
                    ? 'bg-[#F5EFE3] text-[#292444] shadow-xs'
                    : 'text-[#5E5875] hover:bg-[#FAF6ED] hover:text-[#292444]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`transition-colors ${
                      isActive ? 'text-[#FF5B3D]' : 'text-[#5E5875] group-hover:text-[#292444]'
                    }`}
                  >
                    {item.icon}
                  </span>
                  <span className="truncate">{item.label}</span>
                </div>
                {isActive && (
                  <span className="w-1.5 h-4 bg-[#FF5B3D] rounded-full shrink-0" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer — User & Sign Out */}
        <div className="p-3 border-t border-[#E8E0D2] bg-[#FAF6ED]/40 shrink-0">
          <div className="p-2.5 rounded-xl bg-white border border-[#E8E0D2] mb-2 shadow-xs">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-[#292444] text-[#FAF6ED] flex items-center justify-center text-xs font-bold shrink-0">
                {currentUser.full_name?.charAt(0) || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-bold text-[#292444] truncate">
                  {currentUser.full_name}
                </div>
                <div className="text-[10px] font-semibold text-[#5E5875] truncate">
                  {currentUser.role}
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={onSignOut}
            className="w-full flex items-center gap-2 px-3 py-2 text-xs font-semibold text-[#5E5875] hover:text-red-600 hover:bg-red-50/60 rounded-xl transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* ========================================================================= */}
      {/* MOBILE / TABLET DRAWER OVERLAY                                            */}
      {/* ========================================================================= */}
      {mobileDrawerOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-[#292444]/40 backdrop-blur-xs transition-opacity"
            onClick={() => setMobileDrawerOpen(false)}
          />

          {/* Drawer content */}
          <aside className="fixed top-0 bottom-0 left-0 w-[270px] bg-white border-r border-[#E8E0D2] flex flex-col z-50 shadow-xl animate-in slide-in-from-left duration-200">
            {/* Drawer Header */}
            <div className="h-16 px-5 border-b border-[#E8E0D2] flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-[#292444] text-[#FAF6ED] flex items-center justify-center font-bold">
                  <GraduationCap className="w-4 h-4 text-[#FF5B3D]" />
                </div>
                <span className="text-sm font-bold text-[#292444] font-display">
                  Placement Portal
                </span>
              </div>
              <button
                onClick={() => setMobileDrawerOpen(false)}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-[#5E5875] hover:bg-[#FAF6ED] hover:text-[#292444]"
                aria-label="Close navigation"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Nav list */}
            <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
              {navItems.map((item) => {
                const isActive = currentView === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleItemClick(item.id)}
                    className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-[#F5EFE3] text-[#292444]'
                        : 'text-[#5E5875] hover:bg-[#FAF6ED] hover:text-[#292444]'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className={isActive ? 'text-[#FF5B3D]' : 'text-[#5E5875]'}>
                        {item.icon}
                      </span>
                      <span>{item.label}</span>
                    </div>
                    {isActive && (
                      <span className="w-1.5 h-4 bg-[#FF5B3D] rounded-full shrink-0" />
                    )}
                  </button>
                );
              })}
            </nav>

            {/* Drawer Footer */}
            <div className="p-3 border-t border-[#E8E0D2] bg-[#FAF6ED]/40 shrink-0">
              <div className="p-2.5 rounded-xl bg-white border border-[#E8E0D2] mb-2">
                <div className="text-xs font-bold text-[#292444] truncate">
                  {currentUser.full_name}
                </div>
                <div className="text-[10px] text-[#5E5875]">{currentUser.role}</div>
              </div>
              <button
                onClick={() => {
                  setMobileDrawerOpen(false);
                  onSignOut();
                }}
                className="w-full flex items-center gap-2 px-3 py-2 text-xs font-semibold text-red-600 hover:bg-red-50 rounded-xl"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Sign Out</span>
              </button>
            </div>
          </aside>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MAIN CONTAINER (OFFSET BY SIDEBAR ON DESKTOP)                              */}
      {/* ========================================================================= */}
      <div className="lg:pl-[260px] flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="sticky top-0 z-20 h-16 bg-[#FAF6ED]/90 backdrop-blur-md border-b border-[#E8E0D2] px-4 sm:px-6 lg:px-8 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            {/* Mobile menu trigger */}
            <button
              onClick={() => setMobileDrawerOpen(true)}
              className="lg:hidden w-9 h-9 rounded-xl border border-[#E8E0D2] bg-white flex items-center justify-center text-[#292444] hover:bg-[#FAF6ED]"
              aria-label="Open navigation menu"
            >
              <Menu className="w-4 h-4" />
            </button>

            {/* Breadcrumb / Page Title */}
            <div className="flex items-center gap-2 text-xs text-[#5E5875]">
              <span className="hidden sm:inline font-medium">{pageInfo.section}</span>
              <ChevronRight className="hidden sm:inline w-3.5 h-3.5 text-[#5E5875]/40" />
              <span className="font-bold text-[#292444] text-sm sm:text-base font-display">
                {pageInfo.title}
              </span>
            </div>
          </div>

          {/* Header Right Actions */}
          <div className="flex items-center gap-3">
            {currentUser.role === 'STUDENT' && onStartPractice && currentView !== 'practice' && (
              <Button
                variant="primary"
                size="sm"
                onClick={onStartPractice}
                leftIcon={<Sparkles className="w-3.5 h-3.5" />}
                className="text-xs shadow-xs"
              >
                <span className="hidden sm:inline">Start Practice</span>
                <span className="sm:hidden">Practice</span>
              </Button>
            )}

            <div className="hidden sm:flex items-center gap-2 pl-3 border-l border-[#E8E0D2]">
              <span className="text-[11px] font-semibold text-[#5E5875] font-mono">
                {currentUser.email}
              </span>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          {children}
        </main>
      </div>
    </div>
  );
};
