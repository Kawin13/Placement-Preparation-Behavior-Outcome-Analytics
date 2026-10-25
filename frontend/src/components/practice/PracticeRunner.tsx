import { useState, useEffect, useRef } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import {
  type ActiveSession,
  saveSessionAnswer,
  submitPracticeSession,
  type SubmitResult,
} from '../../services/practice';
import {
  Timer,
  Flag,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  LogOut,
} from 'lucide-react';

interface PracticeRunnerProps {
  session: ActiveSession;
  onSessionSubmitted: (result: SubmitResult) => void;
  onExit: () => void;
}

export function PracticeRunner({ session, onSessionSubmitted, onExit }: PracticeRunnerProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>(() => {
    // Restore answers from session payload or localStorage
    const initial: Record<string, string> = {};
    session.questions.forEach((q) => {
      if (q.saved_answer) {
        initial[q.id] = q.saved_answer;
      }
    });
    try {
      const cached = localStorage.getItem(`session_answers_${session.session_id}`);
      if (cached) {
        Object.assign(initial, JSON.parse(cached));
      }
    } catch {}
    return initial;
  });

  const [flagged, setFlagged] = useState<Record<string, boolean>>({});
  const [submitting, setSubmitting] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Active timer calculation
  const totalDurationSeconds = session.duration_minutes * 60;
  const [secondsRemaining, setSecondsRemaining] = useState<number>(() => {
    const elapsed = session.time_spent_seconds || 0;
    return Math.max(0, totalDurationSeconds - elapsed);
  });

  const questionStartTimeRef = useRef<number>(Date.now());
  const timerRef = useRef<number | null>(null);

  // Timer Countdown
  useEffect(() => {
    timerRef.current = setInterval(() => {
      setSecondsRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current!);
          handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // Keyboard navigation shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is in an input or textarea
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) return;

      const currentQ = session.questions[currentIndex];
      if (!currentQ) return;

      if (['1', '2', '3', '4'].includes(e.key)) {
        const optIndex = parseInt(e.key, 10) - 1;
        if (currentQ.options[optIndex]) {
          handleSelectOption(currentQ.id, currentQ.options[optIndex].id);
        }
      } else if (e.key === 'f' || e.key === 'F') {
        toggleFlag(currentQ.id);
      } else if (e.key === 'ArrowRight' && currentIndex < session.questions.length - 1) {
        handleNavigate(currentIndex + 1);
      } else if (e.key === 'ArrowLeft' && currentIndex > 0) {
        handleNavigate(currentIndex - 1);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, answers, session]);

  const handleSelectOption = async (questionId: string, optionId: string) => {
    const now = Date.now();
    const timeSpentMs = now - questionStartTimeRef.current;
    questionStartTimeRef.current = now;

    const newAnswers = { ...answers, [questionId]: optionId };
    setAnswers(newAnswers);

    // Persist to localStorage for crash resilience
    try {
      localStorage.setItem(`session_answers_${session.session_id}`, JSON.stringify(newAnswers));
    } catch {}

    // Async sync to PostgreSQL backend
    try {
      await saveSessionAnswer(session.session_id, questionId, optionId, timeSpentMs);
    } catch (err: any) {
      console.warn('Failed to sync answer to server:', err);
    }
  };

  const handleClearChoice = async (questionId: string) => {
    const newAnswers = { ...answers };
    delete newAnswers[questionId];
    setAnswers(newAnswers);
    try {
      localStorage.setItem(`session_answers_${session.session_id}`, JSON.stringify(newAnswers));
      await saveSessionAnswer(session.session_id, questionId, '', 0);
    } catch {}
  };

  const toggleFlag = (questionId: string) => {
    setFlagged((prev) => ({ ...prev, [questionId]: !prev[questionId] }));
  };

  const handleNavigate = (newIndex: number) => {
    questionStartTimeRef.current = Date.now();
    setCurrentIndex(newIndex);
  };

  const handleAutoSubmit = async () => {
    await performSubmit();
  };

  const performSubmit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const timeSpent = Math.max(1, totalDurationSeconds - secondsRemaining);
      const result = await submitPracticeSession(session.session_id, timeSpent);
      localStorage.removeItem(`session_answers_${session.session_id}`);
      onSessionSubmitted(result);
    } catch (err: any) {
      setError(err.message || 'Failed to submit practice session');
      setSubmitting(false);
    }
  };

  const formatTimer = (totalSec: number) => {
    const mins = Math.floor(totalSec / 60);
    const secs = totalSec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const currentQuestion = session.questions[currentIndex];
  const answeredCount = Object.keys(answers).length;
  const isTimeCritical = secondsRemaining <= 120; // Last 2 minutes

  return (
    <div className="space-y-6">
      {/* Top Banner Navigation & Timer */}
      <div className="bg-[#292444] text-white rounded-3xl p-6 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs uppercase tracking-wider font-semibold text-white/60">
              {session.assessment_category?.replace('_', ' ') || 'Diagnostic Practice'}
            </span>
            <span className="text-white/40">•</span>
            <Badge variant="warning" className="text-[10px]">
              {session.session_type === 'TIMED_MOCK' ? 'Timed Mock' : 'Practice Mode'}
            </Badge>
          </div>
          <h2 className="text-xl font-bold tracking-tight">{session.assessment_title}</h2>
        </div>

        {/* Live Timer & Submit CTA */}
        <div className="flex items-center gap-4 w-full sm:w-auto justify-between sm:justify-end">
          <div
            className={`flex items-center gap-2 px-4 py-2 rounded-2xl border transition-colors ${
              isTimeCritical
                ? 'bg-red-500/20 border-red-500 text-red-200 animate-pulse'
                : 'bg-white/10 border-white/20 text-white'
            }`}
          >
            <Timer className="w-4 h-4" />
            <span className="font-mono text-base font-bold">{formatTimer(secondsRemaining)}</span>
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={onExit}
            className="text-xs text-white/80 bg-white/10 border-white/20 hover:bg-white/20"
          >
            <LogOut className="w-3.5 h-3.5 mr-1" />
            Pause & Exit
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={() => setShowConfirmModal(true)}
            className="text-xs font-semibold shadow-sm"
          >
            Finish & Review
          </Button>
        </div>
      </div>

      {/* Main Practice Workspace: Split into Question View and Palette */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left: Active Question Card (3 columns) */}
        <div className="lg:col-span-3 space-y-6">
          <Card className="p-8 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl">
            {/* Question Header */}
            <div className="flex items-center justify-between pb-4 border-b border-[#E8E0D2]/60 mb-6">
              <div className="flex items-center gap-3">
                <span className="text-sm font-bold text-[#FF5B3D]">
                  Question {currentIndex + 1} of {session.questions.length}
                </span>
                <Badge variant="neutral" className="text-xs font-semibold">
                  {currentQuestion.difficulty}
                </Badge>
                <span className="text-xs text-[#292444]/60">
                  {currentQuestion.points} point{currentQuestion.points > 1 ? 's' : ''}
                </span>
              </div>

              <button
                onClick={() => toggleFlag(currentQuestion.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                  flagged[currentQuestion.id]
                    ? 'bg-amber-100 text-amber-800 border border-amber-300'
                    : 'text-[#292444]/60 hover:bg-[#FAF6ED] border border-transparent'
                }`}
                title="Press 'F' to flag this question for later review"
              >
                <Flag className="w-3.5 h-3.5" />
                <span>{flagged[currentQuestion.id] ? 'Flagged' : 'Flag for review'}</span>
              </button>
            </div>

            {/* Question Statement */}
            <div className="text-base text-[#292444] font-medium leading-relaxed mb-8 whitespace-pre-wrap">
              {currentQuestion.content}
            </div>

            {/* Multiple Choice Options */}
            <div className="space-y-3 mb-8">
              {currentQuestion.options.map((opt, idx) => {
                const isSelected = answers[currentQuestion.id] === opt.id;
                const optionKey = ['A', 'B', 'C', 'D'][idx] || (idx + 1).toString();

                return (
                  <button
                    key={opt.id}
                    onClick={() => handleSelectOption(currentQuestion.id, opt.id)}
                    className={`w-full text-left p-4 rounded-2xl border transition-all flex items-start gap-4 ${
                      isSelected
                        ? 'border-[#FF5B3D] bg-[#FF5B3D]/5 shadow-sm'
                        : 'border-[#E8E0D2] bg-white hover:bg-[#FAF6ED] hover:border-[#292444]/30'
                    }`}
                  >
                    <div
                      className={`w-7 h-7 rounded-xl flex items-center justify-center font-bold text-xs flex-shrink-0 transition-colors ${
                        isSelected
                          ? 'bg-[#FF5B3D] text-white'
                          : 'bg-[#FAF6ED] border border-[#E8E0D2] text-[#292444]/70'
                      }`}
                    >
                      {optionKey}
                    </div>
                    <div className="text-sm text-[#292444] leading-relaxed pt-0.5">
                      {opt.option_text}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Bottom Actions: Clear Choice, Previous, Next */}
            <div className="flex items-center justify-between pt-6 border-t border-[#E8E0D2]/60">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => handleClearChoice(currentQuestion.id)}
                disabled={!answers[currentQuestion.id]}
                className="text-xs text-[#292444]/60"
              >
                <RotateCcw className="w-3 h-3 mr-1" />
                Clear Choice
              </Button>

              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleNavigate(currentIndex - 1)}
                  disabled={currentIndex === 0}
                  className="text-xs font-semibold"
                >
                  <ArrowLeft className="w-3.5 h-3.5 mr-1" />
                  Previous
                </Button>

                {currentIndex < session.questions.length - 1 ? (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleNavigate(currentIndex + 1)}
                    className="text-xs font-semibold"
                  >
                    Next
                    <ArrowRight className="w-3.5 h-3.5 ml-1" />
                  </Button>
                ) : (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => setShowConfirmModal(true)}
                    className="text-xs font-semibold"
                  >
                    Finish Session
                    <CheckCircle2 className="w-3.5 h-3.5 ml-1" />
                  </Button>
                )}
              </div>
            </div>
          </Card>
        </div>

        {/* Right: Question Navigation Palette (1 column) */}
        <div className="space-y-6">
          <Card className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl">
            <h3 className="text-sm font-bold text-[#292444] mb-3">Question Palette</h3>

            {/* Answered Progress bar */}
            <div className="mb-4">
              <div className="flex justify-between text-xs text-[#292444]/70 mb-1">
                <span>Attempted</span>
                <span className="font-bold text-[#292444]">
                  {answeredCount} / {session.questions.length}
                </span>
              </div>
              <div className="w-full bg-[#FAF6ED] rounded-full h-2 border border-[#E8E0D2]">
                <div
                  className="bg-[#FF5B3D] h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(answeredCount / session.questions.length) * 100}%` }}
                />
              </div>
            </div>

            {/* Grid of question buttons */}
            <div className="grid grid-cols-5 gap-2 mb-6">
              {session.questions.map((q, idx) => {
                const isAnswered = Boolean(answers[q.id]);
                const isCurrent = idx === currentIndex;
                const isFlagged = Boolean(flagged[q.id]);

                let btnClass = 'bg-[#FAF6ED] border-[#E8E0D2] text-[#292444]/70 hover:bg-[#FAF6ED]/80';
                if (isCurrent) {
                  btnClass = 'ring-2 ring-[#292444] font-bold';
                }
                if (isAnswered) {
                  btnClass += ' bg-[#FF5B3D] border-[#FF5B3D] text-white';
                } else if (isFlagged) {
                  btnClass += ' bg-amber-100 border-amber-300 text-amber-900';
                }

                return (
                  <button
                    key={q.id}
                    onClick={() => handleNavigate(idx)}
                    className={`h-9 rounded-xl border text-xs font-semibold transition-all flex items-center justify-center relative ${btnClass}`}
                  >
                    {idx + 1}
                    {isFlagged && (
                      <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-amber-500 rounded-full border border-white" />
                    )}
                  </button>
                );
              })}
            </div>

            {/* Legend */}
            <div className="space-y-2 text-[11px] text-[#292444]/70 pt-4 border-t border-[#E8E0D2]/60">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-md bg-[#FF5B3D]" />
                <span>Answered ({answeredCount})</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-md bg-[#FAF6ED] border border-[#E8E0D2]" />
                <span>Unattempted ({session.questions.length - answeredCount})</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-md bg-amber-100 border border-amber-300" />
                <span>Flagged for review ({Object.values(flagged).filter(Boolean).length})</span>
              </div>
            </div>

            {/* Keyboard shortcut tip */}
            <div className="mt-6 pt-4 border-t border-[#E8E0D2]/60 text-[11px] text-[#292444]/60 space-y-1">
              <p className="font-semibold text-[#292444]">Keyboard Shortcuts:</p>
              <p>• Keys <kbd className="px-1 py-0.5 bg-[#FAF6ED] border rounded">1-4</kbd> select option</p>
              <p>• Key <kbd className="px-1 py-0.5 bg-[#FAF6ED] border rounded">F</kbd> flags question</p>
              <p>• Arrows <kbd className="px-1 py-0.5 bg-[#FAF6ED] border rounded">←</kbd> <kbd className="px-1 py-0.5 bg-[#FAF6ED] border rounded">→</kbd> navigate</p>
            </div>
          </Card>
        </div>
      </div>

      {/* Confirmation & Summary Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
          <Card className="w-full max-w-md p-6 bg-white border border-[#E8E0D2] shadow-xl rounded-3xl">
            <h3 className="text-lg font-bold text-[#292444] mb-2 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-[#FF5B3D]" />
              Submit Practice Assessment
            </h3>
            <p className="text-xs text-[#292444]/70 mb-4 leading-relaxed">
              Are you ready to submit your attempt? You will immediately receive deterministic scoring and step-by-step mathematical explanations.
            </p>

            <div className="bg-[#FAF6ED] p-4 rounded-2xl border border-[#E8E0D2] space-y-2 mb-6 text-xs">
              <div className="flex justify-between">
                <span className="text-[#292444]/60">Total Questions:</span>
                <span className="font-bold text-[#292444]">{session.questions.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#292444]/60">Attempted Questions:</span>
                <span className="font-bold text-[#FF5B3D]">{answeredCount}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#292444]/60">Unanswered Questions:</span>
                <span className="font-bold text-[#292444]">{session.questions.length - answeredCount}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#292444]/60">Flagged for Review:</span>
                <span className="font-bold text-amber-700">{Object.values(flagged).filter(Boolean).length}</span>
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-50 text-red-700 text-xs rounded-xl mb-4 border border-red-200 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                className="flex-1 text-xs"
                onClick={() => setShowConfirmModal(false)}
                disabled={submitting}
              >
                Back to Questions
              </Button>
              <Button
                variant="primary"
                size="sm"
                className="flex-1 text-xs font-semibold"
                onClick={performSubmit}
                disabled={submitting}
              >
                {submitting ? 'Grading...' : 'Confirm Submission'}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
