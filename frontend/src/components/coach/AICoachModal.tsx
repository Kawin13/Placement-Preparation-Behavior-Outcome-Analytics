import React, { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import {
  explainMistake,
  generateStudyPlan,
  type MistakeExplanationResponse,
  type StudyPlanResponse,
} from '../../services/coach';
import {
  Sparkles,
  X,
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  ShieldCheck,
  Calendar,
  Clock,
  ArrowRight,
  RefreshCw,
  Cpu,
} from 'lucide-react';

export interface AICoachModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'explain' | 'plan';
  questionContext?: {
    questionId: string;
    questionTitle?: string;
    selectedAnswer?: string | null;
    studentNotes?: string | null;
    errorTag?: string | null;
  } | null;
  targetRoleId?: string;
  onLaunchAssessment?: (assessmentId: string) => void;
}

export const AICoachModal: React.FC<AICoachModalProps> = ({
  isOpen,
  onClose,
  initialMode = 'explain',
  questionContext,
  targetRoleId = 'SDE',
  onLaunchAssessment,
}) => {
  const [activeTab, setActiveTab] = useState<'explain' | 'plan'>(
    questionContext ? 'explain' : initialMode
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Explanation state
  const [explanation, setExplanation] = useState<MistakeExplanationResponse | null>(null);

  // Study plan state
  const [selectedRole, setSelectedRole] = useState<string>(targetRoleId);
  const [weeklyHours, setWeeklyHours] = useState<number>(10);
  const [studyPlan, setStudyPlan] = useState<StudyPlanResponse | null>(null);

  useEffect(() => {
    if (isOpen) {
      if (questionContext && questionContext.questionId) {
        setActiveTab('explain');
        handleFetchExplanation();
      } else {
        setActiveTab('plan');
        if (!studyPlan) {
          handleGeneratePlan();
        }
      }
    }
  }, [isOpen, questionContext?.questionId]);

  const handleFetchExplanation = async () => {
    if (!questionContext?.questionId) return;
    try {
      setLoading(true);
      setError(null);
      const res = await explainMistake({
        question_id: questionContext.questionId,
        selected_answer: questionContext.selectedAnswer,
        student_notes: questionContext.studentNotes,
        error_tag: questionContext.errorTag,
      });
      setExplanation(res);
    } catch (err: any) {
      setError(err.message || 'Failed to generate explanation');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePlan = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await generateStudyPlan({
        target_role_id: selectedRole,
        weekly_hours_available: weeklyHours,
      });
      setStudyPlan(res);
    } catch (err: any) {
      setError(err.message || 'Failed to generate personalized study plan');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-[#292444]/65 backdrop-blur-sm animate-in fade-in overflow-y-auto">
      <div className="bg-[#FAF6ED] rounded-3xl border border-[#E8E0D2] shadow-2xl max-w-3xl w-full max-h-[90vh] flex flex-col overflow-hidden my-auto">
        {/* Header Banner */}
        <div className="bg-[#292444] text-white p-6 sm:p-7 relative shrink-0">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#FF5B3D] to-[#FF8A65] flex items-center justify-center shadow-md">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-xl sm:text-2xl font-bold font-display tracking-tight text-white">
                    AI Learning Coach
                  </h2>
                  <Badge variant="coral" className="text-[10px] uppercase font-bold py-0.5">
                    Grounded Mentor
                  </Badge>
                </div>
                <p className="text-xs text-white/70 mt-1">
                  Pedagogical assistance grounded strictly in institutional curricula · Zero student PII shared
                </p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 text-white/80 flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Navigation Pill Tabs */}
          <div className="flex gap-2 mt-5">
            {questionContext && (
              <button
                onClick={() => setActiveTab('explain')}
                className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${
                  activeTab === 'explain'
                    ? 'bg-[#FF5B3D] text-white shadow-xs'
                    : 'bg-white/10 text-white/70 hover:bg-white/20'
                }`}
              >
                <Lightbulb className="w-3.5 h-3.5" />
                Mistake Breakdown
              </button>
            )}
            <button
              onClick={() => {
                setActiveTab('plan');
                if (!studyPlan) handleGeneratePlan();
              }}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'plan'
                  ? 'bg-[#FF5B3D] text-white shadow-xs'
                  : 'bg-white/10 text-white/70 hover:bg-white/20'
              }`}
            >
              <Calendar className="w-3.5 h-3.5" />
              Personalized Study Plan
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="p-6 sm:p-7 overflow-y-auto space-y-6">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl flex items-center gap-3 text-xs">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
              <Button
                variant="secondary"
                size="sm"
                onClick={activeTab === 'explain' ? handleFetchExplanation : handleGeneratePlan}
                className="ml-auto text-xs"
              >
                Retry
              </Button>
            </div>
          )}

          {loading ? (
            <div className="py-16 text-center space-y-3">
              <div className="inline-block w-9 h-9 border-3 border-[#FF5B3D] border-t-transparent rounded-full animate-spin" />
              <p className="text-sm font-semibold text-[#292444]">
                {activeTab === 'explain'
                  ? 'Consulting grounded syllabus reasoning engine...'
                  : 'Synthesizing verified attempt history & gap telemetry...'}
              </p>
              <p className="text-xs text-[#5E5875]">Zero personal telemetry is shared externally.</p>
            </div>
          ) : activeTab === 'explain' && explanation ? (
            /* Explain Mistake Tab */
            <div className="space-y-5 animate-in fade-in">
              {/* Context Summary & Provider Info */}
              <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-2xl border border-[#E8E0D2] shadow-xs">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#5E5875] block">
                    Target Question
                  </span>
                  <h3 className="text-sm font-bold text-[#292444] mt-0.5">
                    {explanation.question_title}
                  </h3>
                </div>
                <div className="flex items-center gap-2">
                  <Badge
                    variant={explanation.provider_used === 'GEMINI_EXTERNAL' ? 'coral' : 'neutral'}
                    className="text-[11px] font-medium flex items-center gap-1"
                  >
                    <Cpu className="w-3 h-3" />
                    {explanation.provider_used === 'GEMINI_EXTERNAL' ? 'Gemini 1.5 Grounded' : 'Deterministic Offline Mentor'}
                  </Badge>
                  {explanation.is_grounded_in_syllabus && (
                    <Badge variant="success" className="text-[11px]">
                      Syllabus Grounded
                    </Badge>
                  )}
                </div>
              </div>

              {/* Core Concept Summary */}
              <Card className="p-5 bg-white border border-[#E8E0D2]">
                <div className="flex items-center gap-2 mb-2">
                  <BookOpen className="w-4 h-4 text-[#FF5B3D]" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#292444]">
                    Core Concept Overview
                  </h4>
                </div>
                <p className="text-sm text-[#292444] leading-relaxed">
                  {explanation.concept_summary}
                </p>
              </Card>

              {/* Step-by-Step Proof / Detailed Solution */}
              <Card className="p-5 bg-white border border-[#E8E0D2] space-y-2">
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#292444]">
                    Step-by-Step Verification & Proof
                  </h4>
                </div>
                <div className="text-xs sm:text-sm text-[#292444]/90 whitespace-pre-wrap leading-relaxed font-mono bg-[#FAF6ED] p-4 rounded-xl border border-[#E8E0D2]/80">
                  {explanation.detailed_proof_or_explanation}
                </div>
              </Card>

              {/* Why Answer was Incorrect (if available) */}
              {explanation.why_answer_was_incorrect && (
                <div className="p-4 bg-amber-50/70 border border-amber-200 rounded-2xl">
                  <div className="flex items-center gap-2 text-amber-800 font-bold text-xs uppercase tracking-wider mb-1">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                    Misconception Identified
                  </div>
                  <p className="text-xs text-amber-900 leading-relaxed">
                    {explanation.why_answer_was_incorrect}
                  </p>
                </div>
              )}

              {/* Key Remedial Takeaway */}
              <div className="p-4 bg-[#292444] text-white rounded-2xl shadow-sm space-y-1">
                <div className="flex items-center gap-1.5 text-[#FF5B3D] text-xs font-bold uppercase tracking-wider">
                  <Lightbulb className="w-3.5 h-3.5" />
                  Key Pedagogical Rule to Retain
                </div>
                <p className="text-xs sm:text-sm text-white/90 leading-relaxed font-medium">
                  {explanation.remedial_takeaway}
                </p>
              </div>

              {/* Recommended Topic & Privacy Banner */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
                <div className="text-xs text-[#5E5875]">
                  Recommended Practice Area: <span className="font-semibold text-[#292444]">{explanation.recommended_topic}</span>
                </div>
                <div className="flex items-center gap-1.5 text-[11px] text-[#5E5875]">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>{explanation.privacy_notice}</span>
                </div>
              </div>
            </div>
          ) : activeTab === 'plan' ? (
            /* Study Plan Tab */
            <div className="space-y-6 animate-in fade-in">
              {/* Controls Header */}
              <div className="bg-white p-5 rounded-2xl border border-[#E8E0D2] shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#5E5875] block">
                    Curriculum Target & Availability
                  </span>
                  <div className="flex flex-wrap items-center gap-3">
                    <select
                      value={selectedRole}
                      onChange={(e) => setSelectedRole(e.target.value)}
                      className="text-xs font-bold text-[#292444] bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl px-3 py-2 outline-none focus:ring-1 focus:ring-[#FF5B3D]"
                    >
                      <option value="SDE">Software Development Engineer (SDE)</option>
                      <option value="DATA_ANALYST">Data Analyst / SQL Specialist</option>
                      <option value="CORE_TECH">Core Technology Graduate</option>
                    </select>

                    <div className="flex items-center gap-2 text-xs text-[#5E5875]">
                      <Clock className="w-3.5 h-3.5" />
                      <span>Weekly Hours:</span>
                      <select
                        value={weeklyHours}
                        onChange={(e) => setWeeklyHours(Number(e.target.value))}
                        className="text-xs font-semibold text-[#292444] bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl px-2 py-1.5 outline-none"
                      >
                        <option value={5}>5 hours</option>
                        <option value={10}>10 hours</option>
                        <option value={15}>15 hours</option>
                        <option value={20}>20 hours</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleGeneratePlan}
                  leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
                  className="shrink-0 text-xs"
                >
                  Regenerate Plan
                </Button>
              </div>

              {studyPlan && (
                <div className="space-y-5">
                  {/* Plan Overview */}
                  <div className="bg-white p-5 rounded-2xl border border-[#E8E0D2]">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-bold text-[#292444]">
                        {studyPlan.target_role_name} Prep Strategy
                      </h4>
                      <Badge variant="neutral" className="text-[11px]">
                        Engine: {studyPlan.provider_used}
                      </Badge>
                    </div>
                    <p className="text-xs text-[#5E5875] leading-relaxed">
                      {studyPlan.plan_overview}
                    </p>
                  </div>

                  {/* Schedule Timeline */}
                  <div className="space-y-3">
                    <h5 className="text-xs font-bold uppercase tracking-wider text-[#5E5875]">
                      Targeted 5-Day Diagnostic Schedule
                    </h5>
                    <div className="grid grid-cols-1 gap-3">
                      {studyPlan.schedule.map((item) => (
                        <div
                          key={item.day_number}
                          className="bg-white p-4 rounded-2xl border border-[#E8E0D2] hover:border-[#FF5B3D]/50 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                        >
                          <div className="flex items-start gap-3">
                            <div className="w-9 h-9 rounded-xl bg-[#292444] text-[#FAF6ED] flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                              D{item.day_number}
                            </div>
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-xs font-bold text-[#292444]">
                                  {item.topic_focus}
                                </span>
                                <Badge
                                  variant={
                                    item.action_type === 'PRACTICE_DRILL'
                                      ? 'coral'
                                      : item.action_type === 'MISTAKE_REVIEW'
                                      ? 'warning'
                                      : 'neutral'
                                  }
                                  className="text-[10px] font-semibold py-0.5"
                                >
                                  {item.action_type.replace('_', ' ')}
                                </Badge>
                                <span className="text-[11px] text-[#5E5875]">
                                  · {item.suggested_duration_minutes} mins
                                </span>
                              </div>
                              <p className="text-xs text-[#5E5875] leading-relaxed">
                                {item.pedagogical_objective}
                              </p>
                            </div>
                          </div>

                          {item.suggested_assessment_id && onLaunchAssessment && (
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => {
                                onClose();
                                onLaunchAssessment(item.suggested_assessment_id!);
                              }}
                              rightIcon={<ArrowRight className="w-3 h-3 text-[#FF5B3D]" />}
                              className="shrink-0 text-xs text-[#292444]"
                            >
                              Launch Practice
                            </Button>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Footnotes & Grounding */}
                  <div className="bg-[#FAF6ED] p-4 rounded-2xl border border-[#E8E0D2] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-[#5E5875]">
                    <div>{studyPlan.evidence_grounding_note}</div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                      <span>{studyPlan.privacy_notice}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-white border-t border-[#E8E0D2] flex items-center justify-between shrink-0">
          <div className="text-[11px] text-[#5E5875]">
            Strict institutional governance: No ranking, no auto-rejection, no predictive hiring guarantees.
          </div>
          <Button variant="outline" size="sm" onClick={onClose} className="text-xs">
            Close Coach
          </Button>
        </div>
      </div>
    </div>
  );
};
