import React, { useState, useEffect } from 'react';
import {
  Compass,
  CheckCircle2,
  Clock,
  BookOpen,
  Code2,
  ChevronRight,
  Sparkles,
  ArrowRight,
  Target,
  RefreshCw,
  Layers,
  ChevronDown,
} from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import {
  fetchCareerPaths,
  selectCareerPath,
  fetchMyCareerGoal,
  fetchRoadmapTree,
  fetchNextRecommendedAction,
  type CareerPathItem,
  type StudentCareerGoal,
  type RoadmapTree,
  type NextActionResponse,
} from '../../services/roadmap';

interface CareerRoadmapViewProps {
  onSelectTopic: (topicId: string) => void;
  onLaunchDsa?: (slug: string) => void;
  onStartPractice?: () => void;
  onReviewMistakes?: () => void;
}

export const CareerRoadmapView: React.FC<CareerRoadmapViewProps> = ({
  onSelectTopic,
  onLaunchDsa,
  onStartPractice,
  onReviewMistakes,
}) => {
  const [careerPaths, setCareerPaths] = useState<CareerPathItem[]>([]);
  const [currentGoal, setCurrentGoal] = useState<StudentCareerGoal | null>(null);
  const [roadmapTree, setRoadmapTree] = useState<RoadmapTree | null>(null);
  const [nextAction, setNextAction] = useState<NextActionResponse | null>(null);
  const [isChangingGoal, setIsChangingGoal] = useState(false);
  const [expandedSubjects, setExpandedSubjects] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRoadmapData();
  }, []);

  const loadRoadmapData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [paths, goal] = await Promise.all([
        fetchCareerPaths(),
        fetchMyCareerGoal(),
      ]);
      setCareerPaths(paths);
      setCurrentGoal(goal);

      if (goal) {
        const [tree, rec] = await Promise.all([
          fetchRoadmapTree(goal.career_path_id),
          fetchNextRecommendedAction().catch(() => null),
        ]);
        setRoadmapTree(tree);
        setNextAction(rec);
        // Expand first subject by default
        if (tree.subjects.length > 0) {
          setExpandedSubjects({ [tree.subjects[0].id]: true });
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load career roadmap');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPath = async (pathId: string) => {
    setActionLoading(true);
    try {
      const goal = await selectCareerPath(pathId);
      setCurrentGoal(goal);
      setIsChangingGoal(false);
      const [tree, rec] = await Promise.all([
        fetchRoadmapTree(pathId),
        fetchNextRecommendedAction().catch(() => null),
      ]);
      setRoadmapTree(tree);
      setNextAction(rec);
      if (tree.subjects.length > 0) {
        setExpandedSubjects({ [tree.subjects[0].id]: true });
      }
    } catch (err: any) {
      alert(err.message || 'Failed to assign career path');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStartActivity = () => {
    if (!nextAction) return;

    if (nextAction.action_type === 'REVIEW_MISTAKES' || nextAction.action_type === 'REVISE_MISTAKES') {
      if (onReviewMistakes) {
        onReviewMistakes();
        return;
      }
    }

    if (nextAction.action_type === 'SOLVE_DSA') {
      if (nextAction.target_slug && onLaunchDsa) {
        onLaunchDsa(nextAction.target_slug);
        return;
      }
    }

    if (nextAction.action_type === 'SOLVE_PRACTICE') {
      if (onStartPractice) {
        onStartPractice();
        return;
      }
    }

    const topicId = nextAction.target_topic_id || nextAction.target_id;
    if (topicId) {
      onSelectTopic(topicId);
    } else if (onStartPractice) {
      onStartPractice();
    }
  };

  const toggleSubject = (subjectId: string) => {
    setExpandedSubjects((prev) => ({
      ...prev,
      [subjectId]: !prev[subjectId],
    }));
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[420px] p-8 text-center">
        <RefreshCw className="w-8 h-8 text-[#FF5B3D] animate-spin mb-4" />
        <h3 className="text-base font-bold text-[#292444] font-display">Loading Preparation Roadmap...</h3>
        <p className="text-xs text-[#5E5875] mt-1">Connecting syllabus hierarchy, practice banks, and coding challenges.</p>
      </div>
    );
  }

  // 1. Goal Selection View (if no goal set or student wants to switch)
  if (!currentGoal || isChangingGoal) {
    return (
      <div className="space-y-8 animate-fadeIn max-w-[1240px] mx-auto">
        <div className="border-b border-[#E8E0D2] pb-6 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="p-1.5 rounded-lg bg-[#FF5B3D]/10 text-[#FF5B3D]">
                <Target className="w-5 h-5" />
              </span>
              <span className="text-xs font-bold uppercase tracking-wider text-[#FF5B3D]">Career Goal & Roadmap</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#292444] font-display">
              {currentGoal ? 'Change Target Career Goal' : 'Select Your Placement Preparation Goal'}
            </h1>
            <p className="text-sm text-[#5E5875] mt-1">
              Select your primary engineering role to unlock a tailored, multi-subject curriculum covering Programming, DSA, Core CS, and Aptitude.
            </p>
          </div>
          {currentGoal && (
            <Button variant="secondary" size="sm" onClick={() => setIsChangingGoal(false)}>
              Back to Active Roadmap
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {careerPaths.map((path) => {
            const isCurrent = currentGoal?.career_path_id === path.id;
            return (
              <Card
                key={path.id}
                className={`p-6 flex flex-col justify-between border-2 transition-all duration-200 ${
                  isCurrent
                    ? 'border-[#FF5B3D] bg-white shadow-warm'
                    : 'border-[#E8E0D2] bg-white hover:border-[#292444]/40 hover:shadow-md'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-10 h-10 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D]">
                      <Compass className="w-5 h-5" />
                    </div>
                    {isCurrent && (
                      <Badge variant="coral" className="text-[11px] font-bold">
                        Current Goal
                      </Badge>
                    )}
                  </div>
                  <h3 className="text-lg font-bold text-[#292444] mb-1 font-display">{path.title}</h3>
                  <p className="text-xs font-semibold text-[#8E879E] mb-3">Target: {path.target_role}</p>
                  <p className="text-xs text-[#5E5875] leading-relaxed mb-6">{path.description}</p>
                </div>

                <div className="pt-4 border-t border-[#E8E0D2]/60">
                  <Button
                    variant={isCurrent ? 'secondary' : 'primary'}
                    size="sm"
                    className="w-full font-semibold"
                    disabled={actionLoading || isCurrent}
                    onClick={() => handleSelectPath(path.id)}
                  >
                    {isCurrent ? 'Active Curriculum' : 'Select Roadmap'}
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    );
  }

  // 2. Active Roadmap Tree & Preparation Hub
  return (
    <div className="space-y-8 animate-fadeIn max-w-[1240px] mx-auto">
      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-xs text-rose-700">
          {error}
        </div>
      )}
      {/* Header Banner */}
      <div className="border-b border-[#E8E0D2] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="p-1.5 rounded-lg bg-[#FF5B3D]/10 text-[#FF5B3D]">
              <Compass className="w-4 h-4" />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-[#FF5B3D]">
              Career Preparation Hub
            </span>
            <span className="text-xs text-[#8E879E]">·</span>
            <span className="text-xs font-semibold text-[#292444]">{currentGoal.career_path_title}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#292444] font-display">
            {currentGoal.target_role} Roadmap
          </h1>
          <p className="text-xs text-[#5E5875] mt-1">
            Structured curriculum across programming fundamentals, DSA, aptitude, and core computer science.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="secondary" size="sm" onClick={() => setIsChangingGoal(true)}>
            Change Goal
          </Button>
        </div>
      </div>

      {/* Progress & Next Recommended Activity Strip */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Overall Syllabus Progress Card */}
        <Card className="p-6 bg-white border border-[#E8E0D2] rounded-2xl shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-[#8E879E] uppercase tracking-wider">
                Syllabus Progress
              </span>
              <span className="text-xs font-bold text-[#FF5B3D]">
                {roadmapTree?.completed_topics || 0} / {roadmapTree?.total_topics || 0} Topics
              </span>
            </div>
            <div className="flex items-baseline gap-2 mb-3">
              <span className="text-4xl font-extrabold text-[#292444] font-display">
                {roadmapTree?.overall_progress_pct || 0}%
              </span>
              <span className="text-xs text-[#5E5875]">completed</span>
            </div>
            {/* Custom progress bar */}
            <div className="w-full bg-[#FAF6ED] rounded-full h-3 border border-[#E8E0D2] overflow-hidden p-0.5">
              <div
                className="bg-gradient-to-r from-[#FF5B3D] to-[#E0482B] h-full rounded-full transition-all duration-700"
                style={{ width: `${Math.min(100, roadmapTree?.overall_progress_pct || 0)}%` }}
              />
            </div>
          </div>

          <div className="pt-4 mt-4 border-t border-[#E8E0D2]/60 flex items-center justify-between text-xs text-[#5E5875]">
            <span>Verified Mastery Threshold</span>
            <span className="font-semibold text-[#292444]">≥ 70% Accuracy & 5+ Attempts</span>
          </div>
        </Card>

        {/* Recommended Next Action Banner */}
        <Card className="lg:col-span-2 p-6 bg-gradient-to-br from-[#292444] to-[#1E1A33] text-white rounded-2xl shadow-warm flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-[#FF5B3D]/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-[#FF5B3D]" />
              <span className="text-xs font-bold uppercase tracking-wider text-[#FF5B3D]">
                Recommended Next Step
              </span>
            </div>
            <h3 className="text-lg sm:text-xl font-bold font-display text-white mb-1.5">
              {nextAction?.title || 'Continue Next Topic'}
            </h3>
            <p className="text-xs text-white/80 leading-relaxed max-w-xl">
              {nextAction?.reason || 'System analyzed your progress across recent assessments and practice.'}
            </p>
          </div>

          <div className="relative z-10 pt-4 mt-4 border-t border-white/10 flex flex-wrap items-center justify-between gap-4">
            <span className="text-xs text-white/60">
              Action: {nextAction?.action_type?.replace(/_/g, ' ') || 'LEARNING DRILL'}
            </span>
            <div className="flex items-center gap-2">
              {nextAction && (
                <Button
                  variant="primary"
                  size="sm"
                  rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                  onClick={handleStartActivity}
                  className="font-bold shadow-warm"
                >
                  Start Activity
                </Button>
              )}
              {nextAction?.action_type === 'SOLVE_DSA' && nextAction.target_slug && onLaunchDsa && (
                <Button
                  variant="secondary"
                  size="sm"
                  rightIcon={<Code2 className="w-3.5 h-3.5" />}
                  onClick={() => onLaunchDsa(nextAction.target_slug!)}
                  className="font-bold bg-white/10 hover:bg-white/20 text-white border-none"
                >
                  Solve Problem
                </Button>
              )}
              {onStartPractice && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onStartPractice}
                  className="text-white border-white/20 hover:bg-white/10"
                >
                  Practice Engine
                </Button>
              )}
            </div>
          </div>
        </Card>
      </div>

      {/* Curriculum Subject Breakdown */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-[#292444] font-display flex items-center gap-2">
            <Layers className="w-5 h-5 text-[#FF5B3D]" />
            Preparation Roadmap Modules
          </h2>
          <span className="text-xs text-[#8E879E]">
            {roadmapTree?.subjects?.length || 0} Subject Domains
          </span>
        </div>

        {roadmapTree?.subjects.map((subject, index) => {
          const isExpanded = !!expandedSubjects[subject.id];
          return (
            <div
              key={subject.id}
              className="border border-[#E8E0D2] bg-white rounded-2xl overflow-hidden shadow-xs transition-all duration-200"
            >
              {/* Subject Header Row */}
              <div
                onClick={() => toggleSubject(subject.id)}
                className="p-5 sm:p-6 flex items-center justify-between cursor-pointer hover:bg-[#FAF6ED]/50 transition-colors select-none"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center font-bold text-sm text-[#292444]">
                    {String(index + 1).padStart(2, '0')}
                  </div>
                  <div>
                    <div className="flex items-center gap-2.5">
                      <h3 className="text-base font-bold text-[#292444] font-display">{subject.name}</h3>
                      <Badge variant="neutral" className="text-[10px] font-semibold">
                        {subject.topics.length} topics
                      </Badge>
                    </div>
                    {subject.description && (
                      <p className="text-xs text-[#5E5875] mt-0.5 line-clamp-1">{subject.description}</p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  {/* Subject progress pill */}
                  <div className="hidden sm:flex flex-col items-end">
                    <span className="text-xs font-bold text-[#292444]">{subject.progress_pct}%</span>
                    <div className="w-24 bg-[#FAF6ED] rounded-full h-1.5 border border-[#E8E0D2] overflow-hidden mt-1">
                      <div
                        className="bg-[#FF5B3D] h-full rounded-full"
                        style={{ width: `${subject.progress_pct}%` }}
                      />
                    </div>
                  </div>

                  <div className={`p-1.5 rounded-lg text-[#8E879E] transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}>
                    <ChevronDown className="w-5 h-5" />
                  </div>
                </div>
              </div>

              {/* Topics Sublist */}
              {isExpanded && (
                <div className="border-t border-[#E8E0D2] divide-y divide-[#E8E0D2]/60 bg-[#FAF6ED]/30">
                  {subject.topics.map((topic) => {
                    const statusVariant: 'success' | 'coral' | 'warning' | 'neutral' =
                      topic.status === 'MASTERED'
                        ? 'success'
                        : topic.status === 'COMPLETED'
                        ? 'coral'
                        : topic.status === 'IN_PROGRESS'
                        ? 'warning'
                        : 'neutral';

                    return (
                      <div
                        key={topic.id}
                        className="p-4 sm:px-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-white transition-colors"
                      >
                        <div className="flex items-start sm:items-center gap-3">
                          <div className="mt-1 sm:mt-0">
                            {topic.status === 'MASTERED' || topic.status === 'COMPLETED' ? (
                              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                            ) : (
                              <div className="w-4 h-4 rounded-full border-2 border-[#8E879E]/40" />
                            )}
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-bold text-[#292444]">{topic.name}</span>
                              <Badge variant={statusVariant} className="text-[10px] font-bold">
                                {topic.status.replace(/_/g, ' ')}
                              </Badge>
                              <Badge variant="neutral" className="text-[10px]">
                                {topic.difficulty}
                              </Badge>
                            </div>
                            <div className="flex flex-wrap items-center gap-4 text-xs text-[#8E879E] mt-1">
                              <span className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {topic.estimated_minutes} mins
                              </span>
                              <span className="flex items-center gap-1">
                                <BookOpen className="w-3 h-3" />
                                {topic.resources_count} materials
                              </span>
                              {topic.dsa_problems_count > 0 && (
                                <span className="flex items-center gap-1 text-[#292444]">
                                  <Code2 className="w-3 h-3 text-[#FF5B3D]" />
                                  {topic.dsa_problems_count} coding challenges
                                </span>
                              )}
                              {topic.questions_attempted > 0 && (
                                <span className="text-emerald-700 font-semibold">
                                  {topic.accuracy_rate}% accuracy ({topic.questions_attempted} attempts)
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 self-end sm:self-center">
                          <Button
                            variant="secondary"
                            size="sm"
                            rightIcon={<ChevronRight className="w-3.5 h-3.5" />}
                            onClick={() => onSelectTopic(topic.id)}
                            className="text-xs font-semibold py-1.5 px-3"
                          >
                            Study Topic
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
