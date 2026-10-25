import React, { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import {
  fetchApprovedRoles,
  evaluateRoleReadiness,
  type RoleDefinition,
  type RoleReadinessResponse,
} from '../../services/readiness';
import {
  Target,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  AlertCircle,
  Clock,
  ArrowRight,
  CheckCircle2,
  HelpCircle,
} from 'lucide-react';

export interface RoleReadinessViewProps {
  onSelectAssessment?: (assessmentId: string) => void;
  onOpenCoachModal?: (roleId: string) => void;
}

export const RoleReadinessView: React.FC<RoleReadinessViewProps> = ({
  onSelectAssessment,
  onOpenCoachModal,
}) => {
  const [roles, setRoles] = useState<RoleDefinition[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<string>('SDE');
  const [readiness, setReadiness] = useState<RoleReadinessResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showFormula, setShowFormula] = useState<boolean>(false);

  useEffect(() => {
    loadRolesAndReadiness();
  }, [selectedRoleId]);

  const loadRolesAndReadiness = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch approved roles if not already loaded
      let currentRoles = roles;
      if (roles.length === 0) {
        currentRoles = await fetchApprovedRoles();
        setRoles(currentRoles);
      }

      // Fetch readiness evaluation for selected role
      const res = await evaluateRoleReadiness(selectedRoleId);
      setReadiness(res);
    } catch (err: any) {
      setError(err.message || 'Failed to evaluate role readiness');
    } finally {
      setLoading(false);
    }
  };

  const getTierBadgeVariant = (tier: string) => {
    switch (tier) {
      case 'ROLE_READY':
        return 'success';
      case 'DEVELOPING':
        return 'warning';
      case 'FOUNDATION_NEEDED':
        return 'coral';
      default:
        return 'neutral';
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'CRITICAL_DEFICIT':
        return <Badge variant="coral" className="text-[10px] font-bold">Critical Deficit</Badge>;
      case 'HIGH_PRIORITY':
        return <Badge variant="warning" className="text-[10px] font-bold">High Priority</Badge>;
      default:
        return <Badge variant="neutral" className="text-[10px] font-bold">Reinforcement</Badge>;
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in pb-12">
      {/* Top Banner & Header */}
      <div className="bg-[#292444] text-white rounded-3xl p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2 mb-3">
              <Badge variant="coral" className="text-xs uppercase tracking-wider font-bold">
                Phase 7 · Role Intelligence
              </Badge>
              <Badge variant="neutral" className="text-xs text-white/80 border-white/20">
                Non-Predictive Governance
              </Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold font-display tracking-tight text-white mb-2">
              Role-Specific Readiness Telemetry
            </h1>
            <p className="text-white/80 text-sm leading-relaxed">
              Diagnostic multi-domain evaluation mapping your verified practice attempts against authentic industry requirements. Readiness scores require minimum evidence thresholds to ensure defensibility.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <Button
              variant="primary"
              size="sm"
              onClick={() => onOpenCoachModal?.(selectedRoleId)}
              leftIcon={<Sparkles className="w-3.5 h-3.5" />}
              className="text-xs shadow-md"
            >
              Consult AI Coach
            </Button>
          </div>
        </div>

        {/* Role Selector Tabs */}
        <div className="flex flex-wrap gap-2 mt-6 pt-6 border-t border-white/10">
          {(roles.length > 0
            ? roles
            : [
                { role_id: 'SDE', role_name: 'Software Development Engineer (SDE)' },
                { role_id: 'DATA_ANALYST', role_name: 'Data Analyst / SQL Specialist' },
                { role_id: 'CORE_TECH', role_name: 'Core Technology Graduate' },
              ]
          ).map((role) => (
            <button
              key={role.role_id}
              onClick={() => setSelectedRoleId(role.role_id)}
              className={`px-4 py-2 rounded-full text-xs font-semibold transition-all flex items-center gap-2 ${
                selectedRoleId === role.role_id
                  ? 'bg-[#FF5B3D] text-white shadow-xs'
                  : 'bg-white/10 text-white/80 hover:bg-white/20'
              }`}
            >
              <Target className="w-3.5 h-3.5" />
              {role.role_name}
            </button>
          ))}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
          <Button variant="secondary" size="sm" onClick={loadRolesAndReadiness} className="ml-auto text-xs">
            Retry
          </Button>
        </div>
      )}

      {loading ? (
        <div className="py-20 text-center text-[#292444]/60">
          <div className="inline-block w-8 h-8 border-4 border-[#FF5B3D] border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-sm font-semibold">Evaluating verified attempt evidence for {selectedRoleId}...</p>
        </div>
      ) : readiness ? (
        <>
          {/* Composite Readiness Card */}
          <Card className="p-6 sm:p-8 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-[#E8E0D2]">
              <div className="space-y-1.5">
                <div className="flex items-center gap-2.5">
                  <Badge variant="neutral" className="text-[11px] font-bold">
                    Target: {readiness.target_industry_tier.replace(/_/g, ' ')}
                  </Badge>
                  <Badge variant={getTierBadgeVariant(readiness.readiness_tier)} className="text-[11px] font-bold">
                    {readiness.readiness_tier.replace(/_/g, ' ')}
                  </Badge>
                </div>
                <h2 className="text-2xl font-bold text-[#292444] font-display">
                  {readiness.role_name}
                </h2>
                <p className="text-xs sm:text-sm text-[#5E5875] max-w-2xl leading-relaxed">
                  {readiness.role_description}
                </p>
              </div>

              {/* Composite Metric Display */}
              <div className="bg-[#FAF6ED] p-5 rounded-2xl border border-[#E8E0D2] flex items-center gap-5 shrink-0 min-w-[260px]">
                <div className="w-16 h-16 rounded-2xl bg-[#292444] text-white flex flex-col items-center justify-center shadow-inner">
                  {readiness.has_sufficient_evidence && readiness.readiness_score !== null ? (
                    <>
                      <span className="text-xl font-bold font-display text-[#FF5B3D] leading-none">
                        {readiness.readiness_score.toFixed(0)}
                      </span>
                      <span className="text-[9px] text-white/70 font-semibold uppercase mt-0.5">/ 100</span>
                    </>
                  ) : (
                    <>
                      <span className="text-base font-bold font-display text-white/50 leading-none">--</span>
                      <span className="text-[8px] text-white/60 font-semibold uppercase mt-0.5">Evidence Req</span>
                    </>
                  )}
                </div>

                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#5E5875] block">
                    Readiness Index
                  </span>
                  <div className="text-sm font-bold text-[#292444] mt-0.5">
                    {readiness.has_sufficient_evidence
                      ? `${readiness.total_role_attempts} attempts verified`
                      : 'Sample Threshold Unmet'}
                  </div>
                  <span className="text-[11px] text-[#5E5875] block mt-0.5">
                    {readiness.has_sufficient_evidence ? 'Statistically Defensible' : 'Withheld per Rule 6'}
                  </span>
                </div>
              </div>
            </div>

            {/* Insufficient Evidence Warning Banner */}
            {!readiness.has_sufficient_evidence && (
              <div className="mt-6 p-4 sm:p-5 bg-amber-50 border border-amber-200/80 rounded-2xl flex items-start gap-4">
                <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                <div className="space-y-1.5 text-xs text-amber-900">
                  <span className="font-bold uppercase tracking-wider text-amber-800 block">
                    Score Suppressed: Insufficient Evidence Threshold
                  </span>
                  <p className="leading-relaxed">
                    To prevent statistical bias and avoid speculative grading, composite readiness scores are withheld until you log at least <strong>5 evaluated attempts</strong> in each required domain.
                  </p>
                  {readiness.missing_evidence_summary.length > 0 && (
                    <ul className="list-disc list-inside space-y-1 mt-2 text-amber-950 font-medium">
                      {readiness.missing_evidence_summary.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            )}
          </Card>

          {/* Domain Evidence Breakdown Grid */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-[#292444] font-display">
                  Domain Evidence Breakdown
                </h3>
                <p className="text-xs text-[#5E5875]">
                  Minimum threshold: 5 verified attempts per domain with 90-day recency tracking.
                </p>
              </div>
              <button
                onClick={() => setShowFormula(!showFormula)}
                className="text-xs text-[#FF5B3D] hover:underline flex items-center gap-1 font-semibold"
              >
                <HelpCircle className="w-3.5 h-3.5" />
                {showFormula ? 'Hide Formula' : 'View Scoring Formula'}
              </button>
            </div>

            {showFormula && (
              <div className="p-4 bg-white rounded-2xl border border-[#E8E0D2] text-xs text-[#5E5875] space-y-2 animate-in fade-in">
                <div className="font-bold text-[#292444]">Institutional Scoring Governance:</div>
                <div className="font-mono bg-[#FAF6ED] p-3 rounded-xl border border-[#E8E0D2] text-[#292444]">
                  {readiness.formula_documentation}
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {readiness.domain_evidence.map((dom) => (
                <Card
                  key={dom.domain}
                  className="p-5 bg-white border border-[#E8E0D2] rounded-2xl flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="text-sm font-bold text-[#292444]">{dom.domain_name}</h4>
                        <span className="text-[11px] text-[#5E5875]">Weight: {(dom.weight * 100).toFixed(0)}% of Role</span>
                      </div>
                      <Badge
                        variant={
                          dom.status === 'PROFICIENT'
                            ? 'success'
                            : dom.status === 'MODERATE'
                            ? 'warning'
                            : dom.status === 'NEEDS_ATTENTION'
                            ? 'coral'
                            : 'neutral'
                        }
                        className="text-[10px] font-bold"
                      >
                        {dom.status.replace(/_/g, ' ')}
                      </Badge>
                    </div>

                    {/* Attempts vs Threshold */}
                    <div className="bg-[#FAF6ED] p-3 rounded-xl border border-[#E8E0D2] space-y-1.5 text-xs">
                      <div className="flex justify-between items-center">
                        <span className="text-[#5E5875]">Attempt Evidence:</span>
                        <span className="font-bold text-[#292444] flex items-center gap-1">
                          {dom.attempts_count} / 5 attempts
                          {dom.meets_threshold ? (
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          ) : (
                            <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                          )}
                        </span>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className="text-[#5E5875]">Raw Accuracy:</span>
                        <span className="font-bold text-[#292444]">
                          {dom.raw_accuracy_percentage !== null
                            ? `${dom.raw_accuracy_percentage.toFixed(1)}%`
                            : 'N/A (<5 attempts)'}
                        </span>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className="text-[#5E5875]">Recency Status:</span>
                        <span className="font-medium text-[#292444] flex items-center gap-1">
                          <Clock className="w-3 h-3 text-[#5E5875]" />
                          {dom.recency_label}
                        </span>
                      </div>
                    </div>
                  </div>

                  <p className="text-[11px] text-[#5E5875] leading-relaxed italic border-t border-[#E8E0D2]/60 pt-3">
                    {dom.evidence_note}
                  </p>
                </Card>
              ))}
            </div>
          </div>

          {/* Real Practice Recommendations */}
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-bold text-[#292444] font-display">
                Targeted Practice Recommendations
              </h3>
              <p className="text-xs text-[#5E5875]">
                Curated assessments from the real institutional catalogue addressing your highest-weighted deficits.
              </p>
            </div>

            {readiness.recommendations.length === 0 ? (
              <Card className="p-8 text-center bg-white border border-[#E8E0D2]">
                <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
                <h4 className="text-sm font-bold text-[#292444]">All Domain Thresholds Met</h4>
                <p className="text-xs text-[#5E5875] mt-1">
                  Keep maintaining recency across all domains to preserve your role readiness benchmark.
                </p>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {readiness.recommendations.map((rec) => (
                  <Card
                    key={rec.assessment_id}
                    className="p-5 bg-white border border-[#E8E0D2] rounded-2xl flex flex-col justify-between space-y-4 hover:border-[#FF5B3D]/50 transition-all shadow-xs"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between gap-2">
                        {getPriorityBadge(rec.priority)}
                        <span className="text-[11px] text-[#5E5875] flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {rec.duration_minutes} mins
                        </span>
                      </div>

                      <h4 className="text-sm font-bold text-[#292444]">
                        {rec.assessment_title}
                      </h4>
                      <p className="text-xs text-[#5E5875] leading-relaxed">
                        {rec.rationale}
                      </p>
                    </div>

                    <div className="pt-2 flex justify-end">
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => onSelectAssessment?.(rec.assessment_id)}
                        rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                        className="text-xs"
                      >
                        Launch Practice Drill
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Institutional Non-Predictive Disclaimer Card */}
          <Card className="p-5 sm:p-6 bg-[#FAF6ED] border border-[#E8E0D2] rounded-2xl">
            <div className="flex items-start gap-3.5">
              <ShieldCheck className="w-5 h-5 text-[#292444] shrink-0 mt-0.5" />
              <div className="space-y-1 text-xs text-[#5E5875]">
                <div className="font-bold text-[#292444] uppercase tracking-wider text-[11px]">
                  Institutional Transparency & Non-Predictive Disclaimer
                </div>
                <p className="leading-relaxed">
                  {readiness.non_predictive_disclaimer}
                </p>
              </div>
            </div>
          </Card>
        </>
      ) : null}
    </div>
  );
};
