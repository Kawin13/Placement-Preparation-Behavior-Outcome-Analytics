import { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Card } from './components/common/Card';
import { Badge } from './components/common/Badge';
import { Button } from './components/common/Button';
import {
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Calculator,
  BookOpen,
  Terminal,
  Database,
  Timer,
  MessageSquare,
  CheckSquare,
  Brain,
  Layers,
  BookOpenCheck,
  ShieldCheck,
  TrendingUp,
  Target,
  Clock,
  FileCheck,
  GraduationCap,
} from 'lucide-react';
import { AuthModal } from './components/auth/AuthModal';
import { StudentWorkspace } from './components/student/StudentWorkspace';
import { PracticeModuleList } from './components/practice/PracticeModuleList';
import { PracticeRunner } from './components/practice/PracticeRunner';
import { PracticeResultsDrawer } from './components/practice/PracticeResultsDrawer';
import { MistakeNotebookView } from './components/practice/MistakeNotebookView';
import { StudentAnalyticsView } from './components/analytics/StudentAnalyticsView';
import { CohortAnalyticsView } from './components/analytics/CohortAnalyticsView';
import { RoleReadinessView } from './components/readiness/RoleReadinessView';
import { AICoachModal } from './components/coach/AICoachModal';
import { PlacementOutcomesView } from './components/placement/PlacementOutcomesView';
import { TrainingEffectivenessView } from './components/training/TrainingEffectivenessView';
import { CollegeIntelligenceView } from './components/admin/CollegeIntelligenceView';
import { AppShell, type ViewMode } from './components/layout/AppShell';
import { LearningResourcesView } from './components/catalog/LearningResourcesView';
import { DSAProblemListView } from './components/dsa/DSAProblemListView';
import { DSACodingWorkspace } from './components/dsa/DSACodingWorkspace';
import { CareerRoadmapView } from './components/roadmap/CareerRoadmapView';
import { TopicDetailView } from './components/roadmap/TopicDetailView';
import { QuestionBankManager } from './components/practice/QuestionBankManager';
import { fetchHealthTelemetry } from './services/api';
import { getStoredUser, removeStoredToken, type UserSummary } from './services/auth';
import {
  startPracticeSession,
  type ActiveSession,
  type SubmitResult,
} from './services/practice';

