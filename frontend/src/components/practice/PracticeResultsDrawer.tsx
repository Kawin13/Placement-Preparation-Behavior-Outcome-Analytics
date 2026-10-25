import { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import {
  fetchSessionReview,
  type SubmitResult,
  type SessionReview,
} from '../../services/practice';
import {
  CheckCircle2,
  XCircle,
  HelpCircle,
  Timer,
  Award,
  ArrowRight,
  BookOpen,
  Sparkles,
  AlertCircle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

interface PracticeResultsDrawerProps {
  result: SubmitResult;
  onGoToWorkspace: () => void;
  onGoToMistakes: () => void;
}

export function PracticeResultsDrawer({
  result,
  onGoToWorkspace,
  onGoToMistakes,
}: PracticeResultsDrawerProps) {
  const [review, setReview] = useState<SessionReview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedQuestions, setExpandedQuestions] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadReview();
  }, [result.session_id]);

  const loadReview = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchSessionReview(result.session_id);
      setReview(data);
      // Auto-expand all questions for immediate learning review
      const expanded: Record<string, boolean> = {};
      data.questions.forEach((q) => {
        expanded[q.id] = true;
      });
      setExpandedQuestions(expanded);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch session review');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (qId: string) => {
    setExpandedQuestions((prev) => ({ ...prev, [qId]: !prev[qId] }));
  };

  const formatDuration = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Score Summary Card */}
      <div className="bg-[#292444] text-white rounded-3xl p-8 shadow-sm">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-[#FF5B3D]" />
              <span className="text-xs font-semibold uppercase tracking-wider text-white/70">
                Attempt Complete • Formative Mastery Mode
              </span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">
              {review?.assessment_title || 'Session Results'}
            </h1>
            <p className="text-xs text-white/80 max-w-xl leading-relaxed">
              Diagnostic results calculated deterministically from your authenticated attempt records.
              Zero penalty rules applied. All incorrect responses have been synced to your Mistake Notebook.
            </p>
          </div>

          {/* Metric Radial / Badge */}
          <div className="bg-white/10 border border-white/20 rounded-3xl p-6 text-center min-w-[200px]">
            <div className="text-4xl font-extrabold text-[#FF5B3D] tracking-tight mb-1">
              {result.percentage.toFixed(1)}%
            </div>
            <div className="text-xs font-semibold text-white/80">
              {result.total_score} / {result.max_score} Points
            </div>
            <div className="mt-3">
              <Badge
                variant={result.is_passed ? 'success' : 'neutral'}
                className="text-[11px] font-bold uppercase tracking-wider"
              >
                {result.is_passed ? 'Proficient' : 'Needs Practice'}
              </Badge>
            </div>
          </div>
        </div>

        {/* Breakdown Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8 pt-6 border-t border-white/10">
          <div className="bg-white/5 rounded-2xl p-3 border border-white/10">
            <div className="flex items-center gap-2 text-xs text-emerald-400 mb-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Correct</span>
            </div>
            <div className="text-xl font-bold">{result.correct_count}</div>
          </div>

          <div className="bg-white/5 rounded-2xl p-3 border border-white/10">
            <div className="flex items-center gap-2 text-xs text-red-400 mb-1">
              <XCircle className="w-3.5 h-3.5" />
              <span>Incorrect</span>
            </div>
            <div className="text-xl font-bold">{result.incorrect_count}</div>
          </div>

          <div className="bg-white/5 rounded-2xl p-3 border border-white/10">
            <div className="flex items-center gap-2 text-xs text-white/60 mb-1">
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Unanswered</span>
            </div>
            <div className="text-xl font-bold">{result.unanswered_count}</div>
          </div>

          <div className="bg-white/5 rounded-2xl p-3 border border-white/10">
            <div className="flex items-center gap-2 text-xs text-amber-400 mb-1">
              <Timer className="w-3.5 h-3.5" />
              <span>Time Spent</span>
            </div>
            <div className="text-xl font-bold">{formatDuration(result.time_spent_seconds)}</div>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-wrap gap-3 mt-8">
          <Button
            variant="primary"
            size="sm"
            onClick={onGoToWorkspace}
            className="text-xs font-semibold"
          >
            Return to Workspace
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Button>

          {result.incorrect_count > 0 && (
            <Button
              variant="secondary"
              size="sm"
              onClick={onGoToMistakes}
              className="text-xs font-semibold bg-white text-[#292444] hover:bg-white/90"
            >
              <BookOpen className="w-3.5 h-3.5 mr-1 text-[#FF5B3D]" />
              Review Mistake Notebook ({result.incorrect_count})
            </Button>
          )}
        </div>
      </div>

      {/* Detailed Solution Proofs & Distractor Rationales */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-[#292444] flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-[#FF5B3D]" />
            Detailed Question Review & Proofs
          </h2>
          <span className="text-xs text-[#292444]/60">
            {review?.questions.length || 0} questions reviewed
          </span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-[#292444]/60">
            <div className="inline-block w-8 h-8 border-4 border-[#FF5B3D] border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-xs font-medium">Loading verified solutions...</p>
          </div>
        ) : error ? (
          <Card className="p-6 text-center text-red-600 bg-red-50 border border-red-200">
            <AlertCircle className="w-6 h-6 mx-auto mb-2" />
            <p className="text-xs">{error}</p>
          </Card>
        ) : (
          review?.questions.map((q, idx) => {
            const isExpanded = Boolean(expandedQuestions[q.id]);
            const statusVariant = q.is_correct
              ? 'success'
              : q.submitted_answer
              ? 'error'
              : 'neutral';

            return (
              <Card
                key={q.id}
                className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl transition-all"
              >
                {/* Header Row */}
                <div
                  className="flex items-center justify-between cursor-pointer select-none"
                  onClick={() => toggleExpand(q.id)}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-bold text-[#FF5B3D]">Q{idx + 1}</span>
                    <h3 className="text-sm font-bold text-[#292444]">{q.title}</h3>
                    <Badge variant={statusVariant} className="text-[10px] font-semibold">
                      {q.is_correct
                        ? `Correct (+${q.score_awarded})`
                        : q.submitted_answer
                        ? 'Incorrect (0)'
                        : 'Unattempted'}
                    </Badge>
                  </div>

                  <button className="text-[#292444]/60 hover:text-[#292444]">
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>

                {/* Collapsible Content */}
                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-[#E8E0D2]/60 space-y-4">
                    {/* Problem Statement */}
                    <div className="text-sm text-[#292444] leading-relaxed whitespace-pre-wrap font-medium">
                      {q.content}
                    </div>

                    {/* Options Breakdown with Feedback */}
                    <div className="space-y-2">
                      <div className="text-xs font-bold text-[#292444]/60 uppercase tracking-wider">
                        Options & Rationales
                      </div>
                      {q.options.map((opt) => {
                        const isStudentChoice = q.submitted_answer === opt.id;
                        const isCorrectOption = opt.is_correct;

                        let borderBg = 'border-[#E8E0D2] bg-white';
                        if (isCorrectOption) {
                          borderBg = 'border-emerald-500 bg-emerald-50/60';
                        } else if (isStudentChoice && !isCorrectOption) {
                          borderBg = 'border-red-400 bg-red-50/60';
                        }

                        return (
                          <div
                            key={opt.id}
                            className={`p-3.5 rounded-2xl border text-xs leading-relaxed transition-all ${borderBg}`}
                          >
                            <div className="flex items-start justify-between gap-2 mb-1">
                              <span className="font-semibold text-[#292444]">{opt.option_text}</span>
                              <div className="flex items-center gap-1.5 flex-shrink-0">
                                {isStudentChoice && (
                                  <Badge
                                    variant={isCorrectOption ? 'success' : 'error'}
                                    className="text-[10px]"
                                  >
                                    Your Choice
                                  </Badge>
                                )}
                                {isCorrectOption && (
                                  <Badge variant="success" className="text-[10px]">
                                    Correct Key
                                  </Badge>
                                )}
                              </div>
                            </div>
                            {opt.feedback && (
                              <p className="text-[11px] text-[#292444]/70 pt-1 border-t border-black/5">
                                {opt.feedback}
                              </p>
                            )}
                          </div>
                        );
                      })}
                    </div>

                    {/* Step-by-Step Proof Box */}
                    {q.explanation && (
                      <div className="p-4 bg-[#FAF6ED] rounded-2xl border border-[#E8E0D2] space-y-1">
                        <div className="text-xs font-bold text-[#292444] flex items-center gap-1.5 mb-1">
                          <Award className="w-3.5 h-3.5 text-[#FF5B3D]" />
                          Step-by-Step Proof & Mathematical Resolution
                        </div>
                        <div className="text-xs text-[#292444]/80 leading-relaxed whitespace-pre-wrap">
                          {q.explanation}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}
