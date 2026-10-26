import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  BookOpen,
  Clock,
  Code2,
  ExternalLink,
  Brain,
  Sparkles,
  FileText,
  AlertCircle,
  RefreshCw,
  Check,
  PlayCircle,
  Award,
  CheckCircle2,
  HelpCircle,
} from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import {
  fetchTopicDetail,
  fetchResourceDetail,
  completeResource,
  trackStudentBehaviorEvent,
  type TopicDetail,
  type LearningResourceSummary,
  type LearningResourceDetail,
} from '../../services/roadmap';

interface TopicDetailViewProps {
  topicId: string;
  onBack: () => void;
  onSelectDsaProblem?: (slug: string) => void;
  onPracticeQuestions?: (topicName?: string) => void;
  onStartAssessment?: (assessmentId: string) => void;
}

export const TopicDetailView: React.FC<TopicDetailViewProps> = ({
  topicId,
  onBack,
  onSelectDsaProblem,
  onPracticeQuestions,
  onStartAssessment,
}) => {
  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [activeTab, setActiveTab] = useState<'materials' | 'practice' | 'dsa'>('materials');
  const [activeResource, setActiveResource] = useState<LearningResourceDetail | null>(null);
  const [completingId, setCompletingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTopic();
    // Track topic viewing event
    trackStudentBehaviorEvent('SESSION_START', {
      topic_id: topicId,
      metadata: { context: 'TOPIC_STUDY' },
    });
  }, [topicId]);

  const loadTopic = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchTopicDetail(topicId);
      setTopic(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load topic details');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenResource = async (resource: LearningResourceSummary) => {
    try {
      const full = await fetchResourceDetail(resource.id);
      setActiveResource(full);
      // Track resource study event
      trackStudentBehaviorEvent('RESOURCE_OPENED', {
        topic_id: topicId,
        resource_id: resource.id,
      });
    } catch (err: any) {
      alert(err.message || 'Failed to open resource');
    }
  };

  const handleMarkResourceComplete = async (resourceId: string) => {
    setCompletingId(resourceId);
    try {
      await completeResource(resourceId, 120);
      await loadTopic();
      if (activeResource && activeResource.id === resourceId) {
        setActiveResource({ ...activeResource, is_completed: true });
      }
    } catch (err: any) {
      alert(err.message || 'Failed to complete resource');
    } finally {
      setCompletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[420px] p-8 text-center">
        <RefreshCw className="w-8 h-8 text-[#FF5B3D] animate-spin mb-4" />
        <h3 className="text-base font-bold text-[#292444] font-display">Loading Topic Study Workspace...</h3>
        <p className="text-xs text-[#5E5875] mt-1">Retrieving learning objectives, study notes, and diagnostic questions.</p>
      </div>
    );
  }

  if (error || !topic) {
    return (
      <div className="p-8 text-center max-w-md mx-auto">
        <AlertCircle className="w-10 h-10 text-rose-600 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-[#292444] font-display">Unable to load topic</h3>
        <p className="text-xs text-[#5E5875] mb-4">{error || 'Topic not found'}</p>
        <Button variant="secondary" size="sm" onClick={onBack}>
          Return to Roadmap
        </Button>
      </div>
    );
  }

  const confidenceBadgeVariant =
    topic.evidence_confidence === 'HIGH'
      ? 'success'
      : topic.evidence_confidence === 'MODERATE'
      ? 'coral'
      : 'neutral';

  return (
    <div className="space-y-8 animate-fadeIn max-w-[1240px] mx-auto">
      {/* Header & Breadcrumb */}
      <div>
        <button
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs font-bold text-[#5E5875] hover:text-[#292444] mb-4 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Career Roadmap
        </button>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#E8E0D2] pb-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[#8E879E]">
                {topic.subject_name}
              </span>
              <span className="text-xs text-[#8E879E]">·</span>
              <Badge variant="neutral" className="text-[10px]">
                {topic.difficulty}
              </Badge>
              <Badge variant={confidenceBadgeVariant} className="text-[10px] font-bold">
                Evidence: {topic.evidence_confidence}
              </Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#292444] font-display">
              {topic.name}
            </h1>
            {topic.description && (
              <p className="text-xs sm:text-sm text-[#5E5875] mt-1 max-w-2xl">{topic.description}</p>
            )}
          </div>

          <div className="flex items-center gap-3">
            {topic.assessment && onStartAssessment ? (
              <Button
                variant="primary"
                size="sm"
                rightIcon={<PlayCircle className="w-4 h-4" />}
                onClick={() => onStartAssessment(topic.assessment!.id)}
                className="font-bold shadow-warm bg-[#FF5B3D] text-white hover:bg-[#e0482b]"
              >
                Take Topic Assessment
              </Button>
            ) : topic.practice_questions.length > 0 && onPracticeQuestions ? (
              <Button
                variant="primary"
                size="sm"
                rightIcon={<Brain className="w-3.5 h-3.5" />}
                onClick={() => onPracticeQuestions(topic.name)}
                className="font-bold shadow-warm"
              >
                Practise Questions
              </Button>
            ) : null}
          </div>
        </div>
      </div>

      {/* Stats & Diagnostic Summary Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card className="p-4 bg-white border border-[#E8E0D2] rounded-xl">
          <span className="text-[11px] font-bold text-[#8E879E] uppercase tracking-wider block mb-1">
            Learning Status
          </span>
          <span className="text-base font-bold text-[#292444] font-display">
            {topic.status.replace(/_/g, ' ')}
          </span>
        </Card>

        <Card className="p-4 bg-white border border-[#E8E0D2] rounded-xl">
          <span className="text-[11px] font-bold text-[#8E879E] uppercase tracking-wider block mb-1">
            Questions Attempted
          </span>
          <span className="text-base font-bold text-[#292444] font-display">
            {topic.questions_attempted} attempts
          </span>
        </Card>

        <Card className="p-4 bg-white border border-[#E8E0D2] rounded-xl">
          <span className="text-[11px] font-bold text-[#8E879E] uppercase tracking-wider block mb-1">
            Accuracy Rate
          </span>
          <span className="text-base font-bold text-emerald-700 font-display">
            {topic.accuracy_rate}%
          </span>
        </Card>

        <Card className="p-4 bg-white border border-[#E8E0D2] rounded-xl">
          <span className="text-[11px] font-bold text-[#8E879E] uppercase tracking-wider block mb-1">
            Coding Challenges Solved
          </span>
          <span className="text-base font-bold text-[#FF5B3D] font-display">
            {topic.coding_problems_solved} / {topic.dsa_problems.length}
          </span>
        </Card>
      </div>

      {/* Learning Objectives Box */}
      {topic.learning_objectives && (
        <Card className="p-6 bg-[#FAF6ED] border border-[#E8E0D2] rounded-2xl">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-[#FF5B3D]" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#292444]">
              Pedagogical Learning Objectives
            </h3>
          </div>
          <p className="text-xs sm:text-sm text-[#5E5875] leading-relaxed whitespace-pre-line">
            {topic.learning_objectives}
          </p>
        </Card>
      )}

      {/* Verified GeeksforGeeks Placement Assessment Banner */}
      {topic.assessment && (
        <Card className="p-6 bg-gradient-to-br from-[#292444] to-[#1c1830] text-white rounded-2xl shadow-warm-lg border border-[#3e3765]">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-[#FF5B3D] text-white uppercase tracking-wider">
                  <Sparkles className="w-3 h-3" />
                  Verified GFG Assessment
                </span>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-white/10 text-emerald-300">
                  <CheckCircle2 className="w-3 h-3" />
                  Authentic Placement Patterns
                </span>
              </div>
              <h3 className="text-xl font-bold font-display text-white">
                {topic.assessment.title}
              </h3>
              <p className="text-xs text-[#E8E0D2]/80 max-w-xl leading-relaxed">
                Diagnostic placement assessment referencing GeeksforGeeks placement patterns. Real question scenarios, code analysis, edge cases, and comprehensive explanations.
              </p>
              <div className="flex flex-wrap items-center gap-4 text-xs text-[#E8E0D2]/70 pt-1">
                <span className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-[#FF5B3D]" />
                  {topic.assessment.duration_minutes} Minutes
                </span>
                <span>•</span>
                <span className="flex items-center gap-1.5">
                  <HelpCircle className="w-3.5 h-3.5 text-[#FF5B3D]" />
                  {topic.assessment.questions_count} GFG Placement Questions
                </span>
                {topic.assessment.passing_score && (
                  <>
                    <span>•</span>
                    <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                      <Award className="w-3.5 h-3.5" />
                      Passing Score: {topic.assessment.passing_score}%
                    </span>
                  </>
                )}
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 flex-shrink-0">
              {onStartAssessment && (
                <Button
                  variant="primary"
                  size="md"
                  rightIcon={<PlayCircle className="w-4 h-4" />}
                  onClick={() => onStartAssessment(topic.assessment!.id)}
                  className="bg-[#FF5B3D] hover:bg-[#ff4724] text-white font-bold shadow-warm border-none px-6 py-2.5"
                >
                  Start Assessment Drill
                </Button>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-[#E8E0D2] gap-8">
        <button
          onClick={() => setActiveTab('materials')}
          className={`pb-3 text-sm font-bold border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'materials'
              ? 'border-[#FF5B3D] text-[#FF5B3D]'
              : 'border-transparent text-[#5E5875] hover:text-[#292444]'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          Learning Materials ({topic.resources.length})
        </button>

        <button
          onClick={() => setActiveTab('practice')}
          className={`pb-3 text-sm font-bold border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'practice'
              ? 'border-[#FF5B3D] text-[#FF5B3D]'
              : 'border-transparent text-[#5E5875] hover:text-[#292444]'
          }`}
        >
          <Brain className="w-4 h-4" />
          Practice Questions ({topic.practice_questions.length})
        </button>

        <button
          onClick={() => setActiveTab('dsa')}
          className={`pb-3 text-sm font-bold border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'dsa'
              ? 'border-[#FF5B3D] text-[#FF5B3D]'
              : 'border-transparent text-[#5E5875] hover:text-[#292444]'
          }`}
        >
          <Code2 className="w-4 h-4" />
          Linked DSA Problems ({topic.dsa_problems.length})
        </button>
      </div>

      {/* Tab 1: Learning Materials */}
      {activeTab === 'materials' && (
        <div className="space-y-4">
          {topic.resources.length === 0 ? (
            <div className="p-8 text-center border border-dashed border-[#E8E0D2] rounded-2xl bg-white">
              <BookOpen className="w-8 h-8 text-[#8E879E] mx-auto mb-2" />
              <p className="text-xs text-[#5E5875]">No learning resources published for this topic yet.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {topic.resources.map((res) => (
                <Card
                  key={res.id}
                  className="p-5 bg-white border border-[#E8E0D2] rounded-2xl shadow-xs flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="p-1.5 rounded-lg bg-[#FAF6ED] text-[#292444]">
                          <FileText className="w-4 h-4" />
                        </span>
                        <span className="text-[11px] font-bold uppercase tracking-wider text-[#8E879E]">
                          {res.resource_type.replace(/_/g, ' ')}
                        </span>
                      </div>
                      {res.is_completed ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                          <Check className="w-3 h-3" /> Studied
                        </span>
                      ) : (
                        <span className="text-[11px] text-[#8E879E] flex items-center gap-1">
                          <Clock className="w-3 h-3" /> {res.estimated_minutes} mins
                        </span>
                      )}
                    </div>
                    <h3 className="text-base font-bold text-[#292444] mb-2 font-display">{res.title}</h3>
                  </div>

                  <div className="pt-4 border-t border-[#E8E0D2]/60 flex items-center justify-between gap-3">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleOpenResource(res)}
                      className="text-xs font-semibold"
                    >
                      Read Study Guide
                    </Button>

                    {!res.is_completed && (
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={completingId === res.id}
                        onClick={() => handleMarkResourceComplete(res.id)}
                        className="text-xs text-[#292444]"
                      >
                        {completingId === res.id ? 'Saving...' : 'Mark Completed'}
                      </Button>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Practice Questions */}
      {activeTab === 'practice' && (
        <div className="space-y-4">
          {topic.assessment && (
            <div className="p-4 bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-[#292444] flex items-center justify-center text-white font-bold text-xs">
                  GFG
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#292444]">
                    GeeksforGeeks Verified Placement Assessment Drill
                  </h4>
                  <p className="text-[11px] text-[#5E5875]">
                    {topic.assessment.questions_count} questions • {topic.assessment.duration_minutes} min duration
                  </p>
                </div>
              </div>
              {onStartAssessment && (
                <Button
                  variant="primary"
                  size="sm"
                  rightIcon={<PlayCircle className="w-3.5 h-3.5" />}
                  onClick={() => onStartAssessment(topic.assessment!.id)}
                  className="font-bold text-xs"
                >
                  Take Full Assessment
                </Button>
              )}
            </div>
          )}

          {topic.practice_questions.length === 0 ? (
            <div className="p-8 text-center border border-dashed border-[#E8E0D2] rounded-2xl bg-white">
              <Brain className="w-8 h-8 text-[#8E879E] mx-auto mb-2" />
              <p className="text-xs text-[#5E5875]">No practice questions linked to this topic yet.</p>
            </div>
          ) : (
            <div className="divide-y divide-[#E8E0D2] border border-[#E8E0D2] bg-white rounded-2xl overflow-hidden shadow-xs">
              {topic.practice_questions.map((q, idx) => (
                <div key={q.id} className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-[#FAF6ED]/40 transition-colors">
                  <div className="flex items-start gap-3 flex-1">
                    <span className="text-xs font-bold text-[#8E879E] mt-0.5">
                      #{idx + 1}
                    </span>
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <span className="text-sm font-bold text-[#292444]">{q.title}</span>
                        <Badge variant="neutral" className="text-[10px]">
                          {q.difficulty}
                        </Badge>
                        <span className="text-[11px] text-[#8E879E]">{q.points} pt</span>
                      </div>
                      {q.content && (
                        <p className="text-xs text-[#5E5875] line-clamp-2 font-mono bg-[#FAF6ED]/60 p-2 rounded border border-[#E8E0D2]/50 mt-1 max-w-3xl whitespace-pre-line">
                          {q.content}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 self-end sm:self-center flex-shrink-0">
                    {q.attempts_count > 0 && (
                      <span className="text-xs font-semibold text-emerald-700">
                        {q.user_accuracy !== null ? `${q.user_accuracy}% accurate` : 'Attempted'}
                      </span>
                    )}
                    {topic.assessment && onStartAssessment ? (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => onStartAssessment(topic.assessment!.id)}
                        className="text-xs font-semibold"
                      >
                        Start Drill
                      </Button>
                    ) : onPracticeQuestions && (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => onPracticeQuestions(topic.name)}
                        className="text-xs font-semibold"
                      >
                        Practise
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Linked DSA Problems */}
      {activeTab === 'dsa' && (
        <div className="space-y-4">
          {topic.dsa_problems.length === 0 ? (
            <div className="p-8 text-center border border-dashed border-[#E8E0D2] rounded-2xl bg-white">
              <Code2 className="w-8 h-8 text-[#8E879E] mx-auto mb-2" />
              <p className="text-xs text-[#5E5875]">No algorithmic coding problems linked to this topic.</p>
            </div>
          ) : (
            <div className="divide-y divide-[#E8E0D2] border border-[#E8E0D2] bg-white rounded-2xl overflow-hidden shadow-xs">
              {topic.dsa_problems.map((p) => {
                const diffColor =
                  p.difficulty === 'EASY'
                    ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
                    : p.difficulty === 'MEDIUM'
                    ? 'text-amber-700 bg-amber-50 border-amber-200'
                    : 'text-rose-700 bg-rose-50 border-rose-200';

                return (
                  <div
                    key={p.id}
                    className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-[#FAF6ED]/40 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center font-bold text-xs text-[#292444]">
                        {p.problem_number}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-[#292444]">{p.title}</span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${diffColor}`}>
                            {p.difficulty}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 self-end sm:self-center">
                      <Badge
                        variant={p.status === 'SOLVED' ? 'success' : p.status === 'ATTEMPTED' ? 'coral' : 'neutral'}
                        className="text-[10px] font-bold"
                      >
                        {p.status}
                      </Badge>
                      {onSelectDsaProblem && (
                        <Button
                          variant="primary"
                          size="sm"
                          rightIcon={<Code2 className="w-3.5 h-3.5" />}
                          onClick={() => onSelectDsaProblem(p.slug)}
                          className="text-xs font-semibold shadow-warm"
                        >
                          Solve Problem
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Learning Resource Reader Modal */}
      {activeResource && (
        <div className="fixed inset-0 z-50 bg-[#292444]/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-[#E8E0D2] shadow-warm-lg max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden animate-fadeIn">
            {/* Modal Header */}
            <div className="p-6 border-b border-[#E8E0D2] flex items-center justify-between bg-[#FAF6ED]/50">
              <div>
                <span className="text-[10px] font-bold text-[#FF5B3D] uppercase tracking-wider block mb-1">
                  {activeResource.resource_type.replace(/_/g, ' ')}
                </span>
                <h3 className="text-lg font-bold text-[#292444] font-display">{activeResource.title}</h3>
              </div>
              <button
                onClick={() => setActiveResource(null)}
                className="w-8 h-8 rounded-full bg-white border border-[#E8E0D2] text-[#5E5875] hover:text-[#292444] flex items-center justify-center"
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-4 flex-1">
              {activeResource.description && (
                <div className="p-3 bg-[#FAF6ED] rounded-xl text-xs text-[#5E5875] border border-[#E8E0D2]/60">
                  {activeResource.description}
                </div>
              )}

              <div className="prose prose-sm max-w-none text-xs sm:text-sm text-[#292444] leading-relaxed whitespace-pre-line font-mono bg-white p-4 rounded-xl border border-[#E8E0D2]">
                {activeResource.content || 'Content is loading or being compiled by the editorial team.'}
              </div>

              {activeResource.external_url && (
                <a
                  href={activeResource.external_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-[#FF5B3D] hover:underline pt-2"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  View external reference material
                </a>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-[#E8E0D2] flex items-center justify-between bg-[#FAF6ED]/30">
              <span className="text-xs text-[#8E879E]">
                Estimated time: {activeResource.estimated_minutes} mins
              </span>
              <div className="flex items-center gap-2">
                {!activeResource.is_completed ? (
                  <Button
                    variant="primary"
                    size="sm"
                    rightIcon={<Check className="w-3.5 h-3.5" />}
                    onClick={() => handleMarkResourceComplete(activeResource.id)}
                    className="font-bold shadow-warm"
                  >
                    Mark as Studied
                  </Button>
                ) : (
                  <Badge variant="success" className="text-xs font-bold">
                    ✓ Completed
                  </Badge>
                )}
                <Button variant="secondary" size="sm" onClick={() => setActiveResource(null)}>
                  Close
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
