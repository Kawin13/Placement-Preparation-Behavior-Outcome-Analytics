import { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import {
  fetchCohortAnalytics,
  downloadCohortReport,
  type CohortAnalytics,
} from '../../services/analytics';
import {
  Users,
  Timer,
  Award,
  AlertTriangle,
  Sparkles,
  AlertCircle,
  HelpCircle,
  Download,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';

export function CohortAnalyticsView() {
  const [analytics, setAnalytics] = useState<CohortAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState<number>(30);
  const [downloading, setDownloading] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  useEffect(() => {
    loadAnalytics();
  }, [days]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchCohortAnalytics(undefined, undefined, days);
      setAnalytics(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load cohort analytics');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!analytics?.cohort_id) return;
    try {
      setDownloading(true);
      await downloadCohortReport(analytics.cohort_id);
      setDownloadSuccess(true);
      setTimeout(() => setDownloadSuccess(false), 3000);
    } catch (err: any) {
      alert(err.message || 'Failed to export cohort report');
    } finally {
      setDownloading(false);
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'HIGH_FRICTION':
        return <Badge variant="error">High Friction (&lt;40%)</Badge>;
      case 'MODERATE_FRICTION':
        return <Badge variant="warning">Moderate Friction (40-60%)</Badge>;
      case 'STABLE':
      default:
        return <Badge variant="success">Stable (&gt;60%)</Badge>;
    }
  };

  return (
    <div className="space-y-8">
      {/* Editorial Header Banner */}
      <div className="bg-[#292444] text-white rounded-3xl p-8 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2 mb-3">
              <Badge variant="warning" className="text-xs uppercase tracking-wider font-semibold">
                Institutional Department Telemetry
              </Badge>
              <Badge variant="neutral" className="text-xs font-semibold bg-white/10 text-white border-white/20">
                Staff &amp; Admin RBAC
              </Badge>
            </div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Cohort Preparation &amp; Performance Telemetry</h1>
            <p className="text-white/80 leading-relaxed text-sm">
              Aggregated from authentic preparation sessions and verified student attempt records.
              Zero synthetic data or simulated numbers. Correlation between preparation and placement outcomes strictly enforces sample-size criteria.
            </p>
          </div>

          {/* Time Window Filter & Export Action */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 shrink-0">
            <div className="flex bg-white/10 p-1.5 rounded-2xl border border-white/20">
              {[
                { label: 'Past 7 Days', value: 7 },
                { label: 'Past 30 Days', value: 30 },
                { label: 'All Time', value: 365 },
              ].map((tab) => (
                <button
                  key={tab.value}
                  onClick={() => setDays(tab.value)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                    days === tab.value
                      ? 'bg-[#FF5B3D] text-white shadow-sm'
                      : 'text-white/70 hover:text-white'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <Button
              variant="primary"
              size="sm"
              onClick={handleDownloadReport}
              disabled={downloading || !analytics}
              leftIcon={<Download className="w-3.5 h-3.5" />}
              className="bg-[#FF5B3D] hover:bg-[#e04b2f] text-white"
            >
              {downloading ? 'Exporting...' : downloadSuccess ? 'Exported!' : 'Export CSV'}
            </Button>
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
          <p className="text-sm font-medium">Aggregating departmental cohort records from PostgreSQL...</p>
        </div>
      ) : !analytics ? (
        <Card className="p-12 text-center text-[#292444]/60 bg-white border border-[#E8E0D2] rounded-3xl">
          <HelpCircle className="w-8 h-8 mx-auto text-amber-500 mb-3" />
          <h3 className="text-base font-bold text-[#292444] mb-1">No Cohort Records Available</h3>
          <p className="text-xs text-[#292444]/60">Ensure students are assigned to cohorts in your department.</p>
        </Card>
      ) : (
        <>
          {/* Cohort Identity Banner */}
          <div className="bg-white border border-[#E8E0D2] rounded-3xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <span className="text-[10px] uppercase font-bold text-[#292444]/60 tracking-wider">
                Active Cohort Context
              </span>
              <h2 className="text-xl font-bold text-[#292444]">
                {analytics.department_name} — {analytics.cohort_name}
              </h2>
              <p className="text-xs text-[#292444]/60 mt-0.5">
                Graduation Year: {analytics.graduation_year} • Section: {analytics.section || 'All Sections'}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="neutral" className="text-xs">
                Data Freshness: {new Date(analytics.data_freshness_timestamp).toLocaleTimeString()}
              </Badge>
              <Badge variant="success" className="text-xs">
                Real-Time DB Sync
              </Badge>
            </div>
          </div>

          {/* Top 4 Cohort Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {/* 1. Active Participating Students */}
            <Card className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-[#292444]/60 uppercase tracking-wider">
                    Student Participation
                  </span>
                  <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                    <Users className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-3xl font-extrabold text-[#292444] mb-1">
                  {analytics.active_participating_students}{' '}
                  <span className="text-base font-normal text-[#292444]/60">
                    / {analytics.total_enrolled_students}
                  </span>
                </div>
                <Badge
                  variant={analytics.participation_rate_percentage >= 50 ? 'success' : 'warning'}
                  className="text-[10px] font-semibold"
                >
                  {analytics.participation_rate_percentage}% Active
                </Badge>
              </div>
              <p className="text-[11px] text-[#292444]/60 mt-4 pt-3 border-t border-[#E8E0D2]/60">
                Logged practice or assessment within window
              </p>
            </Card>

            {/* 2. Total Cumulative Preparation Time */}
            <Card className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-[#292444]/60 uppercase tracking-wider">
                    Cohort Active Time
                  </span>
                  <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                    <Timer className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-3xl font-extrabold text-[#292444] mb-1">
                  {analytics.total_cohort_active_hours}{' '}
                  <span className="text-base font-normal text-[#292444]/60">hrs</span>
                </div>
                <Badge variant="success" className="text-[10px] font-semibold">
                  Platform Telemetry
                </Badge>
              </div>
              <p className="text-[11px] text-[#292444]/60 mt-4 pt-3 border-t border-[#E8E0D2]/60">
                Sum of capped attempt durations (max 10m/q)
              </p>
            </Card>

            {/* 3. Cohort Average Accuracy */}
            <Card className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-[#292444]/60 uppercase tracking-wider">
                    Mean Cohort Accuracy
                  </span>
                  <div className="w-8 h-8 rounded-xl bg-[#FAF6ED] text-[#FF5B3D] flex items-center justify-center">
                    <Award className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-3xl font-extrabold text-[#292444] mb-1">
                  {analytics.cohort_average_accuracy !== null
                    ? `${analytics.cohort_average_accuracy}%`
                    : 'N/A'}
                </div>
                <Badge variant="neutral" className="text-[10px] font-semibold">
                  Evaluated Answers
                </Badge>
              </div>
              <p className="text-[11px] text-[#292444]/60 mt-4 pt-3 border-t border-[#E8E0D2]/60">
                {analytics.cohort_average_accuracy !== null
                  ? 'Aggregate accuracy across all submitted questions'
                  : 'No cohort submissions recorded in this window'}
              </p>
            </Card>

            {/* 4. Friction Points Detected */}
            <Card className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-[#292444]/60 uppercase tracking-wider">
                    Topic Friction Points
                  </span>
                  <div className="w-8 h-8 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-3xl font-extrabold text-[#292444] mb-1">
                  {analytics.topic_friction_points.length}
                </div>
                <Badge
                  variant={analytics.topic_friction_points.length === 0 ? 'success' : 'warning'}
                  className="text-[10px] font-semibold"
                >
                  {analytics.topic_friction_points.length === 0
                    ? 'All Topics Stable'
                    : 'Needs Remediation'}
                </Badge>
              </div>
              <p className="text-[11px] text-[#292444]/60 mt-4 pt-3 border-t border-[#E8E0D2]/60">
                Topics where cohort accuracy falls below 60%
              </p>
            </Card>
          </div>

          {/* Skill Gap Distribution Matrix */}
          <Card className="p-8 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Sparkles className="w-4 h-4 text-[#FF5B3D]" />
                  <span className="text-xs font-bold text-[#292444]/60 uppercase tracking-wider">
                    Departmental Diagnostic Breakdown
                  </span>
                </div>
                <h2 className="text-xl font-bold text-[#292444]">
                  Cohort Skill-Gap Standing Distribution
                </h2>
              </div>
              <span className="text-xs text-[#292444]/60">
                Student tier distribution based on individual assessment evidence
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { domain: 'QUANT', name: 'Quantitative Aptitude' },
                { domain: 'LOGICAL', name: 'Logical Reasoning' },
                { domain: 'VERBAL', name: 'Verbal Ability' },
              ].map(({ domain, name }) => {
                const dist = analytics.skill_gap_distribution[domain] || {
                  PROFICIENT: 0,
                  MODERATE: 0,
                  NEEDS_ATTENTION: 0,
                  INSUFFICIENT_DATA: 0,
                };
                const totalEvaluated =
                  dist.PROFICIENT + dist.MODERATE + dist.NEEDS_ATTENTION + dist.INSUFFICIENT_DATA;

                return (
                  <div
                    key={domain}
                    className="p-5 rounded-2xl border border-[#E8E0D2] bg-[#FAF6ED]/40 flex flex-col justify-between space-y-4"
                  >
                    <div>
                      <h3 className="text-base font-bold text-[#292444] mb-0.5">{name}</h3>
                      <span className="text-xs text-[#292444]/60">
                        {totalEvaluated} students mapped in cohort
                      </span>
                    </div>

                    <div className="space-y-2.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="flex items-center gap-1.5 text-emerald-700 font-medium">
                          <span className="w-2 h-2 rounded-full bg-emerald-500" />
                          Proficient (&ge;75%)
                        </span>
                        <span className="font-bold text-[#292444]">{dist.PROFICIENT}</span>
                      </div>

                      <div className="flex items-center justify-between text-xs">
                        <span className="flex items-center gap-1.5 text-amber-700 font-medium">
                          <span className="w-2 h-2 rounded-full bg-amber-500" />
                          Moderate (50-74%)
                        </span>
                        <span className="font-bold text-[#292444]">{dist.MODERATE}</span>
                      </div>

                      <div className="flex items-center justify-between text-xs">
                        <span className="flex items-center gap-1.5 text-red-700 font-medium">
                          <span className="w-2 h-2 rounded-full bg-red-500" />
                          Needs Attention (&lt;50%)
                        </span>
                        <span className="font-bold text-[#292444]">{dist.NEEDS_ATTENTION}</span>
                      </div>

                      <div className="flex items-center justify-between text-xs pt-1 border-t border-[#E8E0D2]">
                        <span className="flex items-center gap-1.5 text-[#292444]/60">
                          <span className="w-2 h-2 rounded-full bg-neutral-400" />
                          Insufficient Data (&lt;5 attempts)
                        </span>
                        <span className="font-bold text-[#292444]">{dist.INSUFFICIENT_DATA}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Topic Friction Points Table */}
          <Card className="p-8 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-bold text-[#292444]">Identified Topic Friction Points</h3>
                <p className="text-xs text-[#292444]/60">
                  Topics where aggregated cohort accuracy is under 60% with minimum 5 verified attempts
                </p>
              </div>
            </div>

            {analytics.topic_friction_points.length === 0 ? (
              <div className="p-6 bg-[#FAF6ED] rounded-2xl border border-[#E8E0D2] flex items-center gap-3 text-xs text-[#292444]/70">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                <span>
                  No low-accuracy friction points identified. Cohort accuracy across all qualifying topics is currently above 60%, or sample thresholds have not yet been met.
                </span>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-[#E8E0D2] text-[#292444]/60 uppercase tracking-wider text-[10px]">
                      <th className="py-3 px-4 font-bold">Topic Title</th>
                      <th className="py-3 px-4 font-bold">Domain</th>
                      <th className="py-3 px-4 font-bold text-center">Cohort Attempts</th>
                      <th className="py-3 px-4 font-bold text-center">Cohort Accuracy</th>
                      <th className="py-3 px-4 font-bold">Severity Status</th>
                      <th className="py-3 px-4 font-bold">Recommended Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E8E0D2]/60">
                    {analytics.topic_friction_points.map((fp, idx) => (
                      <tr key={idx} className="hover:bg-[#FAF6ED]/50 transition-colors">
                        <td className="py-3.5 px-4 font-bold text-[#292444]">{fp.topic_name}</td>
                        <td className="py-3.5 px-4">
                          <Badge variant="neutral" className="text-[10px]">
                            {fp.domain}
                          </Badge>
                        </td>
                        <td className="py-3.5 px-4 text-center font-semibold text-[#292444]">
                          {fp.cohort_attempts}
                        </td>
                        <td className="py-3.5 px-4 text-center font-bold text-red-600">
                          {fp.cohort_accuracy_percentage}%
                        </td>
                        <td className="py-3.5 px-4">{getSeverityBadge(fp.severity)}</td>
                        <td className="py-3.5 px-4 text-[#292444]/70">
                          Schedule remedial workshop and targeted practice assignment.
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>

          {/* Placement Correlation Diagnostic Card (Mandatory Guardrails & Disclaimer) */}
          <Card className="p-8 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl space-y-5">
            <div className="flex items-center gap-2 mb-1">
              <ShieldCheck className="w-5 h-5 text-[#292444]" />
              <h3 className="text-lg font-bold text-[#292444]">
                Preparation vs. Placement Outcome Association
              </h3>
            </div>

            <div className="p-5 rounded-2xl bg-[#FAF6ED] border border-[#E8E0D2] space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E8E0D2]">
                <div className="text-xs">
                  <span className="text-[#292444]/60 block uppercase font-bold text-[10px]">
                    Verified Placement Sample Size
                  </span>
                  <span className="text-base font-extrabold text-[#292444]">
                    n = {analytics.placement_correlation.sample_size} verified placed students
                  </span>
                </div>
                <Badge
                  variant={analytics.placement_correlation.is_statistically_valid ? 'success' : 'warning'}
                >
                  {analytics.placement_correlation.is_statistically_valid
                    ? 'Threshold Met (n ≥ 30)'
                    : 'Sample Guardrail Active (n < 30)'}
                </Badge>
              </div>

              {/* Spearman Rho or Sample Limitation Display */}
              <div className="text-xs text-[#292444]/80 leading-relaxed">
                <p className="font-medium mb-2">{analytics.placement_correlation.significance_note}</p>
                {analytics.placement_correlation.spearman_rho !== null && (
                  <div className="p-3 bg-white rounded-xl border border-[#E8E0D2] inline-flex items-center gap-3 mb-2">
                    <span className="text-[#292444]/70">Calculated Spearman Rank Correlation:</span>
                    <span className="font-mono font-bold text-sm text-[#FF5B3D]">
                      ρ = {analytics.placement_correlation.spearman_rho}
                    </span>
                  </div>
                )}
              </div>

              {/* Mandatory Non-Causal Institutional Disclaimer (Rule 8 / Phase 6 Restrictions) */}
              <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 flex items-start gap-2.5 text-[11px] text-amber-900 leading-relaxed">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <strong>Institutional Non-Causal Disclaimer: </strong>
                  {analytics.placement_correlation.non_causal_disclaimer}
                </div>
              </div>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
