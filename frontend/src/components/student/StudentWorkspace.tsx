import { useState, useEffect, useCallback } from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { EmptyState } from '../common/EmptyState';
import { EditProfileModal } from './EditProfileModal';
import { LogActivityModal } from './LogActivityModal';
import { CreateGoalModal } from './CreateGoalModal';
import {
  fetchStudentProfile,
  fetchWorkspaceSummary,
  fetchActivities,
  deleteActivity,
  fetchGoals,
  updateGoal,
  deleteGoal,
  type StudentProfileDetailed,
  type StudentWorkspaceSummary,
  type PreparationActivity,
  type LearningGoal,
} from '../../services/student';
import {
  UserCheck,
  Edit3,
  Clock,
  CheckCircle2,
  Brain,
  Target,
  Plus,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Filter,
  Layers,
  Sparkles,
  BookOpenCheck,
  Check,
} from 'lucide-react';

export function StudentWorkspace() {
  const [profile, setProfile] = useState<StudentProfileDetailed | null>(null);
  const [summary, setSummary] = useState<StudentWorkspaceSummary | null>(null);
  const [activities, setActivities] = useState<PreparationActivity[]>([]);
  const [goals, setGoals] = useState<LearningGoal[]>([]);
  const [totalActivities, setTotalActivities] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [activeTab, setActiveTab] = useState<'activities' | 'goals'>('activities');

  // Filters
  const [categoryFilter, setCategoryFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [stateFilter, setStateFilter] = useState('');

  // Modals
  const [isEditProfileOpen, setIsEditProfileOpen] = useState(false);
  const [isLogActivityOpen, setIsLogActivityOpen] = useState(false);
  const [isCreateGoalOpen, setIsCreateGoalOpen] = useState(false);

  // Loading states
  const [isLoading, setIsLoading] = useState(true);
  const [isTableLoading, setIsTableLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load initial workspace data
  const loadWorkspaceData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [profData, sumData, goalsData] = await Promise.all([
        fetchStudentProfile(),
        fetchWorkspaceSummary(),
        fetchGoals(),
      ]);
      setProfile(profData);
      setSummary(sumData);
      setGoals(goalsData);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load workspace data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load paginated & filtered activities
  const loadActivitiesData = useCallback(async (page: number) => {
    setIsTableLoading(true);
    try {
      const data = await fetchActivities({
        page,
        page_size: 10,
        category: categoryFilter || undefined,
        activity_type: typeFilter || undefined,
        completion_state: stateFilter || undefined,
      });
      setActivities(data.items);
      setTotalActivities(data.total);
      setCurrentPage(data.page);
      setTotalPages(data.total_pages);
    } catch (err: unknown) {
      console.error('Error fetching activities:', err);
    } finally {
      setIsTableLoading(false);
    }
  }, [categoryFilter, typeFilter, stateFilter]);

  useEffect(() => {
    loadWorkspaceData();
  }, [loadWorkspaceData]);

  useEffect(() => {
    loadActivitiesData(currentPage);
  }, [loadActivitiesData, currentPage]);

  const handleDeleteActivity = async (id: string) => {
    if (!confirm('Are you sure you want to delete this activity record?')) return;
    try {
      await deleteActivity(id);
      loadActivitiesData(currentPage);
      // Refresh summary telemetry
      const sum = await fetchWorkspaceSummary();
      setSummary(sum);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to delete activity');
    }
  };

  const handleCompleteGoal = async (goal: LearningGoal) => {
    try {
      await updateGoal(goal.id, {
        current_value: goal.target_value,
        status: 'COMPLETED',
      });
      const updatedGoals = await fetchGoals();
      setGoals(updatedGoals);
      const sum = await fetchWorkspaceSummary();
      setSummary(sum);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to update goal');
    }
  };

  const handleDeleteGoal = async (id: string) => {
    if (!confirm('Are you sure you want to delete this learning goal?')) return;
    try {
      await deleteGoal(id);
      const updatedGoals = await fetchGoals();
      setGoals(updatedGoals);
      const sum = await fetchWorkspaceSummary();
      setSummary(sum);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to delete goal');
    }
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`;
    const hrs = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hrs}h ${mins}m` : `${hrs}h`;
  };

  const formatPlacementBadge = (status: string) => {
    switch (status) {
      case 'PLACED':
        return <Badge variant="success">Placed</Badge>;
      case 'IN_PROCESS':
        return <Badge variant="coral">Interviewing</Badge>;
      case 'OPTED_OUT':
        return <Badge variant="neutral">Opted Out</Badge>;
      default:
        return <Badge variant="neutral">Actively Preparing</Badge>;
    }
  };

  const formatCategoryName = (cat: string) => {
    return cat
      .split('_')
      .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
      .join(' ');
  };

  const formatActivityTypeName = (type: string) => {
    switch (type) {
      case 'PRACTICE_SESSION':
        return 'Practice Drill';
      case 'MOCK_TEST':
        return 'Mock Test';
      case 'CONCEPT_REVISION':
        return 'Concept Revision';
      case 'MISTAKE_REVIEW':
        return 'Mistake Review';
      case 'SELF_STUDY':
        return 'Self Study';
      default:
        return type;
    }
  };

  if (isLoading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center gap-3">
        <div className="w-8 h-8 border-2 border-[#FF5B3D] border-t-transparent rounded-full animate-spin" />
        <p className="text-sm font-medium text-[#5E5875]">Loading your placement preparation workspace...</p>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="p-8 rounded-2xl bg-white border border-[#E8E0D2] text-center max-w-lg mx-auto">
        <h3 className="text-lg font-bold text-[#292444] mb-2 font-display">Workspace Initialization Required</h3>
        <p className="text-sm text-[#5E5875] mb-6">
          {error || 'Your student academic profile is pending assignment by your institution.'}
        </p>
        <Button variant="primary" onClick={loadWorkspaceData}>
          Retry Connection
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-10 animate-in fade-in">
      {/* Student Academic Profile Header Card */}
      <Card className="p-6 sm:p-8 bg-white border border-[#E8E0D2] shadow-warm-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="flex items-start sm:items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D] shrink-0">
              <UserCheck className="w-7 h-7" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2.5 mb-1.5">
                <h2 className="text-2xl font-bold text-[#292444] font-display">{profile.user_full_name}</h2>
                <span className="px-2.5 py-0.5 rounded-md bg-[#FAF6ED] border border-[#E8E0D2] font-mono text-xs font-semibold text-[#292444]">
                  {profile.roll_number}
                </span>
                {formatPlacementBadge(profile.placement_status)}
              </div>
              <div className="flex flex-wrap items-center gap-y-1 gap-x-4 text-xs text-[#5E5875]">
                <span>
                  <strong>Institution:</strong> {profile.institution_name}
                </span>
                <span>•</span>
                <span>
                  <strong>Department:</strong> {profile.department_name || profile.department_code || 'General'}
                </span>
                <span>•</span>
                <span>
                  <strong>Cohort:</strong> {profile.cohort_graduation_year ? `${profile.cohort_graduation_year} Batch` : 'Standard'} {profile.cohort_section ? `(Sec ${profile.cohort_section})` : ''}
                </span>
                {profile.cgpa !== null && (
                  <>
                    <span>•</span>
                    <span className="font-semibold text-[#292444]">
                      CGPA: {profile.cgpa.toFixed(2)}
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <Button
              variant="secondary"
              size="sm"
              leftIcon={<Edit3 className="w-3.5 h-3.5" />}
              onClick={() => setIsEditProfileOpen(true)}
            >
              Edit Profile
            </Button>
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus className="w-3.5 h-3.5" />}
              onClick={() => setIsLogActivityOpen(true)}
            >
              Log Activity
            </Button>
          </div>
        </div>
      </Card>

      {/* Verified Telemetry Metrics (Rule 8: Zero Fake Data) */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-[#FF5B3D]">
              Verified Telemetry (Rule 8 Compliant)
            </span>
            <h3 className="text-lg font-bold text-[#292444] font-display">
              Preparation Standing & Volume
            </h3>
          </div>
          <Badge variant="neutral" hasDot>
            Live PostgreSQL Aggregation
          </Badge>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card variant="subtle" className="p-5 flex items-center gap-4">
            <div className="w-11 h-11 rounded-xl bg-white border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D] shrink-0">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-[#5E5875]">Total Prep Time</p>
              <h4 className="text-2xl font-bold text-[#292444] font-display">
                {summary ? formatDuration(summary.total_duration_minutes) : '0m'}
              </h4>
            </div>
          </Card>

          <Card variant="subtle" className="p-5 flex items-center gap-4">
            <div className="w-11 h-11 rounded-xl bg-white border border-[#E8E0D2] flex items-center justify-center text-[#15803D] shrink-0">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-[#5E5875]">Completed Activities</p>
              <h4 className="text-2xl font-bold text-[#292444] font-display">
                {summary ? summary.completed_activities : 0}
              </h4>
            </div>
          </Card>

          <Card variant="subtle" className="p-5 flex items-center gap-4">
            <div className="w-11 h-11 rounded-xl bg-white border border-[#E8E0D2] flex items-center justify-center text-[#292444] shrink-0">
              <Brain className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-[#5E5875]">Topics Explored</p>
              <h4 className="text-2xl font-bold text-[#292444] font-display">
                {summary ? summary.unique_topics_count : 0}
              </h4>
            </div>
          </Card>

          <Card variant="subtle" className="p-5 flex items-center gap-4">
            <div className="w-11 h-11 rounded-xl bg-white border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D] shrink-0">
              <Target className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-[#5E5875]">Active Goals</p>
              <h4 className="text-2xl font-bold text-[#292444] font-display">
                {summary ? summary.active_goals_count : 0}
              </h4>
            </div>
          </Card>
        </div>
      </section>

      {/* Main Workspace Tabs */}
      <section className="space-y-6">
        <div className="flex border-b border-[#E8E0D2]">
          <button
            onClick={() => setActiveTab('activities')}
            className={`pb-3.5 px-4 text-sm font-bold transition-all relative ${
              activeTab === 'activities'
                ? 'text-[#292444] border-b-2 border-[#FF5B3D]'
                : 'text-[#5E5875] hover:text-[#292444]'
            }`}
          >
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4" />
              <span>Preparation History ({totalActivities})</span>
            </div>
          </button>

          <button
            onClick={() => setActiveTab('goals')}
            className={`pb-3.5 px-4 text-sm font-bold transition-all relative ${
              activeTab === 'goals'
                ? 'text-[#292444] border-b-2 border-[#FF5B3D]'
                : 'text-[#5E5875] hover:text-[#292444]'
            }`}
          >
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4" />
              <span>Learning Goals ({goals.length})</span>
            </div>
          </button>
        </div>

        {/* Tab 1: Preparation Activities History */}
        {activeTab === 'activities' && (
          <div className="space-y-6 animate-in fade-in">
            {/* Filter Bar */}
            <div className="p-4 rounded-2xl bg-white border border-[#E8E0D2] flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-[#5E5875]">
                  <Filter className="w-3.5 h-3.5" />
                  <span>Filter by:</span>
                </div>

                <select
                  value={categoryFilter}
                  onChange={(e) => {
                    setCategoryFilter(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="px-3 py-1.5 rounded-lg border border-[#E8E0D2] bg-[#FAF6ED] text-xs text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
                >
                  <option value="">All Categories</option>
                  <option value="QUANTITATIVE_APTITUDE">Quantitative Aptitude</option>
                  <option value="LOGICAL_REASONING">Logical Reasoning</option>
                  <option value="VERBAL_ABILITY">Verbal Ability</option>
                  <option value="PROGRAMMING">Programming & DSA</option>
                  <option value="SQL">SQL & Databases</option>
                  <option value="CORE_TECHNICAL">Core Technical Concepts</option>
                  <option value="HR_BEHAVIORAL">HR & Behavioral STAR</option>
                  <option value="GENERAL">General Prep</option>
                </select>

                <select
                  value={typeFilter}
                  onChange={(e) => {
                    setTypeFilter(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="px-3 py-1.5 rounded-lg border border-[#E8E0D2] bg-[#FAF6ED] text-xs text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
                >
                  <option value="">All Activity Types</option>
                  <option value="PRACTICE_SESSION">Practice Drill</option>
                  <option value="MOCK_TEST">Mock Assessment</option>
                  <option value="CONCEPT_REVISION">Concept Revision</option>
                  <option value="MISTAKE_REVIEW">Mistake Review</option>
                  <option value="SELF_STUDY">Self Study</option>
                </select>

                <select
                  value={stateFilter}
                  onChange={(e) => {
                    setStateFilter(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="px-3 py-1.5 rounded-lg border border-[#E8E0D2] bg-[#FAF6ED] text-xs text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
                >
                  <option value="">All States</option>
                  <option value="COMPLETED">Completed</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="ABANDONED">Partially Done</option>
                </select>

                {(categoryFilter || typeFilter || stateFilter) && (
                  <button
                    onClick={() => {
                      setCategoryFilter('');
                      setTypeFilter('');
                      setStateFilter('');
                      setCurrentPage(1);
                    }}
                    className="text-xs text-[#FF5B3D] hover:underline font-semibold"
                  >
                    Reset Filters
                  </button>
                )}
              </div>

              <Button
                variant="primary"
                size="sm"
                leftIcon={<Plus className="w-3.5 h-3.5" />}
                onClick={() => setIsLogActivityOpen(true)}
              >
                Log Activity
              </Button>
            </div>

            {/* Activities Table / List */}
            {isTableLoading ? (
              <div className="py-12 flex justify-center">
                <div className="w-6 h-6 border-2 border-[#FF5B3D] border-t-transparent rounded-full animate-spin" />
              </div>
            ) : activities.length === 0 ? (
              <Card className="p-8">
                <EmptyState
                  icon={<BookOpenCheck className="w-8 h-8 text-[#5E5875]" />}
                  title="No Preparation Activities Recorded Yet"
                  description="Begin tracking your placement preparation journey by recording practice drills, concept revisions, or self-study sessions. All metrics are calculated from real records."
                  actionText="Log Your First Activity"
                  onAction={() => setIsLogActivityOpen(true)}
                />
              </Card>
            ) : (
              <div className="bg-white rounded-2xl border border-[#E8E0D2] overflow-hidden shadow-xs">
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-[#FAF6ED] border-b border-[#E8E0D2] text-[#5E5875] font-semibold uppercase tracking-wider text-[11px]">
                        <th className="py-3 px-4">Topic & Notes</th>
                        <th className="py-3 px-4">Category</th>
                        <th className="py-3 px-4">Type</th>
                        <th className="py-3 px-4">Duration</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4">Date</th>
                        <th className="py-3 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E8E0D2]">
                      {activities.map((act) => (
                        <tr key={act.id} className="hover:bg-[#FAF6ED]/40 transition-colors">
                          <td className="py-3 px-4">
                            <span className="font-bold text-[#292444] text-sm block">{act.topic}</span>
                            {act.notes && (
                              <p className="text-xs text-[#5E5875] line-clamp-1 mt-0.5 max-w-sm">{act.notes}</p>
                            )}
                          </td>
                          <td className="py-3 px-4">
                            <Badge variant="neutral">{formatCategoryName(act.category)}</Badge>
                          </td>
                          <td className="py-3 px-4 text-[#5E5875] font-medium">
                            {formatActivityTypeName(act.activity_type)}
                          </td>
                          <td className="py-3 px-4 font-mono font-semibold text-[#292444]">
                            {formatDuration(act.duration_minutes)}
                          </td>
                          <td className="py-3 px-4">
                            {act.completion_state === 'COMPLETED' ? (
                              <span className="inline-flex items-center gap-1 text-[#15803D] font-semibold text-[11px]">
                                <Check className="w-3.5 h-3.5" /> Completed
                              </span>
                            ) : act.completion_state === 'IN_PROGRESS' ? (
                              <span className="text-[#FF5B3D] font-semibold text-[11px]">In Progress</span>
                            ) : (
                              <span className="text-[#8E879E] font-semibold text-[11px]">Paused</span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-[#8E879E] whitespace-nowrap">
                            {new Date(act.activity_date).toLocaleDateString(undefined, {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric',
                            })}
                          </td>
                          <td className="py-3 px-4 text-right">
                            <button
                              onClick={() => handleDeleteActivity(act.id)}
                              className="p-1.5 rounded-lg text-[#8E879E] hover:text-[#FF5B3D] hover:bg-[#FFF5F3] transition-colors"
                              title="Delete activity record"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination Controls */}
                {totalPages > 1 && (
                  <div className="p-4 border-t border-[#E8E0D2] flex items-center justify-between text-xs text-[#5E5875]">
                    <span>
                      Showing Page {currentPage} of {totalPages} ({totalActivities} total records)
                    </span>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={currentPage <= 1}
                        onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                        leftIcon={<ChevronLeft className="w-3.5 h-3.5" />}
                      >
                        Prev
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={currentPage >= totalPages}
                        onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                        rightIcon={<ChevronRight className="w-3.5 h-3.5" />}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Learning Goals & Targets */}
        {activeTab === 'goals' && (
          <div className="space-y-6 animate-in fade-in">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-base font-bold text-[#292444] font-display">Target Preparation Goals</h4>
                <p className="text-xs text-[#5E5875]">Measurable targets updated by your logged activity</p>
              </div>
              <Button
                variant="primary"
                size="sm"
                leftIcon={<Plus className="w-3.5 h-3.5" />}
                onClick={() => setIsCreateGoalOpen(true)}
              >
                New Goal
              </Button>
            </div>

            {goals.length === 0 ? (
              <Card className="p-8">
                <EmptyState
                  icon={<Target className="w-8 h-8 text-[#5E5875]" />}
                  title="No Active Learning Goals Set"
                  description="Set measurable targets (e.g. 120 minutes of Quantitative Aptitude practice or 50 DSA problems) to guide your weekly preparation cadence."
                  actionText="Create Your First Goal"
                  onAction={() => setIsCreateGoalOpen(true)}
                />
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {goals.map((g) => (
                  <Card key={g.id} className="p-6 bg-white border border-[#E8E0D2] flex flex-col justify-between">
                    <div>
                      <div className="flex items-start justify-between gap-3 mb-3">
                        <Badge variant="coral">{formatCategoryName(g.category)}</Badge>
                        <span
                          className={`text-[11px] font-bold px-2 py-0.5 rounded-md ${
                            g.status === 'COMPLETED'
                              ? 'bg-[#EBF7EE] text-[#15803D]'
                              : 'bg-[#FAF6ED] text-[#292444]'
                          }`}
                        >
                          {g.status}
                        </span>
                      </div>

                      <h4 className="text-base font-bold text-[#292444] mb-2 font-display">{g.title}</h4>

                      <div className="space-y-2 mb-4">
                        <div className="flex justify-between text-xs text-[#5E5875]">
                          <span>Progress</span>
                          <span className="font-semibold text-[#292444]">
                            {g.current_value} / {g.target_value} {g.target_type === 'MINUTES_PRACTICED' ? 'mins' : ''}
                          </span>
                        </div>
                        <div className="w-full h-2 rounded-full bg-[#FAF6ED] border border-[#E8E0D2] overflow-hidden">
                          <div
                            className="h-full bg-[#FF5B3D] rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(100, g.progress_percentage)}%` }}
                          />
                        </div>
                        <div className="flex justify-between text-[11px] text-[#8E879E]">
                          <span>{g.progress_percentage}% completed</span>
                          {g.deadline && <span>Due: {new Date(g.deadline).toLocaleDateString()}</span>}
                        </div>
                      </div>
                    </div>

                    <div className="pt-4 border-t border-[#E8E0D2] flex items-center justify-between">
                      {g.status !== 'COMPLETED' ? (
                        <button
                          onClick={() => handleCompleteGoal(g)}
                          className="text-xs font-semibold text-[#15803D] hover:underline flex items-center gap-1"
                        >
                          <Check className="w-3.5 h-3.5" /> Mark Done
                        </button>
                      ) : (
                        <span className="text-xs font-semibold text-[#15803D] flex items-center gap-1">
                          <Sparkles className="w-3.5 h-3.5" /> Goal Achieved!
                        </span>
                      )}

                      <button
                        onClick={() => handleDeleteGoal(g.id)}
                        className="text-xs text-[#8E879E] hover:text-[#FF5B3D] transition-colors p-1"
                        title="Delete Goal"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </section>

      {/* Edit Profile Modal */}
      {isEditProfileOpen && profile && (
        <EditProfileModal
          isOpen={isEditProfileOpen}
          profile={profile}
          onClose={() => setIsEditProfileOpen(false)}
          onSuccess={(updated) => {
            setProfile(updated);
          }}
        />
      )}

      {/* Log Activity Modal */}
      {isLogActivityOpen && (
        <LogActivityModal
          isOpen={isLogActivityOpen}
          onClose={() => setIsLogActivityOpen(false)}
          onSuccess={async () => {
            loadActivitiesData(1);
            const sum = await fetchWorkspaceSummary();
            setSummary(sum);
            const updatedGoals = await fetchGoals();
            setGoals(updatedGoals);
          }}
        />
      )}

      {/* Create Goal Modal */}
      {isCreateGoalOpen && (
        <CreateGoalModal
          isOpen={isCreateGoalOpen}
          onClose={() => setIsCreateGoalOpen(false)}
          onSuccess={async () => {
            const updatedGoals = await fetchGoals();
            setGoals(updatedGoals);
            const sum = await fetchWorkspaceSummary();
            setSummary(sum);
          }}
        />
      )}
    </div>
  );
}
