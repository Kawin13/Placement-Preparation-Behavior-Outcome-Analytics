import { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import {
  fetchStudentAnalytics,
  type StudentAnalytics,
} from '../../services/analytics';
import {
  Timer,
  AlertTriangle,
  Award,
  BookOpen,
  Sparkles,
  AlertCircle,
  HelpCircle,
  TrendingUp,
} from 'lucide-react';

export function StudentAnalyticsView() {
  const [analytics, setAnalytics] = useState<StudentAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState<number>(30);
  const [selectedDomain, setSelectedDomain] = useState<string>('ALL');

  useEffect(() => {
    loadAnalytics();
  }, [days]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchStudentAnalytics(days);
      setAnalytics(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PROFICIENT':
        return <Badge variant="success">Proficient</Badge>;
      case 'MODERATE':
        return <Badge variant="warning">Moderate</Badge>;
      case 'NEEDS_ATTENTION':
        return <Badge variant="error">Needs Attention</Badge>;
      case 'INSUFFICIENT_DATA':
      default:
        return <Badge variant="neutral">Insufficient Data</Badge>;
    }
  };

  const filteredTopics = analytics?.topic_breakdown.filter((t) => {
    if (selectedDomain === 'ALL') return true;
    return t.domain === selectedDomain;
  }) || [];

  return (
    <div className="space-y-8">
      {/* Editorial Header Banner */}
      <div className="bg-[#292444] text-white rounded-3xl p-8 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <Badge variant="warning" className="mb-3 text-xs uppercase tracking-wider font-semibold">
              Authentic Performance & Diagnostic Telemetry
            </Badge>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Behavior & Skill Analytics</h1>
            <p className="text-white/80 leading-relaxed text-sm">
              All metrics are computed deterministically from verified platform attempts and student-logged practice.
              Per college policy, skills with fewer than 5 attempts display an explicit sample size notice rather than misleading scores.
            </p>
          </div>

          {/* Time Window Filter */}
          <div className="flex bg-white/10 p-1.5 rounded-2xl border border-white/20 shrink-0">
            {[
              { label: 'Past 7 Days', value: 7 },
              { label: 'Past 30 Days', value: 30 },
              { label: 'All Time', value: 365 },
            ].map((tab) => (
              <button
                key={tab.value}
                onClick={() => setDays(tab.value)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  days === tab.value
                    ? 'bg-[#FF5B3D] text-white shadow-sm'
                    : 'text-white/70 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
          <Button variant="secondary" size="sm" onClick={loadAnalytics} className="ml-auto">
            Retry
          </Button>
        </div>
      )}

      {/* Loading state */}
      {loading ? (
        <div className="py-20 text-center text-[#292444]/60">
          <div className="inline-block w-8 h-8 border-4 border-[#FF5B3D] border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-sm font-medium">Computing verified diagnostic metrics...</p>
        </div>
      ) : !analytics ? null : (
        <>
          {/* Top Provenance Summary Cards (4 Cards) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {/* 1. Measured Platform Active Time */}
            <Card className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-[#292444]/60 uppercase tracking-wider">
                    Platform Active Time
                  </span>
                  <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                    <Timer className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-3xl font-extrabold text-[#292444] mb-1">
                  {analytics.prep_time.measured_platform_hours} <span className="text-base font-normal text-[#292444]/60">hrs</span>
                </div>
                <Badge variant="success" className="text-[10px] font-semibold">
                  Measured Telemetry
                </Badge>
              </div>
              <p className="text-[11px] text-[#292444]/60 mt-4 pt-3 border-t border-[#E8E0D2]/60">
                {analytics.prep_time.measured_sessions_count} sessions • Capped at 10m/question
              </p>
            </Card>

            {/* 2. Self-Logged Study Hours */}
            <Card className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-[#292444]/60 uppercase tracking-wider">
                    Self-Reported Study
                  </span>
                  <div className="w-8 h-8 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
                    <BookOpen className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-3xl font-extrabold text-[#292444] mb-1">
                  {analytics.prep_time.self_logged_hours} <span className="text-base font-normal text-[#292444]/60">hrs</span>
                </div>
                <Badge variant="warning" className="text-[10px] font-semibold">
                  Student-Logged
                </Badge>
              </div>
              <p className="text-[11px] text-[#292444]/60 mt-4 pt-3 border-t border-[#E8E0D2]/60">
                {analytics.prep_time.self_logged_activities_count} external study activities logged
              </p>
            </Card>

            {/* 3. Overall Practice Accuracy */}
            <Card className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-[#292444]/60 uppercase tracking-wider">
                    Overall Accuracy
                  </span>
                  <div className="w-8 h-8 rounded-xl bg-[#FAF6ED] text-[#FF5B3D] flex items-center justify-center">
                    <Award className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-3xl font-extrabold text-[#292444] mb-1">
                  {analytics.overall_accuracy_percentage !== null
                    ? `${analytics.overall_accuracy_percentage}%`
                    : 'N/A'}
                </div>
                <Badge variant="neutral" className="text-[10px] font-semibold">
                  {analytics.total_evaluated_attempts} Total Attempts
                </Badge>
              </div>
              <p className="text-[11px] text-[#292444]/60 mt-4 pt-3 border-t border-[#E8E0D2]/60">
                {analytics.total_evaluated_attempts > 0
                  ? 'Based on validated attempt submissions'
                  : 'No practice sessions submitted yet'}
              </p>
            </Card>

            {/* 4. Mistake Remediation Velocity */}
            <Card className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-[#292444]/60 uppercase tracking-wider">
                    Mistake Remediation
                  </span>
                  <div className="w-8 h-8 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                    <TrendingUp className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-3xl font-extrabold text-[#292444] mb-1">
                  {analytics.mistake_remediation_rate !== null
                    ? `${analytics.mistake_remediation_rate}%`
                    : '0.0%'}
                </div>
                <Badge variant="neutral" className="text-[10px] font-semibold">
                  {analytics.mastered_mistakes_count} / {analytics.total_mistakes_logged} Mastered
                </Badge>
              </div>
              <p className="text-[11px] text-[#292444]/60 mt-4 pt-3 border-t border-[#E8E0D2]/60">
                Tracks resolution of missed practice concepts
              </p>
            </Card>
          </div>

          {/* Diagnostic Skill-Gap Matrix (Domain Level) */}
          <Card className="p-8 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Sparkles className="w-4 h-4 text-[#FF5B3D]" />
                  <span className="text-xs font-bold text-[#292444]/60 uppercase tracking-wider">
                    Adaptive Diagnostic Telemetry
                  </span>
                </div>
                <h2 className="text-xl font-bold text-[#292444]">Multi-Domain Skill Gap Index</h2>
              </div>
              <span className="text-xs text-[#292444]/60">
                Formula: Gap Index = 100 - (Accuracy × Difficulty Factor)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {analytics.skill_gaps.map((sg) => (
                <div
                  key={sg.domain}
                  className="p-5 rounded-2xl border border-[#E8E0D2] bg-[#FAF6ED]/40 flex flex-col justify-between space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-bold text-[#292444]">{sg.domain_name}</h3>
                      <span className="text-xs text-[#292444]/60">
                        {sg.attempts_count} verified attempts logged
                      </span>
                    </div>
                    {getStatusBadge(sg.status)}
                  </div>

                  {sg.status === 'INSUFFICIENT_DATA' ? (
                    <div className="p-3 bg-white rounded-xl border border-[#E8E0D2] text-xs text-[#292444]/70 flex items-center gap-2">
                      <HelpCircle className="w-4 h-4 text-amber-500 shrink-0" />
                      <span>{sg.evidence_note}</span>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-[#292444]/70">Calculated Accuracy:</span>
                        <span className="font-bold text-[#292444]">{sg.accuracy_percentage}%</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-[#292444]/70">Diagnostic Skill Gap:</span>
                        <span className="font-bold text-[#FF5B3D]">{sg.skill_gap_index}%</span>
                      </div>
                      <div className="w-full bg-white rounded-full h-2 border border-[#E8E0D2] overflow-hidden">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${
                            sg.status === 'PROFICIENT'
                              ? 'bg-emerald-500'
                              : sg.status === 'MODERATE'
                              ? 'bg-amber-500'
                              : 'bg-red-500'
                          }`}
                          style={{ width: `${Math.min(100, Math.max(0, 100 - (sg.skill_gap_index || 0)))}%` }}
                        />
                      </div>
                      <p className="text-[11px] text-[#292444]/60 italic pt-1">{sg.evidence_note}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>

          {/* Daily Preparation Velocity Bar Breakdown */}
          <Card className="p-8 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-[#292444]">Daily Preparation Cadence</h3>
                <p className="text-xs text-[#292444]/60">
                  Active minutes per calendar day (Measured Platform Time + Self-Reported Study)
                </p>
              </div>
              <div className="flex items-center gap-4 text-xs text-[#292444]/70">
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-md bg-[#292444]" />
                  <span>Platform Measured</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-md bg-[#FF5B3D]" />
                  <span>Self-Reported</span>
                </div>
              </div>
            </div>

            {/* Daily Bar Chart Visual */}
            <div className="h-44 flex items-end gap-2 pt-6 pb-2 border-b border-[#E8E0D2]">
              {analytics.daily_trends.map((pt) => {
                const maxDayMinutes = Math.max(
                  ...analytics.daily_trends.map((p) => p.active_minutes),
                  60
                );
                const measuredHeight = (pt.measured_minutes / maxDayMinutes) * 100;
                const selfHeight = (pt.self_logged_minutes / maxDayMinutes) * 100;

                return (
                  <div key={pt.date} className="flex-1 flex flex-col items-center h-full justify-end group relative">
                    {/* Tooltip */}
                    <div className="absolute -top-10 bg-[#292444] text-white text-[10px] px-2 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10 shadow-lg">
                      {pt.date}: {pt.active_minutes}m ({pt.measured_minutes}m measured, {pt.self_logged_minutes}m self)
                    </div>

                    <div className="w-full max-w-[28px] flex flex-col justify-end h-full">
                      <div
                        className="w-full bg-[#FF5B3D] rounded-t-sm"
                        style={{ height: `${selfHeight}%` }}
                      />
                      <div
                        className="w-full bg-[#292444] rounded-t-sm"
                        style={{ height: `${measuredHeight}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-[#292444]/60 mt-2 truncate w-full text-center">
                      {pt.date.slice(5)}
                    </span>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Topic Performance Table */}
          <Card className="p-8 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-bold text-[#292444]">Topic-Level Accuracy Breakdown</h3>
                <p className="text-xs text-[#292444]/60">
                  Granular performance across attempted topics with evidence sample sizes
                </p>
              </div>

              {/* Domain Filter Pills */}
              <div className="flex flex-wrap gap-1.5">
                {['ALL', 'QUANT', 'LOGICAL', 'VERBAL'].map((dom) => (
                  <button
                    key={dom}
                    onClick={() => setSelectedDomain(dom)}
                    className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
                      selectedDomain === dom
                        ? 'bg-[#292444] text-white shadow-xs'
                        : 'bg-[#FAF6ED] text-[#292444]/70 hover:bg-[#FAF6ED]/80'
                    }`}
                  >
                    {dom}
                  </button>
                ))}
              </div>
            </div>

            {filteredTopics.length === 0 ? (
              <div className="py-10 text-center text-xs text-[#292444]/60">
                No topic attempts recorded in this category. Complete practice sessions to populate topic telemetry.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-[#E8E0D2] text-[#292444]/60 uppercase tracking-wider text-[10px]">
                      <th className="py-3 px-4 font-bold">Topic Name</th>
                      <th className="py-3 px-4 font-bold">Domain</th>
                      <th className="py-3 px-4 font-bold text-center">Attempts</th>
                      <th className="py-3 px-4 font-bold text-center">Accuracy</th>
                      <th className="py-3 px-4 font-bold">Diagnostic Status</th>
                      <th className="py-3 px-4 font-bold">Evidence Note</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E8E0D2]/60">
                    {filteredTopics.map((top, idx) => (
                      <tr key={idx} className="hover:bg-[#FAF6ED]/50 transition-colors">
                        <td className="py-3.5 px-4 font-bold text-[#292444]">{top.topic_name}</td>
                        <td className="py-3.5 px-4">
                          <Badge variant="neutral" className="text-[10px]">
                            {top.domain}
                          </Badge>
                        </td>
                        <td className="py-3.5 px-4 text-center font-semibold text-[#292444]">
                          {top.attempts_count}
                        </td>
                        <td className="py-3.5 px-4 text-center font-bold">
                          {top.accuracy_percentage !== null ? `${top.accuracy_percentage}%` : 'N/A'}
                        </td>
                        <td className="py-3.5 px-4">{getStatusBadge(top.status)}</td>
                        <td className="py-3.5 px-4 text-[#292444]/70 italic">{top.evidence_note}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>

          {/* Mandatory Data Limitation Notice */}
          <div className="p-4 bg-[#FAF6ED] rounded-2xl border border-[#E8E0D2] flex items-start gap-3 text-xs text-[#292444]/70">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <span className="font-bold text-[#292444]">Institutional Data Transparency Notice: </span>
              {analytics.data_limitation_notice}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
