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
} from 'lucide-react';

interface LearningResourcesViewProps {
  onStartPractice?: () => void;
}

export const LearningResourcesView: React.FC<LearningResourcesViewProps> = ({
  onStartPractice,
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
    },
    {
      id: 'logical',
      title: 'Logical Reasoning',
      category: 'Deductive Analytics',
      topics: ['Syllogisms & Seating', 'Blood Relations & Direction', 'Critical Thinking', 'Pattern Deduction'],
      modulesCount: 18,
      icon: <Brain className="w-5 h-5 text-[#292444]" />,
      summary: 'Analytical deduction and cognitive patterns matching corporate assessment standards.',
    },
    {
      id: 'verbal',
      title: 'Verbal Ability & Reading',
      category: 'Communication',
      topics: ['Reading Comprehension', 'Sentence Correction', 'Para Jumbles', 'Vocabulary in Context'],
      modulesCount: 16,
      icon: <BookOpen className="w-5 h-5 text-[#FF5B3D]" />,
      summary: 'Executive communication, contextual reading, and verbal logic drills.',
    },
    {
      id: 'dsa',
      title: 'Programming & Data Structures',
      category: 'Technical Core',
      topics: ['Arrays & Strings', 'Linked Lists & Trees', 'Dynamic Programming', 'Graph Traversal'],
      modulesCount: 32,
      icon: <Code2 className="w-5 h-5 text-[#292444]" />,
      summary: 'Core computer science algorithms with time and space complexity evaluations.',
    },
    {
      id: 'sql',
      title: 'Database & SQL Systems',
      category: 'Data Engineering',
      topics: ['Joins & Subqueries', 'Window Functions', 'Query Optimization', 'Schema Design'],
      modulesCount: 14,
      icon: <Database className="w-5 h-5 text-[#FF5B3D]" />,
      summary: 'Relational query construction, data transformations, and indexing strategies.',
    },
    {
      id: 'hr',
      title: 'HR & STAR Behavioral Framework',
      category: 'Interview Preparation',
      topics: ['Situation Identification', 'Task Breakdown', 'Action Articulation', 'Result Quantification'],
      modulesCount: 10,
      icon: <CheckCircle2 className="w-5 h-5 text-[#15803D]" />,
      summary: 'Structured behavioral storytelling aligned with corporate culture and leadership principles.',
    },
  ];

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
                Syllabus Aligned
              </Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold font-display tracking-tight text-white mb-2">
              Learning Resources & Curriculum Overview
            </h1>
            <p className="text-white/80 text-sm leading-relaxed">
              Explore college-approved learning paths, syllabus breakdowns, and recommended practice drills.
              Each track is grounded in verified placement blueprints and institutional curriculum guidelines.
            </p>
          </div>

          {onStartPractice && (
            <Button
              variant="primary"
              size="sm"
              onClick={onStartPractice}
              leftIcon={<Sparkles className="w-4 h-4" />}
              className="text-xs shrink-0 shadow-sm"
            >
              Start Practice Session
            </Button>
          )}
        </div>
      </div>

      {/* Curriculum Tracks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tracks.map((track) => (
          <Card
            key={track.id}
            className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl flex flex-col justify-between hover:border-[#FF5B3D]/40 transition-all group"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-2xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center group-hover:scale-105 transition-transform">
                  {track.icon}
                </div>
                <Badge variant="neutral" className="text-[10px] font-semibold">
                  {track.category}
                </Badge>
              </div>

              <h3 className="text-lg font-bold text-[#292444] font-display mb-1.5 group-hover:text-[#FF5B3D] transition-colors">
                {track.title}
              </h3>
              <p className="text-xs text-[#5E5875] leading-relaxed mb-4">
                {track.summary}
              </p>

              <div className="space-y-2 pt-4 border-t border-[#E8E0D2]/60">
                <span className="text-[11px] font-bold text-[#292444] uppercase tracking-wider block">
                  Key Focus Areas:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {track.topics.map((t) => (
                    <span
                      key={t}
                      className="text-[11px] bg-[#FAF6ED] text-[#292444] px-2.5 py-1 rounded-full border border-[#E8E0D2]"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-[#E8E0D2]/60 flex items-center justify-between text-xs text-[#5E5875]">
              <span className="font-medium">{track.modulesCount} Standard Drills</span>
              {onStartPractice && (
                <button
                  onClick={onStartPractice}
                  className="text-xs font-semibold text-[#FF5B3D] flex items-center gap-1 group-hover:translate-x-0.5 transition-transform"
                >
                  Practise Track <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
