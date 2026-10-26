import { useState, useEffect, useMemo } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { fetchAssessments, type AssessmentListItem } from '../../services/practice';
import {
  Calculator,
  Brain,
  BookOpenCheck,
  Timer,
  CheckCircle,
  ArrowRight,
  Sparkles,
  AlertCircle,
  Search,
  Database,
  Code2,
  CheckCircle2,
  X,
  Target,
} from 'lucide-react';

interface PracticeModuleListProps {
  onStartSession: (assessmentId: string, sessionType: 'PRACTICE' | 'TIMED_MOCK') => void;
  initialCategory?: string | null;
  initialTopic?: string | null;
  onClearFilter?: () => void;
  onLaunchDsa?: (slug?: string) => void;
}

export function PracticeModuleList({
  onStartSession,
  initialCategory,
  initialTopic,
  onClearFilter,
  onLaunchDsa,
}: PracticeModuleListProps) {
  const [assessments, setAssessments] = useState<AssessmentListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>(initialCategory || 'ALL');
  const [selectedTopic, setSelectedTopic] = useState<string>(initialTopic || 'ALL');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (initialCategory) {
      setSelectedCategory(initialCategory);
    }
    if (initialTopic) {
      setSelectedTopic(initialTopic);
    }
  }, [initialCategory, initialTopic]);

  useEffect(() => {
    loadAssessments();
  }, []);

  const loadAssessments = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchAssessments();
      setAssessments(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load assessments');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (category: string | null) => {
    switch (category) {
      case 'QUANTITATIVE_APTITUDE':
        return <Calculator className="w-5 h-5 text-[#FF5B3D]" />;
      case 'LOGICAL_REASONING':
        return <Brain className="w-5 h-5 text-[#292444]" />;
      case 'VERBAL_ABILITY':
        return <BookOpenCheck className="w-5 h-5 text-[#FF5B3D]" />;
      case 'SQL_DATABASES':
        return <Database className="w-5 h-5 text-[#292444]" />;
      case 'HR_BEHAVIORAL':
        return <CheckCircle2 className="w-5 h-5 text-[#15803D]" />;
      case 'PROGRAMMING_DSA':
        return <Code2 className="w-5 h-5 text-[#FF5B3D]" />;
      default:
        return <Sparkles className="w-5 h-5 text-[#FF5B3D]" />;
    }
  };

  const getCategoryLabel = (category: string | null) => {
    switch (category) {
      case 'QUANTITATIVE_APTITUDE':
        return 'Quantitative Aptitude';
      case 'LOGICAL_REASONING':
        return 'Logical Reasoning';
      case 'VERBAL_ABILITY':
        return 'Verbal Ability';
      case 'SQL_DATABASES':
        return 'Database & SQL';
      case 'HR_BEHAVIORAL':
        return 'HR & Behavioral';
      case 'PROGRAMMING_DSA':
        return 'DSA & Coding';
      default:
        return 'General Aptitude';
    }
  };

  // Extract unique topics available under current category
  const availableTopics = useMemo(() => {
    const list = assessments
      .filter((a) => {
        if (selectedCategory === 'ALL') return true;
        return a.category === selectedCategory;
      })
      .map((a) => a.topic)
      .filter((t): t is string => Boolean(t));

    return Array.from(new Set(list));
  }, [assessments, selectedCategory]);

  // Filtered assessment list
  const filtered = useMemo(() => {
    return assessments.filter((a) => {
      // Category filter
      if (selectedCategory !== 'ALL' && a.category !== selectedCategory) {
        return false;
      }
      // Topic filter
      if (selectedTopic !== 'ALL' && a.topic !== selectedTopic) {
        return false;
      }
      // Search query filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const titleMatch = a.title.toLowerCase().includes(q);
        const descMatch = (a.description || '').toLowerCase().includes(q);
        const topicMatch = (a.topic || '').toLowerCase().includes(q);
        const categoryMatch = (a.category || '').toLowerCase().includes(q);
        if (!titleMatch && !descMatch && !topicMatch && !categoryMatch) {
          return false;
        }
      }
      return true;
    });
  }, [assessments, selectedCategory, selectedTopic, searchQuery]);

  // Group assessments by topic for topic-wise display
  const groupedByTopic = useMemo(() => {
    const groups: Record<string, AssessmentListItem[]> = {};
    for (const item of filtered) {
      const groupKey = item.topic || 'General Diagnostics & Assessments';
      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(item);
    }
    return groups;
  }, [filtered]);

  const handleClearAllFilters = () => {
    setSelectedCategory('ALL');
    setSelectedTopic('ALL');
    setSearchQuery('');
    if (onClearFilter) {
      onClearFilter();
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in pb-16">
      {/* Header Banner */}
      <div className="bg-[#292444] text-white rounded-3xl p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="max-w-3xl">
            <div className="flex items-center gap-2 mb-3">
              <Badge variant="coral" className="text-xs uppercase tracking-wider font-bold">
                Topic-Wise Assessments
              </Badge>
              <Badge variant="neutral" className="text-xs text-white/80 border-white/20">
                Formative & Diagnostic
              </Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold font-display tracking-tight text-white mb-2">
              Assessments & Diagnostic Drills
            </h1>
            <p className="text-white/80 leading-relaxed text-sm">
              Practice verified placement diagnostics organized topic-wise across Quantitative Aptitude, Logical Reasoning,
              Verbal Ability, SQL, and Behavioral frameworks. Every attempt syncs mistakes to your personal Mistake Notebook with instant AI coaching proofs.
            </p>
          </div>

          {onLaunchDsa && (
            <div className="bg-white/10 rounded-2xl p-4 border border-white/10 shrink-0 max-w-sm">
              <div className="flex items-center gap-2 mb-1.5">
                <Code2 className="w-4 h-4 text-[#FF5B3D]" />
                <span className="text-xs font-bold uppercase tracking-wider text-white">DSA Code Runner</span>
              </div>
              <p className="text-xs text-white/70 mb-3">
                Solve 36 classic GeeksforGeeks problems across 12 DSA topics with live Python & Java automated judge execution.
              </p>
              <Button
                variant="primary"
                size="sm"
                onClick={() => onLaunchDsa()}
                rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                className="w-full text-xs shadow-sm"
              >
                Open DSA Studio
              </Button>
            </div>
          )}
        </div>

        {/* Category Filter Pills */}
        <div className="flex flex-wrap gap-2 mt-6 pt-6 border-t border-white/10">
          {[
            { id: 'ALL', label: 'All Modules' },
            { id: 'QUANTITATIVE_APTITUDE', label: 'Quantitative Aptitude' },
            { id: 'LOGICAL_REASONING', label: 'Logical Reasoning' },
            { id: 'VERBAL_ABILITY', label: 'Verbal Ability' },
            { id: 'SQL_DATABASES', label: 'Database & SQL' },
            { id: 'HR_BEHAVIORAL', label: 'HR & STAR Framework' },
            { id: 'PROGRAMMING_DSA', label: 'DSA & Coding' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setSelectedCategory(tab.id);
                setSelectedTopic('ALL');
              }}
              className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
                selectedCategory === tab.id
                  ? 'bg-[#FF5B3D] text-white shadow-sm'
                  : 'bg-white/10 text-white/80 hover:bg-white/20'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Topic-Wise Sub-Filter Bar & Search */}
      <div className="bg-white p-4 rounded-2xl border border-[#E8E0D2] shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#8E879E]" />
          <input
            type="text"
            placeholder="Search topic or assessment title..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl focus:outline-hidden focus:border-[#FF5B3D] transition-colors text-[#292444]"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#8E879E] hover:text-[#292444]"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Active Filters / Reset */}
        <div className="flex items-center gap-2 flex-wrap">
          {selectedTopic !== 'ALL' && (
            <div className="inline-flex items-center gap-1.5 bg-[#FF5B3D]/10 text-[#FF5B3D] px-3 py-1 rounded-full text-xs font-semibold border border-[#FF5B3D]/30">
              <Target className="w-3.5 h-3.5" />
              <span>Topic: {selectedTopic}</span>
              <button
                onClick={() => setSelectedTopic('ALL')}
                className="hover:text-red-700 ml-1"
                title="Remove topic filter"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}

          {(selectedCategory !== 'ALL' || selectedTopic !== 'ALL' || searchQuery) && (
            <button
              onClick={handleClearAllFilters}
              className="text-xs text-[#5E5875] hover:text-[#FF5B3D] underline underline-offset-2 transition-colors font-medium ml-1"
            >
              Reset Filters
            </button>
          )}

          <span className="text-xs text-[#8E879E] ml-auto">
            Showing {filtered.length} assessment{filtered.length === 1 ? '' : 's'}
          </span>
        </div>
      </div>

      {/* Available Topics Pills (if any exist) */}
      {availableTopics.length > 0 && (
        <div className="bg-[#FAF6ED] p-3.5 rounded-2xl border border-[#E8E0D2]/80">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[11px] font-bold text-[#292444] uppercase tracking-wider">
              Filter by Specific Topic:
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            <button
              onClick={() => setSelectedTopic('ALL')}
              className={`text-xs px-3 py-1 rounded-full border transition-all ${
                selectedTopic === 'ALL'
                  ? 'bg-[#292444] text-white border-[#292444] font-semibold'
                  : 'bg-white text-[#292444] border-[#E8E0D2] hover:border-[#FF5B3D]'
              }`}
            >
              All Topics ({availableTopics.length})
            </button>
            {availableTopics.map((topicName) => (
              <button
                key={topicName}
                onClick={() => setSelectedTopic(topicName)}
                className={`text-xs px-3 py-1 rounded-full border transition-all flex items-center gap-1.5 ${
                  selectedTopic === topicName
                    ? 'bg-[#FF5B3D] text-white border-[#FF5B3D] font-semibold shadow-2xs'
                    : 'bg-white text-[#292444] border-[#E8E0D2] hover:border-[#FF5B3D]'
                }`}
              >
                <span>{topicName}</span>
                <span className="text-[10px] opacity-75">
                  ({assessments.filter((a) => a.topic === topicName).length})
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
          <Button variant="secondary" size="sm" onClick={loadAssessments} className="ml-auto">
            Retry
          </Button>
        </div>
      )}

      {/* Loading state */}
      {loading ? (
        <div className="py-20 text-center text-[#292444]/60">
          <div className="inline-block w-8 h-8 border-4 border-[#FF5B3D] border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-sm font-medium">Loading published topic-wise assessments...</p>
        </div>
      ) : filtered.length === 0 ? (
        <Card className="p-12 text-center bg-white border border-[#E8E0D2] rounded-3xl">
          <Sparkles className="w-12 h-12 text-[#FF5B3D] mx-auto mb-3 opacity-60" />
          <h3 className="text-lg font-bold text-[#292444] mb-1">No assessments found</h3>
          <p className="text-xs text-[#292444]/60 max-w-md mx-auto mb-4">
            No published assessments match the current topic or category filter. Try clearing filters or selecting another topic.
          </p>
          <Button variant="secondary" size="sm" onClick={handleClearAllFilters} className="text-xs">
            Clear Filters
          </Button>
        </Card>
      ) : (
        /* Topic-Wise Grouped Assessment Sections */
        <div className="space-y-8">
          {Object.entries(groupedByTopic).map(([topicTitle, items]) => (
            <div key={topicTitle} className="space-y-4">
              {/* Topic Section Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-[#E8E0D2]">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center shrink-0">
                    {getCategoryIcon(items[0]?.category || null)}
                  </div>
                  <div>
                    <h2 className="text-base sm:text-lg font-bold text-[#292444] font-display flex items-center gap-2">
                      <span>{topicTitle}</span>
                      <Badge variant="neutral" className="text-[10px] font-medium">
                        {getCategoryLabel(items[0]?.category || null)}
                      </Badge>
                    </h2>
                  </div>
                </div>
                <span className="text-xs text-[#5E5875] font-medium">
                  {items.length} Diagnostic Drill{items.length === 1 ? '' : 's'} Available
                </span>
              </div>

              {/* Assessment Cards Grid for this Topic */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {items.map((item) => (
                  <Card
                    key={item.id}
                    className="p-5 flex flex-col justify-between hover:shadow-md hover:border-[#FF5B3D]/50 transition-all border border-[#E8E0D2] bg-white group rounded-2xl"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <Badge variant="coral" className="text-[10px] font-bold">
                          {item.topic || getCategoryLabel(item.category)}
                        </Badge>
                        <Badge variant="neutral" className="text-[10px] font-semibold">
                          v{item.version}
                        </Badge>
                      </div>

                      <h3 className="text-sm sm:text-base font-bold text-[#292444] mb-2 leading-snug group-hover:text-[#FF5B3D] transition-colors font-display">
                        {item.title}
                      </h3>

                      <p className="text-xs text-[#5E5875] mb-4 line-clamp-3 leading-relaxed">
                        {item.description || 'Verified topic-specific diagnostic drill with step-by-step proofs.'}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-[#E8E0D2]/60">
                      <div className="grid grid-cols-2 gap-2 text-xs text-[#5E5875] mb-3.5">
                        <div className="flex items-center gap-1.5">
                          <Timer className="w-3.5 h-3.5 text-[#292444]/50" />
                          <span>{item.duration_minutes} mins</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <CheckCircle className="w-3.5 h-3.5 text-[#292444]/50" />
                          <span>{item.question_count} Questions</span>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          variant="primary"
                          size="sm"
                          className="flex-1 text-xs shadow-2xs"
                          onClick={() => onStartSession(item.id, 'PRACTICE')}
                        >
                          Start Practice
                          <ArrowRight className="w-3 h-3 ml-1" />
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          className="text-xs text-[#292444]"
                          onClick={() => onStartSession(item.id, 'TIMED_MOCK')}
                        >
                          Timed Mock
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