export function App() {
  const [systemStatus, setSystemStatus] = useState<'connected' | 'checking' | 'error'>('checking');
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'signin' | 'register'>('signin');
  const [currentUser, setCurrentUser] = useState<UserSummary | null>(null);

  // Active View Router
  const [viewMode, setViewMode] = useState<ViewMode>('workspace');

  const [selectedDsaSlug, setSelectedDsaSlug] = useState<string | null>(null);
  const [selectedTopicId, setSelectedTopicId] = useState<string | null>(null);

  // Topic-Wise Practice Navigation Filter State
  const [selectedPracticeCategory, setSelectedPracticeCategory] = useState<string | null>(null);
  const [selectedPracticeTopic, setSelectedPracticeTopic] = useState<string | null>(null);

  // Active Practice Execution State
  const [activeSession, setActiveSession] = useState<ActiveSession | null>(null);
  const [submitResult, setSubmitResult] = useState<SubmitResult | null>(null);

  // Grounded AI Learning Coach State
  const [isCoachModalOpen, setIsCoachModalOpen] = useState(false);
  const [coachQuestionContext, setCoachQuestionContext] = useState<any>(null);
  const [coachTargetRoleId, setCoachTargetRoleId] = useState<string>('SDE');

  const handleSelectTrack = (trackId: string, topicName?: string) => {
    if (trackId === 'dsa') {
      setSelectedDsaSlug(null);
      setViewMode('dsa');
    } else {
      const categoryMap: Record<string, string> = {
        quant: 'QUANTITATIVE_APTITUDE',
        logical: 'LOGICAL_REASONING',
        verbal: 'VERBAL_ABILITY',
        sql: 'SQL_DATABASES',
        hr: 'HR_BEHAVIORAL',
      };
      setSelectedPracticeCategory(categoryMap[trackId] || 'ALL');
      setSelectedPracticeTopic(topicName || 'ALL');
      setViewMode('practice');
    }
  };

  useEffect(() => {
    // Check local session
    const user = getStoredUser();
    if (user) {
      setCurrentUser(user);
      const initialView: ViewMode =
        user.role === 'ADMIN'
          ? 'admin'
          : user.role === 'PLACEMENT_OFFICER'
          ? 'outcomes'
          : user.role === 'TRAINER'
          ? 'training'
          : 'workspace';
      setViewMode(initialView);
    }

    // Ping health telemetry
    fetchHealthTelemetry()
      .then(() => {
        setSystemStatus('connected');
      })
      .catch(() => {
        setSystemStatus('error');
      });
  }, []);

  const handleAuthSuccess = (user: UserSummary) => {
    setCurrentUser(user);
    const initialView: ViewMode =
      user.role === 'ADMIN'
        ? 'admin'
        : user.role === 'PLACEMENT_OFFICER'
        ? 'outcomes'
        : user.role === 'TRAINER'
        ? 'training'
        : 'workspace';
    setViewMode(initialView);
    setIsAuthModalOpen(false);
  };

  const handleSignOut = () => {
    removeStoredToken();
    setCurrentUser(null);
    setViewMode('workspace');
    setActiveSession(null);
    setSubmitResult(null);
  };

  const handleStartSession = async (assessmentId: string, sessionType: 'PRACTICE' | 'TIMED_MOCK') => {
    try {
      const session = await startPracticeSession(assessmentId, sessionType);
      setActiveSession(session);
      setViewMode('running');
    } catch (err: any) {
      alert(err.message || 'Failed to start practice session');
    }
  };

  const handleSessionSubmitted = (result: SubmitResult) => {
    setSubmitResult(result);
    setViewMode('results');
  };

  const modules = [
    {
      id: 'quant',
      title: 'Quantitative Aptitude',
      desc: 'Arithmetic, Algebra, Geometry, and Data Interpretation with step-by-step proofs.',
      icon: <Calculator className="w-5 h-5 text-[#FF5B3D]" />,
      topics: '14 Core Topics',
    },
    {
      id: 'logical',
      title: 'Logical Reasoning',
      desc: 'Deductive reasoning, arrangements, syllogisms, and sequence validation matrices.',
      icon: <BookOpen className="w-5 h-5 text-[#292444]" />,
      topics: '11 Core Topics',
    },
    {
      id: 'verbal',
      title: 'Verbal Ability',
      desc: 'Reading comprehension, contextual vocabulary, and sentence rearrangement.',
      icon: <MessageSquare className="w-5 h-5 text-[#FF5B3D]" />,
      topics: '9 Core Topics',
    },
    {
      id: 'dsa',
      title: 'Programming & DSA',
      desc: 'Recurrence relations, dynamic programming, stacks, trees, and algorithmic complexity.',
      icon: <Terminal className="w-5 h-5 text-[#292444]" />,
      topics: '8 Core Topics',
    },
    {
      id: 'sql',
      title: 'SQL & Database Queries',
      desc: 'Complex joins, aggregations, anti-joins, window ranking, and schema validation.',
      icon: <Database className="w-5 h-5 text-[#FF5B3D]" />,
      topics: '6 Core Topics',
    },
    {
      id: 'mocks',
      title: 'Timed Placement Mocks',
      desc: 'Simulated recruitment rounds with strict section timers and full diagnostic scoring.',
      icon: <Timer className="w-5 h-5 text-[#292444]" />,
      topics: 'Full Round Drills',
    },
    {
      id: 'star',
      title: 'HR & Behavioral Practice',
      desc: 'Structured STAR methodology for situational, leadership, and ethical questions.',
      icon: <CheckSquare className="w-5 h-5 text-[#FF5B3D]" />,
      topics: 'STAR Framework',
    },
    {
      id: 'audit',
      title: 'Placement Verification',
      desc: 'Placement cell verification pipeline linking authentic practice to verified hiring tiers.',
      icon: <CheckCircle2 className="w-5 h-5 text-[#15803D]" />,
      topics: 'Accreditation',
    },
  ];

  // Authenticated Application Shell (Left Sidebar + Header)
  if (currentUser) {
    if (viewMode === 'running' && activeSession) {
      return (
        <div className="min-h-screen bg-[#FAF6ED] flex flex-col font-sans text-[#292444] p-4 sm:p-6 lg:p-8">
          <PracticeRunner
            session={activeSession}
            onSessionSubmitted={handleSessionSubmitted}
            onExit={() => setViewMode('practice')}
          />
        </div>
      );
    }

    return (
      <>
        <AppShell
          currentUser={currentUser}
          currentView={viewMode}
          onViewChange={(view) => {
            if (view !== 'dsa') setSelectedDsaSlug(null);
            if (view !== 'roadmap') setSelectedTopicId(null);
            setViewMode(view);
          }}
          onSignOut={handleSignOut}
          onStartPractice={() => setViewMode('practice')}
        >
          {viewMode === 'workspace' && <StudentWorkspace />}
          {viewMode === 'roadmap' && (
            selectedTopicId ? (
              <TopicDetailView
                topicId={selectedTopicId}
                onBack={() => setSelectedTopicId(null)}
                onSelectDsaProblem={(slug) => {
                  setSelectedDsaSlug(slug);
                  setViewMode('dsa');
                }}
                onPracticeQuestions={(topicName) => {
                  if (topicName) {
                    setSelectedPracticeTopic(topicName);
                  }
                  setViewMode('practice');
                }}
                onStartAssessment={(assessmentId) => {
                  handleStartSession(assessmentId, 'PRACTICE');
                }}
              />
            ) : (
              <CareerRoadmapView
                onSelectTopic={(tId) => setSelectedTopicId(tId)}
                onLaunchDsa={(slug) => {
                  setSelectedDsaSlug(slug);
                  setViewMode('dsa');
                }}
                onStartPractice={() => setViewMode('practice')}
                onReviewMistakes={() => setViewMode('mistakes')}
              />
            )
          )}
          {viewMode === 'qbank' && <QuestionBankManager />}
          {viewMode === 'practice' && (
            <PracticeModuleList
              onStartSession={handleStartSession}
              initialCategory={selectedPracticeCategory}
              initialTopic={selectedPracticeTopic}
              onClearFilter={() => {
                setSelectedPracticeCategory(null);
                setSelectedPracticeTopic(null);
              }}
              onLaunchDsa={(slug) => {
                setSelectedDsaSlug(slug || null);
                setViewMode('dsa');
              }}
            />
          )}
          {viewMode === 'dsa' && (
            selectedDsaSlug ? (
              <DSACodingWorkspace
                problemSlug={selectedDsaSlug}
                onBack={() => setSelectedDsaSlug(null)}
              />
            ) : (
              <DSAProblemListView
                onSelectProblem={(slug) => setSelectedDsaSlug(slug)}
              />
            )
          )}
          {viewMode === 'results' && submitResult && (
            <PracticeResultsDrawer
              result={submitResult}
              onGoToWorkspace={() => setViewMode('workspace')}
              onGoToMistakes={() => setViewMode('mistakes')}
            />
          )}
          {viewMode === 'mistakes' && (
            <MistakeNotebookView
              onAskCoach={(ctx) => {
                setCoachQuestionContext(ctx);
                setIsCoachModalOpen(true);
              }}
            />
          )}
          {viewMode === 'analytics' && <StudentAnalyticsView />}
          {viewMode === 'readiness' && (
            <RoleReadinessView
              onSelectAssessment={(assessmentId) => handleStartSession(assessmentId, 'PRACTICE')}
              onOpenCoachModal={(roleId) => {
                setCoachTargetRoleId(roleId);
                setCoachQuestionContext(null);
                setIsCoachModalOpen(true);
              }}
            />
          )}
          {viewMode === 'outcomes' && <PlacementOutcomesView currentUser={currentUser} />}
          {viewMode === 'training' && <TrainingEffectivenessView currentUser={currentUser} />}
          {viewMode === 'cohort-analytics' && <CohortAnalyticsView />}
          {viewMode === 'admin' && <CollegeIntelligenceView currentUser={currentUser} />}
          {viewMode === 'catalog' && (
            <LearningResourcesView
              onSelectTrack={handleSelectTrack}
              onStartPractice={() => {
                setSelectedPracticeCategory('ALL');
                setSelectedPracticeTopic('ALL');
                setViewMode('practice');
              }}
            />
          )}
        </AppShell>

        {/* Grounded AI Learning Coach Modal */}
        <AICoachModal
          isOpen={isCoachModalOpen}
          onClose={() => setIsCoachModalOpen(false)}
          questionContext={coachQuestionContext}
          targetRoleId={coachTargetRoleId}
          onLaunchAssessment={(assessmentId) => handleStartSession(assessmentId, 'PRACTICE')}
        />
      </>
    );
  }

  // Public Guest & Visitor Landing Page
  return (
    <div className="min-h-screen bg-[#FAF6ED] flex flex-col font-sans text-[#292444] selection:bg-[#FF5B3D]/20 selection:text-[#292444]">
      {/* Header Navigation */}
      <Navbar
        systemStatus={systemStatus}
        currentUser={null}
        onStartPractice={() => {
          setAuthMode('signin');
          setIsAuthModalOpen(true);
        }}
        onSignIn={() => {
          setAuthMode('signin');
          setIsAuthModalOpen(true);
        }}
      />

      {/* Main Public Landing Page Container */}
      <main className="flex-1 max-w-[1240px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">

        {/* Editorial Hero Section */}
            <section className="relative pt-6 pb-16 sm:py-20 lg:py-24">
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
                {/* Hero Left Copy */}
                <div className="lg:col-span-7">
                  {/* Status Pill Badge */}
                  <div className="mb-6 inline-flex">
                    <Badge variant="coral" hasDot className="text-xs uppercase font-bold py-1 px-3">
                      Institutional Career Readiness Platform
                    </Badge>
                  </div>

                  {/* Editorial Headline */}
                  <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-[#292444] leading-[1.08] mb-6 font-display">
                    Prepare with purpose. <br />
                    <span className="text-[#FF5B3D]">Progress with proof.</span>
                  </h1>

                  {/* Supporting Copy */}
                  <p className="text-lg sm:text-xl text-[#5E5875] leading-relaxed mb-8 max-w-xl font-normal">
                    Build the skills that matter for your next opportunity. Practise real placement
                    questions, understand your mistakes, and track your progress as you prepare.
                  </p>

                  {/* Primary & Secondary CTAs */}
                  <div className="flex flex-wrap items-center gap-4 mb-8">
                    <Button
                      variant="primary"
                      size="lg"
                      rightIcon={<ArrowRight className="w-4 h-4" />}
                      onClick={() => {
                        if (!currentUser) {
                          setAuthMode('register');
                          setIsAuthModalOpen(true);
                        } else {
                          setViewMode('practice');
                        }
                      }}
                      className="shadow-warm font-semibold text-base px-7 py-3.5"
                    >
                      {currentUser ? 'Go to Practice Engine' : 'Start Practising'}
                    </Button>
                    <Button
                      variant="secondary"
                      size="lg"
                      onClick={() => {
                        const el = document.getElementById('features');
                        el?.scrollIntoView({ behavior: 'smooth' });
                      }}
                      className="font-semibold text-base px-6 py-3.5"
                    >
                      Explore Features
                    </Button>
                  </div>

                  {/* Credibility reassurance */}
                  <div className="flex flex-wrap items-center gap-6 text-xs text-[#8E879E]">
                    <div className="flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>Authentic question banks</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>Zero invented statistics</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>College-approved diagnostics</span>
                    </div>
                  </div>
                </div>

                {/* Hero Right: Authentic Student Preparation Photo */}
                <div className="lg:col-span-5">
                  <div className="relative mx-auto max-w-md lg:max-w-none">
                    {/* Ambient warm canvas glow to blend into page */}
                    <div className="absolute -inset-4 bg-gradient-to-tr from-[#FF5B3D]/15 via-[#FAF6ED] to-[#292444]/10 rounded-[36px] blur-2xl opacity-90 pointer-events-none" />

                    {/* Seamlessly Integrated Image Container */}
                    <div className="relative rounded-3xl overflow-hidden border border-[#E8E0D2] shadow-[0_20px_50px_rgba(41,36,68,0.12)] bg-[#FAF6ED] group">
                      <div className="relative aspect-[4/3] sm:aspect-[16/11] overflow-hidden">
                        <img
                          src="/hero_students.webp"
                          alt="Students collaborating and preparing for placement drives"
                          className="w-full h-full object-cover object-center transition-transform duration-700 ease-out group-hover:scale-[1.03]"
                          loading="eager"
                        />
                        {/* Soft inner vignette border */}
                        <div className="absolute inset-0 rounded-3xl ring-1 ring-inset ring-black/5 pointer-events-none" />

                        {/* Floating Credibility Pill attached to the image */}
                        <div className="absolute bottom-4 left-4 right-4 sm:right-auto bg-white/95 backdrop-blur-md px-3.5 py-2.5 rounded-xl border border-[#E8E0D2] shadow-sm flex items-center gap-2.5">
                          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0" />
                          <div className="text-[11px] leading-tight text-[#292444]">
                            <span className="font-bold block">Collaborative Preparation</span>
                            <span className="text-[#5E5875]">Authentic practice · Peer review</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Trust & Credibility Value Strip */}
            <section id="features" className="mb-20 sm:mb-28 scroll-mt-24">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                <Card className="p-6 bg-white border border-[#E8E0D2] shadow-xs rounded-2xl flex flex-col justify-between">
                  <div>
                    <div className="w-10 h-10 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D] mb-4">
                      <BookOpen className="w-5 h-5" />
                    </div>
                    <h3 className="text-base font-bold text-[#292444] mb-1.5 font-display">
                      Curated Question Sets
                    </h3>
                    <p className="text-xs text-[#5E5875] leading-relaxed">
                      Placement diagnostics across Quantitative Aptitude, Logical Reasoning, Verbal
                      Ability, and Core Engineering.
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-[#E8E0D2]/60 text-[11px] font-semibold text-[#8E879E]">
                    Authentic Problem Banks
                  </div>
                </Card>

                <Card className="p-6 bg-white border border-[#E8E0D2] shadow-xs rounded-2xl flex flex-col justify-between">
                  <div>
                    <div className="w-10 h-10 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#292444] mb-4">
                      <Brain className="w-5 h-5" />
                    </div>
                    <h3 className="text-base font-bold text-[#292444] mb-1.5 font-display">
                      Step-by-Step Proofs
                    </h3>
                    <p className="text-xs text-[#5E5875] leading-relaxed">
                      Every diagnostic question features complete mathematical derivations, logic
                      models, and algorithmic explanations.
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-[#E8E0D2]/60 text-[11px] font-semibold text-[#8E879E]">
                    Zero Guesswork Feedback
                  </div>
                </Card>

                <Card className="p-6 bg-white border border-[#E8E0D2] shadow-xs rounded-2xl flex flex-col justify-between">
                  <div>
                    <div className="w-10 h-10 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D] mb-4">
                      <TrendingUp className="w-5 h-5" />
                    </div>
                    <h3 className="text-base font-bold text-[#292444] mb-1.5 font-display">
                      Honest Skill Diagnostics
                    </h3>
                    <p className="text-xs text-[#5E5875] leading-relaxed">
                      Skill evaluations are calculated strictly from authenticated attempts. Scores
                      require minimum sample sizes to prevent bias.
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-[#E8E0D2]/60 text-[11px] font-semibold text-[#8E879E]">
                    Defensible Evidence Rules
                  </div>
                </Card>

                <Card className="p-6 bg-white border border-[#E8E0D2] shadow-xs rounded-2xl flex flex-col justify-between">
                  <div>
                    <div className="w-10 h-10 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#15803D] mb-4">
                      <BookOpenCheck className="w-5 h-5" />
                    </div>
                    <h3 className="text-base font-bold text-[#292444] mb-1.5 font-display">
                      Mistake Notebook
                    </h3>
                    <p className="text-xs text-[#5E5875] leading-relaxed">
                      Questions missed during practice are automatically cataloged with personal notes
                      and grounded learning reflections.
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-[#E8E0D2]/60 text-[11px] font-semibold text-[#8E879E]">
                    Targeted Remediation
                  </div>
                </Card>
              </div>
            </section>

            {/* Varied Feature Section: How the Platform Helps You Succeed */}
            <section className="mb-20 sm:mb-28">
              <div className="max-w-2xl mb-12">
                <Badge variant="neutral" className="mb-3 text-xs uppercase font-bold tracking-wider">
                  Comprehensive Learning Architecture
                </Badge>
                <h2 className="text-3xl sm:text-4xl font-extrabold text-[#292444] font-display tracking-tight mb-4">
                  Everything you need to prepare with confidence.
                </h2>
                <p className="text-[#5E5875] text-base leading-relaxed">
                  A structured preparation workflow that turns formative practice into measurable,
                  verifiable career readiness.
                </p>
              </div>

              {/* Asymmetric 6-Feature Layout */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Feature 1: Focused Practice */}
                <Card className="p-7 bg-white border border-[#E8E0D2] rounded-3xl shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="w-11 h-11 rounded-2xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D] mb-5">
                      <Layers className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-bold text-[#292444] mb-2 font-display">
                      Focused Practice
                    </h3>
                    <p className="text-sm text-[#5E5875] leading-relaxed mb-6">
                      Work through placement questions by skill and topic. Practice individual
                      competencies or complete full timed recruitment mocks.
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-4 border-t border-[#E8E0D2]">
                    <span className="text-[11px] font-semibold bg-[#FAF6ED] text-[#292444] px-2.5 py-1 rounded-full border border-[#E8E0D2]">
                      Quantitative
                    </span>
                    <span className="text-[11px] font-semibold bg-[#FAF6ED] text-[#292444] px-2.5 py-1 rounded-full border border-[#E8E0D2]">
                      Logical
                    </span>
                    <span className="text-[11px] font-semibold bg-[#FAF6ED] text-[#292444] px-2.5 py-1 rounded-full border border-[#E8E0D2]">
                      Verbal
                    </span>
                    <span className="text-[11px] font-semibold bg-[#FAF6ED] text-[#292444] px-2.5 py-1 rounded-full border border-[#E8E0D2]">
                      DSA
                    </span>
                  </div>
                </Card>

                {/* Feature 2: Learn from Mistakes */}
                <Card className="p-7 bg-white border border-[#E8E0D2] rounded-3xl shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="w-11 h-11 rounded-2xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#292444] mb-5">
                      <BookOpenCheck className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-bold text-[#292444] mb-2 font-display">
                      Learn from Mistakes
                    </h3>
                    <p className="text-sm text-[#5E5875] leading-relaxed mb-6">
                      Review your answers and understand where you can improve. Track unresolved vs
                      mastered concepts, record personal notes, and consult the grounded coach.
                    </p>
                  </div>
                  <div className="bg-[#FAF6ED] p-3 rounded-2xl border border-[#E8E0D2] text-xs space-y-1">
                    <span className="text-[10px] uppercase font-bold text-[#FF5B3D] tracking-wider block">
                      Active Reflection
                    </span>
                    <p className="text-[#292444] font-medium">
                      Categorize recurring errors by formula or time management.
                    </p>
                  </div>
                </Card>

                {/* Feature 3: Track Your Progress */}
                <Card className="p-7 bg-white border border-[#E8E0D2] rounded-3xl shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="w-11 h-11 rounded-2xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-emerald-700 mb-5">
                      <TrendingUp className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-bold text-[#292444] mb-2 font-display">
                      Track Your Progress
                    </h3>
                    <p className="text-sm text-[#5E5875] leading-relaxed mb-6">
                      See how your performance changes across completed practice sessions. Clear
                      separation of platform measured time from self-reported study.
                    </p>
                  </div>
                  <div className="pt-4 border-t border-[#E8E0D2] flex items-center justify-between text-xs text-[#5E5875]">
                    <span>Cadence Tracking</span>
                    <span className="font-semibold text-[#292444]">Daily Active Minutes</span>
                  </div>
                </Card>

                {/* Feature 4: Identify Skill Gaps */}
                <Card className="p-7 bg-white border border-[#E8E0D2] rounded-3xl shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="w-11 h-11 rounded-2xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-indigo-700 mb-5">
                      <Brain className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-bold text-[#292444] mb-2 font-display">
                      Identify Skill Gaps
                    </h3>
                    <p className="text-sm text-[#5E5875] leading-relaxed mb-6">
                      Discover the topics that need more attention based on your attempts. Difficulty-weighted
                      gap index highlights deficits before college interviews.
                    </p>
                  </div>
                  <div className="pt-4 border-t border-[#E8E0D2] flex items-center justify-between text-xs text-[#5E5875]">
                    <span>Evidence Requirement</span>
                    <span className="font-semibold text-[#292444]">≥ 5 Attempts per Domain</span>
                  </div>
                </Card>

                {/* Feature 5: Prepare for Interviews */}
                <Card className="p-7 bg-white border border-[#E8E0D2] rounded-3xl shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="w-11 h-11 rounded-2xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-amber-700 mb-5">
                      <Target className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-bold text-[#292444] mb-2 font-display">
                      Role Competency Pathways
                    </h3>
                    <p className="text-sm text-[#5E5875] leading-relaxed mb-6">
                      Evaluate your readiness against real industry roles including Software Development
                      Engineer, Data Analyst / SQL Specialist, and Core Technology Graduate.
                    </p>
                  </div>
                  <div className="pt-4 border-t border-[#E8E0D2] flex items-center justify-between text-xs text-[#5E5875]">
                    <span>Target Roles</span>
                    <span className="font-semibold text-[#FF5B3D]">3 Approved Frameworks</span>
                  </div>
                </Card>

                {/* Feature 6: Personalised Next Steps */}
                <Card className="p-7 bg-white border border-[#E8E0D2] rounded-3xl shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="w-11 h-11 rounded-2xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D] mb-5">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-bold text-[#292444] mb-2 font-display">
                      Personalised Next Steps
                    </h3>
                    <p className="text-sm text-[#5E5875] leading-relaxed mb-6">
                      Find relevant practice activities based on your learning goals and available
                      performance evidence. Launch targeted drills directly from skill deficit notices.
                    </p>
                  </div>
                  <div className="pt-4 border-t border-[#E8E0D2] flex items-center justify-between text-xs text-[#5E5875]">
                    <span>Catalogue Link</span>
                    <span className="font-semibold text-[#292444]">1-Click Drill Launcher</span>
                  </div>
                </Card>
              </div>
            </section>

            {/* How It Works Section */}
            <section id="how-it-works" className="mb-20 sm:mb-28 scroll-mt-24">
              <div className="max-w-2xl mb-12">
                <Badge variant="neutral" className="mb-3 text-xs uppercase font-bold tracking-wider">
                  Preparation Journey
                </Badge>
                <h2 className="text-3xl sm:text-4xl font-extrabold text-[#292444] font-display tracking-tight mb-4">
                  How it works.
                </h2>
                <p className="text-[#5E5875] text-base leading-relaxed">
                  Three straightforward steps designed to build genuine problem-solving ability.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="p-8 bg-white border border-[#E8E0D2] rounded-3xl shadow-sm relative overflow-hidden">
                  <span className="text-5xl font-black text-[#FAF6ED] font-display absolute top-4 right-6 pointer-events-none select-none">
                    01
                  </span>
                  <div className="w-10 h-10 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D] font-bold mb-6 text-sm">
                    01
                  </div>
                  <h3 className="text-xl font-bold text-[#292444] mb-3 font-display">
                    Choose your focus.
                  </h3>
                  <p className="text-sm text-[#5E5875] leading-relaxed">
                    Select a skill, topic, or preparation track aligned with your upcoming recruitment
                    drives. Choose formative mastery drills or timed exam simulations.
                  </p>
                </Card>

                <Card className="p-8 bg-white border border-[#E8E0D2] rounded-3xl shadow-sm relative overflow-hidden">
                  <span className="text-5xl font-black text-[#FAF6ED] font-display absolute top-4 right-6 pointer-events-none select-none">
                    02
                  </span>
                  <div className="w-10 h-10 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#292444] font-bold mb-6 text-sm">
                    02
                  </div>
                  <h3 className="text-xl font-bold text-[#292444] mb-3 font-display">
                    Practise and review.
                  </h3>
                  <p className="text-sm text-[#5E5875] leading-relaxed">
                    Complete activities and learn from feedback based on your actual responses. Study
                    step-by-step mathematical proofs and understand the underlying principles.
                  </p>
                </Card>

                <Card className="p-8 bg-white border border-[#E8E0D2] rounded-3xl shadow-sm relative overflow-hidden">
                  <span className="text-5xl font-black text-[#FAF6ED] font-display absolute top-4 right-6 pointer-events-none select-none">
                    03
                  </span>
                  <div className="w-10 h-10 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-emerald-700 font-bold mb-6 text-sm">
                    03
                  </div>
                  <h3 className="text-xl font-bold text-[#292444] mb-3 font-display">
                    Build your progress.
                  </h3>
                  <p className="text-sm text-[#5E5875] leading-relaxed">
                    Review your preparation history, resolve items in your Mistake Notebook, and evaluate
                    your readiness against approved role frameworks.
                  </p>
                </Card>
              </div>
            </section>

            {/* Curated Placement Tracks Section */}
            <section id="tracks" className="mb-20 sm:mb-28 scroll-mt-24">
              <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-10 gap-4">
                <div>
                  <Badge variant="neutral" className="mb-2 text-xs uppercase font-bold tracking-wider">
                    Structured Curriculum
                  </Badge>
                  <h2 className="text-3xl font-bold text-[#292444] font-display">
                    Curated Placement Tracks
                  </h2>
                </div>
                <p className="text-sm text-[#5E5875] max-w-md">
                  Each track is grounded in verified institutional question banks with deterministic
                  scoring and step-by-step proofs.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {modules.map((m) => (
                  <Card
                    key={m.id}
                    isHoverable
                    onClick={() => {
                      if (!currentUser) {
                        setAuthMode('signin');
                        setIsAuthModalOpen(true);
                      } else {
                        setViewMode('practice');
                      }
                    }}
                    className="flex flex-col justify-between p-6 bg-white border border-[#E8E0D2] rounded-3xl shadow-xs"
                  >
                    <div>
                      <div className="w-10 h-10 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center mb-4">
                        {m.icon}
                      </div>
                      <h3 className="text-base font-bold text-[#292444] mb-2 font-display">{m.title}</h3>
                      <p className="text-xs text-[#5E5875] leading-relaxed mb-6">{m.desc}</p>
                    </div>

                    <div className="pt-4 border-t border-[#E8E0D2] flex items-center justify-between text-[11px] font-semibold text-[#8E879E]">
                      <span>{m.topics}</span>
                      <span className="text-[#FF5B3D] flex items-center gap-1">
                        Practise <ArrowRight className="w-3 h-3" />
                      </span>
                    </div>
                  </Card>
                ))}
              </div>
            </section>

            {/* Institutional Oversight & Data Governance Strip */}
            <section id="institutions" className="mb-20 sm:mb-28 scroll-mt-24">
              <Card className="p-8 sm:p-10 bg-white border border-[#E8E0D2] rounded-3xl shadow-sm">
                <div className="max-w-2xl mb-8">
                  <Badge variant="coral" className="mb-3 text-xs uppercase font-bold tracking-wider">
                    Institutional Governance
                  </Badge>
                  <h2 className="text-2xl sm:text-3xl font-bold text-[#292444] font-display mb-3">
                    Built for colleges, placement cells, and academic departments.
                  </h2>
                  <p className="text-sm text-[#5E5875] leading-relaxed">
                    Designed from the ground up for defensibility, transparent student record-keeping,
                    and non-causal outcome auditing.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 border-t border-[#E8E0D2]">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <FileCheck className="w-4 h-4 text-[#FF5B3D]" />
                      <h3 className="text-sm font-bold text-[#292444]">Verified Placement Ledger</h3>
                    </div>
                    <p className="text-xs text-[#5E5875] leading-relaxed">
                      Administrative verification workflow with proof documentation, preventing unverified
                      or duplicate self-reports from inflating college metrics.
                    </p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-emerald-700" />
                      <h3 className="text-sm font-bold text-[#292444]">Student Privacy & Isolation</h3>
                    </div>
                    <p className="text-xs text-[#5E5875] leading-relaxed">
                      Cohort analytics require minimum aggregation sizes to protect individual student
                      identity. Cross-institution data leakage is strictly blocked.
                    </p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-indigo-700" />
                      <h3 className="text-sm font-bold text-[#292444]">Defensible Methodology</h3>
                    </div>
                    <p className="text-xs text-[#5E5875] leading-relaxed">
                      Preparation metrics and placement outcomes are strictly reported observationally,
                      avoiding misleading causal attribution claims.
                    </p>
                  </div>
                </div>
              </Card>
            </section>

            {/* Final Call to Action Section */}
            <section className="mb-16 sm:mb-20">
              <div className="bg-[#292444] rounded-3xl p-8 sm:p-14 text-white text-center relative overflow-hidden shadow-warm-lg">
                {/* Decorative background glow */}
                <div className="absolute -top-24 -left-24 w-72 h-72 bg-[#FF5B3D]/20 rounded-full blur-3xl pointer-events-none" />
                <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-[#FAF6ED]/10 rounded-full blur-3xl pointer-events-none" />

                <div className="relative z-10 max-w-2xl mx-auto space-y-6">
                  <h2 className="text-3xl sm:text-5xl font-extrabold font-display tracking-tight text-white leading-tight">
                    Your next opportunity starts with what you practise today.
                  </h2>
                  <p className="text-base text-white/80 leading-relaxed max-w-xl mx-auto">
                    Build your skills one focused session at a time. Join verified placement preparation
                    grounded in real problem-solving.
                  </p>
                  <div className="pt-2 flex flex-wrap items-center justify-center gap-4">
                    <Button
                      variant="primary"
                      size="lg"
                      rightIcon={<Sparkles className="w-4 h-4" />}
                      onClick={() => {
                        if (!currentUser) {
                          setAuthMode('register');
                          setIsAuthModalOpen(true);
                        } else {
                          setViewMode('practice');
                        }
                      }}
                      className="px-8 py-4 text-base font-bold shadow-warm"
                    >
                      Start Practising
                    </Button>
                    {!currentUser && (
                      <Button
                        variant="outline"
                        size="lg"
                        onClick={() => {
                          setAuthMode('signin');
                          setIsAuthModalOpen(true);
                        }}
                        className="px-8 py-4 text-base font-semibold text-white border-white/20 hover:bg-white/10"
                      >
                        Student Sign In
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </section>
      </main>

      {/* Authentication Modal Dialog */}
      <AuthModal
        isOpen={isAuthModalOpen}
        initialMode={authMode}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />

      {/* Grounded AI Learning Coach Modal */}
      <AICoachModal
        isOpen={isCoachModalOpen}
        onClose={() => setIsCoachModalOpen(false)}
        questionContext={coachQuestionContext}
        targetRoleId={coachTargetRoleId}
        onLaunchAssessment={(assessmentId) => handleStartSession(assessmentId, 'PRACTICE')}
      />

      {/* Footer */}
      <footer className="w-full border-t border-[#E8E0D2] bg-white py-12 mt-auto">
        <div className="max-w-[1240px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 pb-8 border-b border-[#E8E0D2]/60">
            <div>
              <div className="flex items-center gap-2.5 mb-2">
                <div className="w-8 h-8 rounded-lg bg-[#292444] text-[#FAF6ED] flex items-center justify-center font-bold">
                  <GraduationCap className="w-4 h-4 text-[#FF5B3D]" />
                </div>
                <span className="text-base font-bold text-[#292444] font-display">
                  Placement Portal
                </span>
              </div>
              <p className="text-xs text-[#5E5875] max-w-sm">
                Dedicated to student career readiness, formative learning intelligence, and verified
                institutional outcomes.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-6 text-xs font-semibold text-[#5E5875]">
              <button
                onClick={() => {
                  const el = document.getElementById('features');
                  el?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="hover:text-[#292444] transition-colors"
              >
                Features
              </button>
              <button
                onClick={() => {
                  const el = document.getElementById('how-it-works');
                  el?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="hover:text-[#292444] transition-colors"
              >
                How It Works
              </button>
              <button
                onClick={() => {
                  const el = document.getElementById('tracks');
                  el?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="hover:text-[#292444] transition-colors"
              >
                Practice Tracks
              </button>
              <button
                onClick={() => {
                  const el = document.getElementById('institutions');
                  el?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="hover:text-[#292444] transition-colors"
              >
                For Institutions
              </button>
              {!currentUser && (
                <button
                  onClick={() => {
                    setAuthMode('signin');
                    setIsAuthModalOpen(true);
                  }}
                  className="hover:text-[#FF5B3D] transition-colors font-bold"
                >
                  Student Sign In
                </button>
              )}
            </div>
          </div>

          <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#8E879E]">
            <p>© 2026 Placement Portal · Institutional Career Readiness & Learning Intelligence.</p>
            <p className="text-center sm:text-right">
              Student Privacy Protected · Observational Outcome Transparency
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
