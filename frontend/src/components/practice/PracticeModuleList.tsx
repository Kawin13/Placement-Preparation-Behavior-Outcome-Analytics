import { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { fetchAssessments, type AssessmentListItem } from '../../services/practice';
import { Calculator, Brain, BookOpenCheck, Timer, CheckCircle, ArrowRight, Sparkles, AlertCircle } from 'lucide-react';

interface PracticeModuleListProps {
  onStartSession: (assessmentId: string, sessionType: 'PRACTICE' | 'TIMED_MOCK') => void;
}

export function PracticeModuleList({ onStartSession }: PracticeModuleListProps) {
  const [assessments, setAssessments] = useState<AssessmentListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>('ALL');

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
        return <Brain className="w-5 h-5 text-[#FF5B3D]" />;
      case 'VERBAL_ABILITY':
        return <BookOpenCheck className="w-5 h-5 text-[#FF5B3D]" />;
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
      default:
        return 'General Aptitude';
    }
  };

  const filtered = assessments.filter((a) => {
    if (selectedFilter === 'ALL') return true;
    return a.category === selectedFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-[#292444] text-white rounded-3xl p-8 shadow-sm">
        <div className="max-w-3xl">
          <Badge variant="warning" className="mb-3 text-xs uppercase tracking-wider font-semibold">
            Formative Practice & Diagnostics
          </Badge>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Practice Engine</h1>
          <p className="text-white/80 leading-relaxed text-sm">
            Engage with college-approved placement diagnostics in Quantitative Aptitude, Logical Reasoning, and Verbal Ability.
            Attempts are scored deterministically with zero penalties for incorrect responses, and all missed concepts sync automatically to your personal Mistake Notebook.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap gap-2 mt-6 pt-6 border-t border-white/10">
          {[
            { id: 'ALL', label: 'All Modules' },
            { id: 'QUANTITATIVE_APTITUDE', label: 'Quantitative' },
            { id: 'LOGICAL_REASONING', label: 'Logical Reasoning' },
            { id: 'VERBAL_ABILITY', label: 'Verbal Ability' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedFilter(tab.id)}
              className={`px-4 py-2 rounded-full text-xs font-medium transition-all ${
                selectedFilter === tab.id
                  ? 'bg-[#FF5B3D] text-white shadow-sm'
                  : 'bg-white/10 text-white/80 hover:bg-white/20'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

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

      {/* Loading */}
      {loading ? (
        <div className="py-20 text-center text-[#292444]/60">
          <div className="inline-block w-8 h-8 border-4 border-[#FF5B3D] border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-sm font-medium">Loading published diagnostic banks...</p>
        </div>
      ) : filtered.length === 0 ? (
        <Card className="p-12 text-center">
          <Sparkles className="w-12 h-12 text-[#FF5B3D] mx-auto mb-3 opacity-60" />
          <h3 className="text-lg font-bold text-[#292444] mb-1">No assessments found</h3>
          <p className="text-xs text-[#292444]/60 max-w-md mx-auto">
            There are currently no published assessments matching the selected category. Check back soon or switch filters.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((item) => (
            <Card
              key={item.id}
              className="p-6 flex flex-col justify-between hover:shadow-md transition-all border border-[#E8E0D2] bg-white group"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-2xl bg-[#FAF6ED] flex items-center justify-center border border-[#E8E0D2]">
                    {getCategoryIcon(item.category)}
                  </div>
                  <Badge variant="neutral" className="text-xs font-semibold">
                    v{item.version}
                  </Badge>
                </div>

                <Badge variant="neutral" className="mb-2 text-[11px] font-semibold">
                  {getCategoryLabel(item.category)}
                </Badge>

                <h3 className="text-base font-bold text-[#292444] mb-2 leading-snug group-hover:text-[#FF5B3D] transition-colors">
                  {item.title}
                </h3>

                <p className="text-xs text-[#292444]/70 mb-5 line-clamp-3 leading-relaxed">
                  {item.description || 'College curated problem set with step-by-step proofs.'}
                </p>
              </div>

              <div className="pt-4 border-t border-[#E8E0D2]/60">
                <div className="grid grid-cols-2 gap-2 text-xs text-[#292444]/70 mb-4">
                  <div className="flex items-center gap-1.5">
                    <Timer className="w-3.5 h-3.5 text-[#292444]/40" />
                    <span>{item.duration_minutes} mins</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <CheckCircle className="w-3.5 h-3.5 text-[#292444]/40" />
                    <span>{item.question_count} Questions</span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="primary"
                    size="sm"
                    className="flex-1 text-xs"
                    onClick={() => onStartSession(item.id, 'PRACTICE')}
                  >
                    Start Practice
                    <ArrowRight className="w-3.5 h-3.5 ml-1" />
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    className="text-xs"
                    onClick={() => onStartSession(item.id, 'TIMED_MOCK')}
                  >
                    Timed Mock
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
