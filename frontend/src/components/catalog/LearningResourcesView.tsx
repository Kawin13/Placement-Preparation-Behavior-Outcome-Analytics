import React from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import {
  BookOpen,
  Calculator,
  Brain,
  Code2,
  Database,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Target,
} from 'lucide-react';

interface LearningResourcesViewProps {
  onStartPractice?: () => void;
  onSelectTrack?: (trackId: string, topicName?: string) => void;
}

export const LearningResourcesView: React.FC<LearningResourcesViewProps> = ({
  onStartPractice,
  onSelectTrack,
}) => {
  const tracks = [
    {
      id: 'quant',
      title: 'Quantitative Aptitude',
      category: 'Mathematical Reasoning',
      topics: ['Percentages & Ratios', 'Time, Speed & Distance', 'Permutations & Probability', 'Data Interpretation'],
      modulesCount: 24,
      icon: <Calculator className="w-5 h-5 text-[#FF5B3D]" />,
      summary: 'Foundational problem-solving topics evaluated by leading tech firms and core recruiters.',
      actionLabel: 'Practise Track',
    },
    {
      id: 'logical',
      title: 'Logical Reasoning',
      category: 'Deductive Analytics',
      topics: ['Syllogisms & Seating', 'Blood Relations & Direction', 'Critical Thinking', 'Pattern Deduction'],
      modulesCount: 18,
      icon: <Brain className="w-5 h-5 text-[#292444]" />,
      summary: 'Analytical deduction and cognitive patterns matching corporate assessment standards.',
      actionLabel: 'Practise Track',
    },
    {
      id: 'verbal',
      title: 'Verbal Ability & Reading',
      category: 'Communication',
      topics: ['Reading Comprehension', 'Sentence Correction', 'Para Jumbles', 'Vocabulary in Context'],
      modulesCount: 16,
      icon: <BookOpen className="w-5 h-5 text-[#FF5B3D]" />,
      summary: 'Executive communication, contextual reading, and verbal logic drills.',
      actionLabel: 'Practise Track',
    },
    {
      id: 'dsa',
      title: 'Programming & Data Structures',
      category: 'Technical Core',
      topics: ['Arrays & Strings', 'Linked Lists & Trees', 'Dynamic Programming', 'Graph Traversal'],
      modulesCount: 36,
      icon: <Code2 className="w-5 h-5 text-[#292444]" />,
      summary: 'Core computer science algorithms with 36 GeeksforGeeks problems across 12 topics in DSA Studio.',
      actionLabel: 'Open DSA Studio (36 GFG Problems)',
      isDSA: true,
    },
    {
      id: 'sql',
      title: 'Database & SQL Systems',
      category: 'Data Engineering',
      topics: ['Joins & Subqueries', 'Window Functions', 'Query Optimization', 'Schema Design'],
      modulesCount: 14,
      icon: <Database className="w-5 h-5 text-[#FF5B3D]" />,
      summary: 'Relational query construction, data transformations, and indexing strategies.',
      actionLabel: 'Practise Track',
    },
    {
      id: 'hr',
      title: 'HR & STAR Behavioral Framework',
      category: 'Interview Preparation',
      topics: ['Situation Identification', 'Task Breakdown', 'Action Articulation', 'Result Quantification'],
      modulesCount: 10,
      icon: <CheckCircle2 className="w-5 h-5 text-[#15803D]" />,
      summary: 'Structured behavioral storytelling aligned with corporate culture and leadership principles.',
      actionLabel: 'Practise Track',
    },
  ];

  const handleTrackClick = (trackId: string, topicName?: string) => {
    if (onSelectTrack) {
      onSelectTrack(trackId, topicName);
    } else if (onStartPractice) {
      onStartPractice();
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in pb-12">
      {/* Header Banner */}
      <div className="bg-[#292444] text-white rounded-3xl p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2 mb-3">
              <Badge variant="coral" className="text-xs uppercase tracking-wider font-bold">
                Institutional Curriculum
              </Badge>
              <Badge variant="neutral" className="text-xs text-white/80 border-white/20">
                Topic-Wise Assessments
              </Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold font-display tracking-tight text-white mb-2">
              Learning Resources & Curriculum Overview
            </h1>
            <p className="text-white/80 text-sm leading-relaxed">
              Explore college-approved learning paths and topic-wise diagnostics.
              Click any focus area chip or track below to launch targeted diagnostics and practice questions for that exact topic.
            </p>
          </div>

          <div className="flex flex-wrap sm:flex-col items-start sm:items-end gap-2 shrink-0">
            {onStartPractice && (
              <Button
                variant="primary"
                size="sm"
                onClick={onStartPractice}
                leftIcon={<Sparkles className="w-4 h-4" />}
                className="text-xs shrink-0 shadow-sm"
              >
                Browse All Assessments
              </Button>
            )}
            <button
              onClick={() => handleTrackClick('dsa')}
              className="text-xs text-white/80 hover:text-white flex items-center gap-1.5 transition-colors font-medium bg-white/10 px-3 py-1.5 rounded-xl hover:bg-white/20"
            >
              <Code2 className="w-3.5 h-3.5 text-[#FF5B3D]" />
              <span>DSA Studio (36 Problems)</span>
            </button>
          </div>
        </div>
      </div>

      {/* Curriculum Tracks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tracks.map((track) => (
          <Card
            key={track.id}
            onClick={() => handleTrackClick(track.id)}
            className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl flex flex-col justify-between hover:border-[#FF5B3D]/60 hover:shadow-md transition-all group cursor-pointer"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-2xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center group-hover:scale-105 group-hover:bg-[#FF5B3D]/10 transition-all">
                  {track.icon}
                </div>
                <div className="flex items-center gap-1.5">
                  {track.isDSA && (
                    <Badge variant="coral" className="text-[10px] font-bold">
                      GFG Judge
                    </Badge>
                  )}
                  <Badge variant="neutral" className="text-[10px] font-semibold">
                    {track.category}
                  </Badge>
                </div>
              </div>

              <h3 className="text-lg font-bold text-[#292444] font-display mb-1.5 group-hover:text-[#FF5B3D] transition-colors flex items-center justify-between">
                <span>{track.title}</span>
                <ArrowRight className="w-4 h-4 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all text-[#FF5B3D]" />
              </h3>
              <p className="text-xs text-[#5E5875] leading-relaxed mb-4">
                {track.summary}
              </p>

              <div className="space-y-2.5 pt-4 border-t border-[#E8E0D2]/60">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-[#292444] uppercase tracking-wider block">
                    Key Focus Areas (Touch to Practice):
                  </span>
                  <span className="text-[10px] text-[#8E879E]">Topic-wise</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {track.topics.map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleTrackClick(track.id, t);
                      }}
                      className="text-[11px] bg-[#FAF6ED] text-[#292444] px-2.5 py-1 rounded-full border border-[#E8E0D2] hover:bg-[#FF5B3D] hover:text-white hover:border-[#FF5B3D] transition-all font-medium flex items-center gap-1 group/pill shadow-2xs"
                      title={`Launch ${t} diagnostic assessment`}
                    >
                      <span>{t}</span>
                      <Target className="w-2.5 h-2.5 opacity-40 group-hover/pill:opacity-100 transition-opacity" />
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-[#E8E0D2]/60 flex items-center justify-between text-xs text-[#5E5875]">
              <span className="font-medium text-[#292444]/80">
                {track.modulesCount} Standard Drills
              </span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  handleTrackClick(track.id);
                }}
                className="text-xs font-bold text-[#FF5B3D] flex items-center gap-1 group-hover:translate-x-0.5 transition-transform"
              >
                <span>{track.actionLabel}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
