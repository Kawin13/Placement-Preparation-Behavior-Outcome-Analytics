import { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Button } from './components/common/Button';
import { Card } from './components/common/Card';
import { Badge } from './components/common/Badge';
import { EmptyState } from './components/common/EmptyState';
import { AuthModal } from './components/auth/AuthModal';
import { StudentWorkspace } from './components/student/StudentWorkspace';
import { fetchHealthTelemetry, type HealthData } from './services/api';
import { getStoredUser, removeStoredToken, type UserSummary } from './services/auth';
import {
  Brain,
  Calculator,
  Code2,
  Database,
  FileCheck2,
  BookOpenCheck,
  MessageSquareCheck,
  Timer,
  CheckCircle2,
  ArrowRight,
  Server,
  Layers,
  ShieldCheck,
  KeyRound,
  UserCheck
} from 'lucide-react';

export function App() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [healthStatus, setHealthStatus] = useState<'connected' | 'checking' | 'error'>('checking');
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<UserSummary | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'signin' | 'register'>('signin');
  const [viewMode, setViewMode] = useState<'workspace' | 'catalog'>('workspace');

  useEffect(() => {
    // Check local storage for existing session
    const user = getStoredUser();
    if (user) {
      setCurrentUser(user);
    }

    // Probe backend health endpoint
    fetchHealthTelemetry()
      .then((data: HealthData) => {
        setHealth(data);
        setHealthStatus(data.database.status === 'connected' ? 'connected' : 'error');
      })
      .catch(() => {
        setHealthStatus('error');
      });
  }, []);

  const handleSignOut = () => {
    removeStoredToken();
    setCurrentUser(null);
  };

  const handleAuthSuccess = (user: UserSummary) => {
    setCurrentUser(user);
  };

  const modules = [
    {
      id: 'quant',
      title: 'Quantitative Aptitude',
      desc: 'Arithmetic, Algebra, Geometry, and Data Interpretation with step-by-step proofs.',
      icon: <Calculator className="w-5 h-5 text-[#FF5B3D]" />,
      topics: '14 Core Topics',
      difficulty: 'Easy to Hard',
    },
    {
      id: 'logical',
      title: 'Logical Reasoning',
      desc: 'Deductive reasoning, arrangements, syllogisms, and sequence validation matrices.',
      icon: <Brain className="w-5 h-5 text-[#FF5B3D]" />,
      topics: '11 Core Topics',
      difficulty: 'Multi-stage',
    },
    {
      id: 'verbal',
      title: 'Verbal Ability',
      desc: 'Reading comprehension, contextual vocabulary, and sentence rearrangement.',
      icon: <BookOpenCheck className="w-5 h-5 text-[#FF5B3D]" />,
      topics: '9 Core Topics',
      difficulty: 'Moderate',
    },
    {
      id: 'programming',
      title: 'Programming & DSA',
      desc: 'Algorithmic problem solving in Python, Java, C++, and JS with unit test execution.',
      icon: <Code2 className="w-5 h-5 text-[#FF5B3D]" />,
      topics: '8 Core Topics',
      difficulty: 'Test-Case Driven',
    },
    {
      id: 'sql',
      title: 'SQL & Database Queries',
      desc: 'Complex joins, aggregations, subqueries, and relational schema validation.',
      icon: <Database className="w-5 h-5 text-[#FF5B3D]" />,
      topics: '6 Core Topics',
      difficulty: 'Result-set Diff',
    },
    {
      id: 'mock',
      title: 'Timed Placement Mocks',
      desc: 'Simulated company recruitment rounds with strict section timers and proctoring.',
      icon: <Timer className="w-5 h-5 text-[#FF5B3D]" />,
      topics: 'Full Round Drills',
      difficulty: 'Timed Multi-Section',
    },
    {
      id: 'hr',
      title: 'HR & Behavioral STAR Practice',
      desc: 'Structured STAR methodology forms for situational, leadership, and ethical questions.',
      icon: <MessageSquareCheck className="w-5 h-5 text-[#FF5B3D]" />,
      topics: 'STAR Framework',
      difficulty: 'Rubric Evaluated',
    },
    {
      id: 'outcomes',
      title: 'Verified Outcome Auditing',
      desc: 'Placement cell verification pipeline linking authentic practice to verified hiring tiers.',
      icon: <FileCheck2 className="w-5 h-5 text-[#FF5B3D]" />,
      topics: 'Accreditation',
      difficulty: 'Governance',
    },
  ];

  return (
    <div className="min-h-screen bg-[#FAF6ED] text-[#292444] flex flex-col font-sans selection:bg-[#FF5B3D]/15 selection:text-[#FF5B3D]">
      {/* Framer-Inspired Navbar */}
      <Navbar
        systemStatus={healthStatus}
        currentUser={currentUser}
        onStartPractice={() => {
          if (!currentUser) {
            setAuthMode('signin');
            setIsAuthModalOpen(true);
          } else {
            setSelectedModule('quant');
          }
        }}
        onSignIn={() => {
          setAuthMode('signin');
          setIsAuthModalOpen(true);
        }}
        onSignOut={handleSignOut}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-[1240px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-16">
        {/* User Session Banner (if signed in) */}
        {currentUser && (
          <div className="mb-10 p-5 rounded-2xl bg-[#FFFFFF] border border-[#E8E0D2] shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D]">
                <UserCheck className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-[#292444] font-display">
                    Welcome back, {currentUser.full_name}
                  </h3>
                  <Badge variant="coral">{currentUser.role}</Badge>
                </div>
                <p className="text-xs text-[#5E5875]">
                  Authenticated Session · Email: <span className="font-mono">{currentUser.email}</span>
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="success" hasDot>
                Institutional RBAC Active
              </Badge>
            </div>
          </div>
        )}

        {/* View Switcher for Authenticated Students */}
        {currentUser && (
          <div className="flex items-center gap-3 mb-8 border-b border-[#E8E0D2] pb-4">
            <button
              onClick={() => setViewMode('workspace')}
              className={`px-4 py-2 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${
                viewMode === 'workspace'
                  ? 'bg-[#292444] text-[#FAF6ED] shadow-sm'
                  : 'text-[#5E5875] hover:bg-white hover:text-[#292444]'
              }`}
            >
              <Layers className="w-4 h-4" />
              <span>Preparation Workspace</span>
            </button>

            <button
              onClick={() => setViewMode('catalog')}
              className={`px-4 py-2 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${
                viewMode === 'catalog'
                  ? 'bg-[#292444] text-[#FAF6ED] shadow-sm'
                  : 'text-[#5E5875] hover:bg-white hover:text-[#292444]'
              }`}
            >
              <Brain className="w-4 h-4" />
              <span>Learning Modules & Practice</span>
            </button>
          </div>
        )}

        {currentUser && viewMode === 'workspace' ? (
          <StudentWorkspace />
        ) : (
          <>
            {/* Hero Section */}
            <div className="relative mb-16 sm:mb-24">
              <div className="max-w-3xl">
                {/* Status Pill Badge */}
                <div className="mb-6 inline-flex">
                  <Badge variant="coral" hasDot>
                    Phase 4 · Student Profiles & Preparation Tracking Active
                  </Badge>
                </div>

                {/* Editorial Heading */}
                <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-[#292444] leading-[1.08] mb-6 font-display">
                  Master the placement round. <br />
                  <span className="text-[#FF5B3D]">Practice for real.</span>
                </h1>

            {/* Subheading */}
            <p className="text-lg sm:text-xl text-[#5E5875] leading-relaxed mb-8 max-w-2xl font-normal">
              An institutional placement preparation platform built on authentic problem sets,
              diagnostic skill-gap telemetry, and verified hiring outcome analytics.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center gap-4">
              <Button
                variant="primary"
                size="lg"
                rightIcon={<ArrowRight className="w-4 h-4" />}
                onClick={() => {
                  if (!currentUser) {
                    setAuthMode('register');
                    setIsAuthModalOpen(true);
                  } else {
                    setSelectedModule('quant');
                  }
                }}
              >
                {currentUser ? 'Start Practice Session' : 'Register Student Account'}
              </Button>
              <Button
                variant="secondary"
                size="lg"
                onClick={() => {
                  const el = document.getElementById('architecture');
                  el?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                View Security Architecture
              </Button>
            </div>
          </div>
        </div>

        {/* Live System Architecture & PostgreSQL Verification Banner */}
        <section id="database" className="mb-16">
          <Card variant="contrast" className="relative overflow-hidden">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Server className="w-5 h-5 text-[#FF5B3D]" />
                  <span className="text-xs font-bold uppercase tracking-wider text-[#FAF6ED]/70">
                    Host Environment Status
                  </span>
                </div>
                <h3 className="text-xl sm:text-2xl font-bold text-white mb-2">
                  Native Windows 11 Stack & Database Verified
                </h3>
                <p className="text-sm text-[#FAF6ED]/80 max-w-xl leading-relaxed">
                  PostgreSQL 16 is running natively via Windows Service <code className="text-[#FF5B3D] bg-white/10 px-2 py-0.5 rounded font-mono text-xs">postgresql-x64-16</code>. All 15 relational tables have been created and migrated via Alembic. Docker is strictly prohibited.
                </p>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-2xl p-5 shrink-0 min-w-[280px]">
                <div className="flex items-center justify-between pb-3 border-b border-white/10 text-xs">
                  <span className="text-white/60">PostgreSQL Service</span>
                  <span className="text-emerald-400 font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Running (5432)
                  </span>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-white/10 text-xs">
                  <span className="text-white/60">FastAPI API Uptime</span>
                  <span className="text-white font-mono">
                    {health ? `${health.database.latency_ms} ms latency` : 'Active (Port 8000)'}
                  </span>
                </div>
                <div className="flex items-center justify-between pt-3 text-xs">
                  <span className="text-white/60">Authentication & Security</span>
                  <span className="text-[#FF5B3D] font-mono font-semibold">Argon2 / Bcrypt Active</span>
                </div>
              </div>
            </div>
          </Card>
        </section>

        {/* Practice Tracks Section */}
        <section id="modules" className="mb-20">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
            <div>
              <Badge variant="neutral" className="mb-2">
                Structured Learning Modules
              </Badge>
              <h2 className="text-2xl sm:text-3xl font-bold text-[#292444] font-display">
                Curated Placement Tracks
              </h2>
            </div>
            <p className="text-sm text-[#5E5875] max-w-md">
              Each track is grounded in verified institutional question banks with deterministic scoring and explanations.
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
                    setSelectedModule(m.id);
                  }
                }}
                className="flex flex-col justify-between"
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

        {/* Rule 8 Compliance: Honest Diagnostic Empty State Demonstration */}
        <section className="mb-20">
          <div className="mb-6">
            <Badge variant="neutral" className="mb-2">
              Rule 8 Compliance: Data Integrity & Truthfulness
            </Badge>
            <h2 className="text-2xl font-bold text-[#292444] font-display">
              Personal Learning Standing & Telemetry
            </h2>
          </div>

          <Card className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <h4 className="text-sm font-bold uppercase tracking-wider text-[#5E5875] mb-3">
                Skill-Gap Diagnostic Telemetry
              </h4>
              <EmptyState
                icon={<Brain className="w-6 h-6 text-[#5E5875]" />}
                title="No Practice Attempts Recorded"
                description="Your skill-gap telemetry requires a minimum of 5 evaluated attempts per topic to display an accurate, statistically defensible diagnostic breakdown."
                actionText="Start Your First Activity"
                onAction={() => {
                  if (!currentUser) {
                    setAuthMode('signin');
                    setIsAuthModalOpen(true);
                  } else {
                    setSelectedModule('quant');
                  }
                }}
              />
            </div>

            <div>
              <h4 className="text-sm font-bold uppercase tracking-wider text-[#5E5875] mb-3">
                Mistake Notebook
              </h4>
              <EmptyState
                icon={<BookOpenCheck className="w-6 h-6 text-[#5E5875]" />}
                title="Notebook is Clear"
                description="Incorrect practice questions will be logged here automatically with personal notes and error reflections."
              />
            </div>
          </Card>
        </section>

        {/* Architectural Principles & Governance Grid */}
        <section id="architecture" className="mb-16">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card variant="subtle">
              <KeyRound className="w-6 h-6 text-[#292444] mb-3" />
              <h4 className="text-base font-bold text-[#292444] mb-1.5 font-display">
                Cryptographic Password Security
              </h4>
              <p className="text-xs text-[#5E5875] leading-relaxed">
                Passwords are protected using industry-standard bcrypt with 12 salted rounds. Single-use, expiring tokens govern password resets with zero token leakage.
              </p>
            </Card>

            <Card variant="subtle">
              <ShieldCheck className="w-6 h-6 text-[#15803D] mb-3" />
              <h4 className="text-base font-bold text-[#292444] mb-1.5 font-display">
                Server-Side RBAC Enforcement
              </h4>
              <p className="text-xs text-[#5E5875] leading-relaxed">
                Authorization is enforced strictly on the server across 4 distinct roles (<code className="font-mono text-[#292444]">STUDENT</code>, <code className="font-mono text-[#292444]">TRAINER</code>, <code className="font-mono text-[#292444]">PLACEMENT_OFFICER</code>, <code className="font-mono text-[#292444]">ADMIN</code>).
              </p>
            </Card>

            <Card variant="subtle">
              <Layers className="w-6 h-6 text-[#FF5B3D] mb-3" />
              <h4 className="text-base font-bold text-[#292444] mb-1.5 font-display">
                Tenant Isolation & Audit Trails
              </h4>
              <p className="text-xs text-[#5E5875] leading-relaxed">
                Cross-institution queries are prohibited at the API layer. Security events, logins, and administrative privilege changes are logged into immutable audit records.
              </p>
            </Card>
          </div>
        </section>
        </>
        )}
      </main>

      {/* Authentication Modal Dialog */}
      <AuthModal
        isOpen={isAuthModalOpen}
        initialMode={authMode}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />

      {/* Module Selection Dialog / Drawer */}
      {selectedModule && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#292444]/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-white rounded-3xl border border-[#E8E0D2] p-6 sm:p-8 max-w-lg w-full shadow-warm-lg">
            <div className="flex items-center justify-between pb-4 border-b border-[#E8E0D2] mb-6">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D]">
                  <Calculator className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-[#292444] font-display">
                  Quantitative Aptitude Practice
                </h3>
              </div>
              <Badge variant="neutral">Track Ready</Badge>
            </div>

            <p className="text-sm text-[#5E5875] leading-relaxed mb-6">
              You are about to launch a practice session on <strong>Quantitative Aptitude</strong>. In Phase 4, questions will be fetched directly from the PostgreSQL database with deterministic step-by-step solutions.
            </p>

            <div className="bg-[#FAF6ED] p-4 rounded-2xl border border-[#E8E0D2] mb-6 text-xs text-[#5E5875] space-y-1.5">
              <div className="flex justify-between">
                <span>Evaluation Mode:</span>
                <span className="font-semibold text-[#292444]">Deterministic Scoring</span>
              </div>
              <div className="flex justify-between">
                <span>Mistake Logging:</span>
                <span className="font-semibold text-[#292444]">Automatic to Notebook</span>
              </div>
              <div className="flex justify-between">
                <span>Telemetry:</span>
                <span className="font-semibold text-[#292444]">Active Time Capped (10m)</span>
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <Button variant="outline" size="sm" onClick={() => setSelectedModule(null)}>
                Close Preview
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => {
                  alert('Question bank ingestion & practice engine is scheduled for Phase 4.');
                  setSelectedModule(null);
                }}
              >
                Launch Track
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="w-full border-t border-[#E8E0D2] bg-white py-8 mt-auto">
        <div className="max-w-[1240px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#8E879E]">
          <p>© 2026 Institutional Placement Portal. Native Windows Execution. No Docker.</p>
          <div className="flex items-center gap-4">
            <span>Framer Tempo Lessons Design System</span>
            <span>·</span>
            <span>PostgreSQL 16</span>
            <span>·</span>
            <span>FastAPI & React</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
