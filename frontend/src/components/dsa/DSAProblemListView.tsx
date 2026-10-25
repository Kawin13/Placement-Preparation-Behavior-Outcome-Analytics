import React, { useState, useEffect } from 'react';
import {
  fetchDSATopics,
  fetchDSAProblems,
  fetchProblemOfTheDay,
  fetchMyDSAAnalytics,
  type DSATopicItem,
  type DSAProblemListItem,
  type DSAStudentAnalyticsResponse,
} from '../../services/dsa';

interface Props {
  onSelectProblem: (slug: string) => void;
}

export const DSAProblemListView: React.FC<Props> = ({ onSelectProblem }) => {
  const [topics, setTopics] = useState<DSATopicItem[]>([]);
  const [problems, setProblems] = useState<DSAProblemListItem[]>([]);
  const [potd, setPotd] = useState<DSAProblemListItem | null>(null);
  const [analytics, setAnalytics] = useState<DSAStudentAnalyticsResponse | null>(null);

  const [selectedTopic, setSelectedTopic] = useState<string>('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [selectedSheet, setSelectedSheet] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [selectedTopic, selectedDifficulty, selectedStatus, selectedSheet]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [topicsRes, problemsRes, potdRes, analyticsRes] = await Promise.all([
        fetchDSATopics().catch(() => []),
        fetchDSAProblems({
          topic_slug: selectedTopic || undefined,
          difficulty: selectedDifficulty || undefined,
          status: selectedStatus || undefined,
          sheet_tag: selectedSheet !== 'ALL' ? selectedSheet : undefined,
          search: searchQuery || undefined,
        }),
        fetchProblemOfTheDay().catch(() => null),
        fetchMyDSAAnalytics().catch(() => null),
      ]);

      setTopics(topicsRes);
      setProblems(problemsRes);
      setPotd(potdRes);
      setAnalytics(analyticsRes);
    } catch (err: any) {
      setError(err.message || 'Failed to load problems');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  const getDifficultyBadge = (diff: string) => {
    switch (diff) {
      case 'EASY':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'MEDIUM':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'HARD':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SOLVED':
        return (
          <span className="flex items-center justify-center w-5 h-5 rounded-full bg-emerald-100 text-emerald-600 text-xs font-bold" title="Solved">
            ✓
          </span>
        );
      case 'ATTEMPTED':
        return (
          <span className="flex items-center justify-center w-5 h-5 rounded-full bg-amber-100 text-amber-600 text-xs font-bold" title="Attempted">
            ◐
          </span>
        );
      default:
        return (
          <span className="flex items-center justify-center w-5 h-5 rounded-full bg-gray-100 text-gray-400 text-xs" title="Unsolved">
            ○
          </span>
        );
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Banner / Hero & POTD */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Hero */}
        <div className="lg:col-span-2 bg-gradient-to-br from-[#292444] to-[#1E1B2E] text-white p-6 sm:p-8 rounded-2xl shadow-sm border border-[#292444]/20 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="px-3 py-1 bg-[#FF5B3D]/20 text-[#FF5B3D] border border-[#FF5B3D]/30 text-xs font-semibold rounded-full uppercase tracking-wider">
                LeetCode-Grade Online Judge
              </span>
              <span className="text-xs text-gray-400">OpenJDK 21 & Python 3.12 Sandboxed</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mb-2">
              DSA Problem-Solving Studio
            </h1>
            <p className="text-gray-300 text-sm max-w-xl leading-relaxed">
              Master fundamental to advanced data structures and algorithms with sandboxed code execution,
              rigorous hidden test evaluation, and algorithmic behavioral telemetry.
            </p>
          </div>

          {/* Quick Sheet Selector Pills */}
          <div className="mt-6 pt-5 border-t border-white/10 flex flex-wrap items-center gap-3">
            <span className="text-xs text-gray-400 font-medium">Curated Tracks:</span>
            {['ALL', 'Core 75', 'Blind 50'].map((sheet) => (
              <button
                key={sheet}
                onClick={() => setSelectedSheet(sheet)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  selectedSheet === sheet
                    ? 'bg-[#FF5B3D] text-white shadow-sm'
                    : 'bg-white/10 text-gray-300 hover:bg-white/20'
                }`}
              >
                {sheet === 'ALL' ? 'All Problems' : sheet}
              </button>
            ))}
          </div>
        </div>

        {/* Problem of the Day Card */}
        <div className="bg-white p-6 rounded-2xl border border-[#E8E0D2] shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="flex items-center gap-1.5 text-xs font-bold text-[#FF5B3D] uppercase tracking-wider">
                <span className="w-2 h-2 rounded-full bg-[#FF5B3D] animate-ping" />
                Problem of the Day
              </span>
              {potd && (
                <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${getDifficultyBadge(potd.difficulty)}`}>
                  {potd.difficulty}
                </span>
              )}
            </div>

            {potd ? (
              <>
                <h3 className="text-lg font-bold text-[#292444] line-clamp-1 mb-1">
                  #{potd.problem_number}. {potd.title}
                </h3>
                <p className="text-xs text-gray-500 mb-3">
                  Topic: <span className="font-medium text-gray-700">{potd.topic_name || 'General'}</span>
                </p>
                <div className="flex items-center gap-3 text-xs text-gray-600 mb-4">
                  <span>Acceptance: {potd.acceptance_rate}%</span>
                  <span>•</span>
                  <span>Status: <span className="font-semibold">{potd.user_status}</span></span>
                </div>
              </>
            ) : (
              <p className="text-xs text-gray-400 py-4">No daily challenge active.</p>
            )}
          </div>

          {potd && (
            <button
              onClick={() => onSelectProblem(potd.slug)}
              className="w-full py-2.5 px-4 bg-[#292444] text-white hover:bg-[#1E1B2E] text-xs font-semibold rounded-xl transition-all shadow-sm flex items-center justify-center gap-2"
            >
              <span>Solve POTD Challenge</span>
              <span>→</span>
            </button>
          )}
        </div>
      </div>

      {/* Analytics Summary Banner */}
      {analytics && (
        <div className="bg-white p-5 rounded-2xl border border-[#E8E0D2] shadow-sm grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
          <div className="border-r border-[#E8E0D2] pr-4">
            <span className="text-[11px] text-gray-500 block uppercase font-medium">Solved Problems</span>
            <span className="text-2xl font-extrabold text-[#292444]">{analytics.total_solved}</span>
            <span className="text-xs text-gray-400 block">/ {analytics.total_problems} Total</span>
          </div>
          <div className="border-r border-[#E8E0D2] pr-4">
            <span className="text-[11px] text-emerald-600 block uppercase font-medium">Easy Solved</span>
            <span className="text-2xl font-extrabold text-emerald-600">{analytics.easy_solved}</span>
          </div>
          <div className="border-r border-[#E8E0D2] pr-4">
            <span className="text-[11px] text-amber-600 block uppercase font-medium">Medium Solved</span>
            <span className="text-2xl font-extrabold text-amber-600">{analytics.medium_solved}</span>
          </div>
          <div className="border-r border-[#E8E0D2] pr-4">
            <span className="text-[11px] text-rose-600 block uppercase font-medium">Hard Solved</span>
            <span className="text-2xl font-extrabold text-rose-600">{analytics.hard_solved}</span>
          </div>
          <div className="border-r border-[#E8E0D2] pr-4">
            <span className="text-[11px] text-gray-500 block uppercase font-medium">Acceptance Rate</span>
            <span className="text-2xl font-extrabold text-[#292444]">{analytics.acceptance_rate}%</span>
            <span className="text-xs text-gray-400 block">{analytics.total_submissions} Attempts</span>
          </div>
          <div>
            <span className="text-[11px] text-gray-500 block uppercase font-medium">Recommended Next</span>
            {analytics.recommended_problem_slug ? (
              <button
                onClick={() => onSelectProblem(analytics.recommended_problem_slug!)}
                className="text-xs text-left font-bold text-[#FF5B3D] hover:underline line-clamp-1 mt-1"
                title={analytics.recommended_reason || ''}
              >
                {analytics.recommended_problem_title} →
              </button>
            ) : (
              <span className="text-xs text-gray-400 block mt-1">All clear!</span>
            )}
          </div>
        </div>
      )}

      {/* 12 Topics Pills Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-gray-600 uppercase tracking-wider">DSA Core Topics (12)</span>
          {selectedTopic && (
            <button
              onClick={() => setSelectedTopic('')}
              className="text-xs text-[#FF5B3D] hover:underline font-medium"
            >
              Clear Topic Filter
            </button>
          )}
        </div>
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin">
          <button
            onClick={() => setSelectedTopic('')}
            className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all border ${
              selectedTopic === ''
                ? 'bg-[#292444] text-white border-[#292444]'
                : 'bg-white text-gray-700 border-[#E8E0D2] hover:bg-gray-50'
            }`}
          >
            All Topics
          </button>
          {topics.map((t) => (
            <button
              key={t.slug}
              onClick={() => setSelectedTopic(t.slug)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all border flex items-center gap-1.5 ${
                selectedTopic === t.slug
                  ? 'bg-[#292444] text-white border-[#292444]'
                  : 'bg-white text-gray-700 border-[#E8E0D2] hover:bg-gray-50'
              }`}
            >
              <span>{t.name}</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-black/10">
                {t.solved_count}/{t.problem_count}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-[#E8E0D2] shadow-sm flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative flex-1">
          <input
            type="text"
            placeholder="Search problem title or keyword (e.g. Two Sum, Binary Search, Islands)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs border border-[#E8E0D2] rounded-lg focus:outline-none focus:ring-1 focus:ring-[#FF5B3D] bg-[#FAF6ED]/30"
          />
          <span className="absolute left-3 top-2.5 text-gray-400 text-xs">🔍</span>
        </form>

        {/* Difficulty & Status Selectors */}
        <div className="flex items-center gap-2">
          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="text-xs border border-[#E8E0D2] rounded-lg px-3 py-2 bg-white text-gray-700 focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
          >
            <option value="">All Difficulties</option>
            <option value="EASY">Easy</option>
            <option value="MEDIUM">Medium</option>
            <option value="HARD">Hard</option>
          </select>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="text-xs border border-[#E8E0D2] rounded-lg px-3 py-2 bg-white text-gray-700 focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
          >
            <option value="">All Statuses</option>
            <option value="SOLVED">Solved</option>
            <option value="ATTEMPTED">Attempted</option>
            <option value="UNSOLVED">Unsolved</option>
          </select>
        </div>
      </div>

      {/* Problem Library Table */}
      <div className="bg-white rounded-2xl border border-[#E8E0D2] shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-gray-500 text-sm">
            <div className="inline-block w-6 h-6 border-2 border-[#FF5B3D] border-t-transparent rounded-full animate-spin mb-2" />
            <p>Loading problems...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-600 text-xs bg-rose-50 m-4 rounded-xl border border-rose-200">
            {error}
          </div>
        ) : problems.length === 0 ? (
          <div className="p-12 text-center text-gray-500 text-sm">
            No problems match your selected criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#FAF6ED]/70 border-b border-[#E8E0D2] text-[11px] font-bold text-gray-500 uppercase tracking-wider">
                  <th className="py-3 px-4 w-12 text-center">Status</th>
                  <th className="py-3 px-4">Title</th>
                  <th className="py-3 px-4">Topic</th>
                  <th className="py-3 px-4">Difficulty</th>
                  <th className="py-3 px-4">Acceptance</th>
                  <th className="py-3 px-4">Tracks</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E8E0D2] text-xs">
                {problems.map((p) => (
                  <tr
                    key={p.id}
                    className="hover:bg-[#FAF6ED]/40 transition-colors group cursor-pointer"
                    onClick={() => onSelectProblem(p.slug)}
                  >
                    <td className="py-3 px-4 text-center">
                      {getStatusIcon(p.user_status)}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-gray-400 text-[11px]">
                          #{p.problem_number}
                        </span>
                        <span className="font-bold text-[#292444] group-hover:text-[#FF5B3D] transition-colors">
                          {p.title}
                        </span>
                        {p.is_problem_of_the_day && (
                          <span className="px-1.5 py-0.2 rounded bg-[#FF5B3D]/10 text-[#FF5B3D] text-[10px] font-bold">
                            POTD
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-600 font-medium">
                      {p.topic_name || 'General'}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2.5 py-1 rounded-md text-[11px] font-bold border ${getDifficultyBadge(p.difficulty)}`}>
                        {p.difficulty}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-600">
                      {p.acceptance_rate}%
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-1">
                        {p.sheet_tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-0.5 rounded text-[10px] font-semibold bg-gray-100 text-gray-600 border border-gray-200"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectProblem(p.slug);
                        }}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#292444] text-white hover:bg-[#FF5B3D] transition-colors shadow-sm"
                      >
                        {p.user_status === 'SOLVED' ? 'Re-Practice' : 'Solve'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
