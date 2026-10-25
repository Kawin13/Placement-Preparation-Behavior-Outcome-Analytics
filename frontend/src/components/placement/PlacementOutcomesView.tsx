import React, { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Input } from '../common/Input';
import {
  fetchPlacementOutcomes,
  submitPlacementOutcome,
  verifyPlacementOutcome,
  withdrawPlacementOutcome,
  exportPlacementOutcomesCsv,
  type PlacementOutcomeRecord,
  type PlacementTier,
  type VerificationStatus,
} from '../../services/placement';
import { type UserSummary } from '../../services/auth';
import {
  Briefcase,
  AlertCircle,
  Download,
  Plus,
  ExternalLink,
  ShieldCheck,
  Filter,
  RefreshCw,
  Building2,
  AlertTriangle,
  FileCheck,
} from 'lucide-react';

export interface PlacementOutcomesViewProps {
  currentUser: UserSummary | null;
}

export const PlacementOutcomesView: React.FC<PlacementOutcomesViewProps> = ({ currentUser }) => {
  const [outcomes, setOutcomes] = useState<PlacementOutcomeRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [tierFilter, setTierFilter] = useState<string>('ALL');

  // Modal states
  const [isSubmitModalOpen, setIsSubmitModalOpen] = useState<boolean>(false);
  const [isVerifyModalOpen, setIsVerifyModalOpen] = useState<boolean>(false);
  const [selectedOutcomeForAction, setSelectedOutcomeForAction] = useState<PlacementOutcomeRecord | null>(null);
  const [rejectionReason, setRejectionReason] = useState<string>('');

  // Submit form state
  const [formCompany, setFormCompany] = useState<string>('');
  const [formJobTitle, setFormJobTitle] = useState<string>('');
  const [formTier, setFormTier] = useState<PlacementTier>('TIER_1_PRODUCT');
  const [formCtcLpa, setFormCtcLpa] = useState<string>('');
  const [formOfferDate, setFormOfferDate] = useState<string>('');
  const [formProofUrl, setFormProofUrl] = useState<string>('');
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const isStaff = currentUser?.role === 'PLACEMENT_OFFICER' || currentUser?.role === 'ADMIN' || currentUser?.role === 'SUPER_ADMIN';

  useEffect(() => {
    loadOutcomes();
  }, [statusFilter, tierFilter]);

  const loadOutcomes = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchPlacementOutcomes({
        status_filter: statusFilter === 'ALL' ? undefined : statusFilter,
        tier_filter: tierFilter === 'ALL' ? undefined : tierFilter,
      });
      setOutcomes(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load placement outcomes');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setSubmitError(null);
      await submitPlacementOutcome({
        company_name: formCompany,
        job_title: formJobTitle,
        tier: formTier,
        ctc_lpa: formCtcLpa ? parseFloat(formCtcLpa) : null,
        offer_date: formOfferDate || null,
        proof_document_url: formProofUrl || null,
      });
      setIsSubmitModalOpen(false);
      resetForm();
      await loadOutcomes();
    } catch (err: any) {
      setSubmitError(err.message || 'Failed to submit placement offer');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormCompany('');
    setFormJobTitle('');
    setFormTier('TIER_1_PRODUCT');
    setFormCtcLpa('');
    setFormOfferDate('');
    setFormProofUrl('');
    setSubmitError(null);
  };

  const handleVerify = async (outcomeId: string, status: 'OFFICIALLY_VERIFIED' | 'REJECTED') => {
    try {
      await verifyPlacementOutcome(outcomeId, {
        verification_status: status,
        rejection_reason: status === 'REJECTED' ? rejectionReason : undefined,
      });
      setIsVerifyModalOpen(false);
      setSelectedOutcomeForAction(null);
      setRejectionReason('');
      await loadOutcomes();
    } catch (err: any) {
      alert(`Action failed: ${err.message}`);
    }
  };

  const handleWithdraw = async (outcomeId: string) => {
    if (!window.confirm('Are you sure you want to withdraw this placement offer record?')) {
      return;
    }
    try {
      await withdrawPlacementOutcome(outcomeId);
      await loadOutcomes();
    } catch (err: any) {
      alert(`Withdrawal failed: ${err.message}`);
    }
  };

  const handleExportCsv = async () => {
    try {
      const csvData = await exportPlacementOutcomesCsv();
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `institutional_placement_outcomes_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err: any) {
      alert(`Export failed: ${err.message}`);
    }
  };

  const getStatusBadge = (status: VerificationStatus) => {
    switch (status) {
      case 'OFFICIALLY_VERIFIED':
        return <Badge variant="success" hasDot>Verified</Badge>;
      case 'PENDING_REVIEW':
        return <Badge variant="warning" hasDot>Pending Review</Badge>;
      case 'REJECTED':
        return <Badge variant="error" hasDot>Verification Rejected</Badge>;
      case 'WITHDRAWN':
        return <Badge variant="neutral">Withdrawn</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const getTierLabel = (tier: PlacementTier) => {
    switch (tier) {
      case 'TIER_1_PRODUCT':
        return 'Tier 1 Product';
      case 'TIER_2_FINTECH':
        return 'Tier 2 FinTech';
      case 'TIER_3_CONSULTING_IT':
        return 'Tier 3 Consulting & IT';
      case 'STARTUP':
        return 'Venture Startup';
      default:
        return tier;
    }
  };

  // Metrics summary
  const verifiedCount = outcomes.filter((o) => o.verification_status === 'OFFICIALLY_VERIFIED').length;
  const pendingCount = outcomes.filter((o) => o.verification_status === 'PENDING_REVIEW').length;
  const verifiedCtcs = outcomes
    .filter((o) => o.verification_status === 'OFFICIALLY_VERIFIED' && o.ctc_lpa !== null)
    .map((o) => o.ctc_lpa as number);
  const avgVerifiedCtc = verifiedCtcs.length > 0 ? (verifiedCtcs.reduce((a, b) => a + b, 0) / verifiedCtcs.length).toFixed(1) : null;

  return (
    <div className="space-y-8 animate-in fade-in pb-12">
      {/* Header Banner */}
      <div className="bg-[#292444] text-white rounded-3xl p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2 mb-3">
              <Badge variant="coral" className="text-xs uppercase tracking-wider font-bold">
                Placement Outcomes
              </Badge>
              <Badge variant="neutral" className="text-xs text-white/80 border-white/20">
                Institutional Verification Ledger
              </Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight font-display text-white">
              Verified Placement Outcome Records
            </h1>
            <p className="text-sm text-white/70 mt-2 leading-relaxed">
              Every placement record preserves provenance, verification status, and offer documentation.
              Aggregated statistics only calculate verified offers, strictly avoiding causal attribution claims.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsSubmitModalOpen(true)}
              leftIcon={<Plus className="w-4 h-4" />}
            >
              Report Placement Offer
            </Button>
            {isStaff && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportCsv}
                leftIcon={<Download className="w-4 h-4" />}
                className="text-white border-white/20 hover:bg-white/10"
              >
                Export CSV Report
              </Button>
            )}
          </div>
        </div>

        {/* Quick KPI Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8 pt-6 border-t border-white/10 text-[#FAF6ED]">
          <div>
            <div className="text-xs font-semibold text-white/60 uppercase tracking-wider">Total Records</div>
            <div className="text-2xl font-bold font-display mt-1">{outcomes.length}</div>
          </div>
          <div>
            <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Verified Offers</div>
            <div className="text-2xl font-bold font-display mt-1 text-emerald-400">{verifiedCount}</div>
          </div>
          <div>
            <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Pending Review</div>
            <div className="text-2xl font-bold font-display mt-1 text-amber-400">{pendingCount}</div>
          </div>
          <div>
            <div className="text-xs font-semibold text-white/60 uppercase tracking-wider">Mean Verified CTC</div>
            <div className="text-2xl font-bold font-display mt-1">
              {avgVerifiedCtc ? `₹${avgVerifiedCtc} LPA` : 'N/A'}
            </div>
          </div>
        </div>
      </div>

      {/* Filter and Control Toolbar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-[#E8E0D2] shadow-xs">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 text-xs font-bold text-[#5E5875]">
            <Filter className="w-4 h-4 text-[#FF5B3D]" />
            <span>Filter Status:</span>
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {['ALL', 'OFFICIALLY_VERIFIED', 'PENDING_REVIEW', 'REJECTED', 'WITHDRAWN'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
                  statusFilter === st
                    ? 'bg-[#292444] text-white shadow-xs'
                    : 'bg-[#FAF6ED] text-[#5E5875] hover:text-[#292444] border border-[#E8E0D2]'
                }`}
              >
                {st === 'ALL' ? 'All' : st.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={tierFilter}
            onChange={(e) => setTierFilter(e.target.value)}
            className="text-xs font-medium bg-[#FAF6ED] border border-[#E8E0D2] rounded-lg px-3 py-1.5 text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
          >
            <option value="ALL">All Company Tiers</option>
            <option value="TIER_1_PRODUCT">Tier 1 Product</option>
            <option value="TIER_2_FINTECH">Tier 2 FinTech</option>
            <option value="TIER_3_CONSULTING_IT">Tier 3 Consulting & IT</option>
            <option value="STARTUP">Startup</option>
          </select>
          <Button
            variant="ghost"
            size="sm"
            onClick={loadOutcomes}
            title="Refresh Ledger"
            leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Outcome Cards Grid */}
      {loading ? (
        <div className="p-12 text-center text-[#5E5875]">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-[#FF5B3D]" />
          <p className="text-sm">Loading verified placement records from database...</p>
        </div>
      ) : error ? (
        <Card className="p-6 border-red-200 bg-red-50 text-red-700">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
            <p className="text-sm font-medium">{error}</p>
          </div>
        </Card>
      ) : outcomes.length === 0 ? (
        <Card className="p-12 text-center border-dashed border-2 border-[#E8E0D2]">
          <Briefcase className="w-12 h-12 text-[#5E5875]/40 mx-auto mb-3" />
          <h3 className="text-base font-bold text-[#292444]">No Placement Outcomes Found</h3>
          <p className="text-xs text-[#5E5875] mt-1 max-w-sm mx-auto">
            {statusFilter !== 'ALL' || tierFilter !== 'ALL'
              ? 'No records match the selected status or tier filters.'
              : 'No student placement offers have been recorded yet.'}
          </p>
          <Button
            variant="primary"
            size="sm"
            className="mt-4"
            onClick={() => setIsSubmitModalOpen(true)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Submit First Offer
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {outcomes.map((item) => (
            <Card
              key={item.id}
              className="p-5 flex flex-col justify-between hover:border-[#292444]/30 transition-all shadow-xs"
            >
              <div>
                {/* Status & Tier Header */}
                <div className="flex items-center justify-between gap-2 mb-3">
                  {getStatusBadge(item.verification_status)}
                  <span className="text-[11px] font-semibold text-[#5E5875] bg-[#FAF6ED] px-2.5 py-0.5 rounded-md border border-[#E8E0D2]">
                    {getTierLabel(item.tier)}
                  </span>
                </div>

                {/* Company & Role */}
                <h3 className="text-lg font-bold text-[#292444] font-display flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-[#FF5B3D] shrink-0" />
                  <span className="truncate">{item.company_name}</span>
                </h3>
                <p className="text-xs font-semibold text-[#5E5875] mt-0.5 ml-6">
                  {item.job_title}
                </p>

                {/* Student Info (If Staff or Available) */}
                {item.student_name && (
                  <div className="mt-3.5 pt-3 border-t border-[#E8E0D2]/60 flex items-center justify-between text-xs text-[#292444]">
                    <span className="font-medium text-[#5E5875]">Candidate:</span>
                    <span className="font-bold">
                      {item.student_name} {item.student_roll_number ? `(${item.student_roll_number})` : ''}
                    </span>
                  </div>
                )}

                {/* Compensation & Date */}
                <div className="mt-3 grid grid-cols-2 gap-2 text-xs bg-[#FAF6ED] p-2.5 rounded-xl border border-[#E8E0D2]/60">
                  <div>
                    <span className="text-[10px] uppercase font-bold text-[#5E5875] block">Compensation</span>
                    <span className="font-bold text-[#292444] text-sm mt-0.5 block">
                      {item.ctc_lpa !== null ? `₹${item.ctc_lpa.toFixed(2)} LPA` : 'Undisclosed'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-[#5E5875] block">Offer Date</span>
                    <span className="font-medium text-[#292444] text-xs mt-1 block">
                      {item.offer_date || 'Not recorded'}
                    </span>
                  </div>
                </div>

                {/* Proof Document URL */}
                {item.proof_document_url && (
                  <div className="mt-3 text-xs">
                    <a
                      href={item.proof_document_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 text-[#FF5B3D] hover:underline font-semibold"
                    >
                      <FileCheck className="w-3.5 h-3.5" />
                      <span>View Offer Letter Proof</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}

                {/* Rejection notice if REJECTED */}
                {item.verification_status === 'REJECTED' && item.rejection_reason && (
                  <div className="mt-3 p-2.5 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs">
                    <div className="flex items-center gap-1.5 font-bold mb-1">
                      <AlertTriangle className="w-3.5 h-3.5 text-red-500" />
                      <span>Verification Note:</span>
                    </div>
                    <p className="text-[11px] leading-relaxed">{item.rejection_reason}</p>
                  </div>
                )}
              </div>

              {/* Actions Footer */}
              <div className="mt-5 pt-3 border-t border-[#E8E0D2] flex items-center justify-between gap-2">
                <span className="text-[10px] text-[#5E5875]">
                  Logged {new Date(item.created_at).toLocaleDateString()}
                </span>

                <div className="flex items-center gap-2">
                  {/* Staff verification controls */}
                  {isStaff && item.verification_status === 'PENDING_REVIEW' && (
                    <>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleVerify(item.id, 'OFFICIALLY_VERIFIED')}
                        className="text-xs h-7 px-2.5 bg-emerald-600 hover:bg-emerald-700 border-none"
                      >
                        Verify
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedOutcomeForAction(item);
                          setIsVerifyModalOpen(true);
                        }}
                        className="text-xs h-7 px-2.5 text-red-600 border-red-200 hover:bg-red-50"
                      >
                        Reject
                      </Button>
                    </>
                  )}

                  {/* Student withdrawal or correction */}
                  {item.verification_status !== 'WITHDRAWN' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleWithdraw(item.id)}
                      className="text-xs text-[#5E5875] hover:text-red-600 h-7 px-2"
                    >
                      Withdraw
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Observational Notice Banner */}
      <div className="bg-[#FAF6ED] border border-[#E8E0D2] rounded-2xl p-5 text-xs text-[#5E5875] flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-[#292444] shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-[#292444] block mb-0.5">
            Observational Outcome Integrity Policy
          </span>
          Placement outcomes reflect verified, administrative records of formal offers. In accordance with college data
          governance, training attendance or portal readiness scores must not be interpreted as the sole or direct cause
          of employment results. Unverified records remain in review and do not alter institutional placement metrics.
        </div>
      </div>

      {/* Modal: Submit Placement Offer */}
      {isSubmitModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-xl border border-[#E8E0D2] animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-4 border-b border-[#E8E0D2]">
              <div>
                <h3 className="text-xl font-bold font-display text-[#292444]">Report Placement Offer</h3>
                <p className="text-xs text-[#5E5875] mt-0.5">
                  Offers enter <span className="font-semibold text-amber-600">Pending Review</span> until verified with proof.
                </p>
              </div>
              <button
                onClick={() => {
                  setIsSubmitModalOpen(false);
                  resetForm();
                }}
                className="text-[#5E5875] hover:text-[#292444] p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="mt-5 space-y-4">
              {submitError && (
                <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-500 shrink-0" />
                  <span>{submitError}</span>
                </div>
              )}

              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Company Name *</label>
                <Input
                  required
                  placeholder="e.g. Google India, Goldman Sachs, Infosys"
                  value={formCompany}
                  onChange={(e) => setFormCompany(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Job Title *</label>
                <Input
                  required
                  placeholder="e.g. Associate Software Engineer, Data Analyst"
                  value={formJobTitle}
                  onChange={(e) => setFormJobTitle(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#292444] mb-1">Industry Tier *</label>
                  <select
                    value={formTier}
                    onChange={(e) => setFormTier(e.target.value as PlacementTier)}
                    className="w-full text-xs font-medium bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl px-3 py-2 text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
                  >
                    <option value="TIER_1_PRODUCT">Tier 1 Product</option>
                    <option value="TIER_2_FINTECH">Tier 2 FinTech</option>
                    <option value="TIER_3_CONSULTING_IT">Tier 3 Consulting & IT</option>
                    <option value="STARTUP">Startup</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#292444] mb-1">CTC (LPA)</label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="e.g. 14.5"
                    value={formCtcLpa}
                    onChange={(e) => setFormCtcLpa(e.target.value)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#292444] mb-1">Offer Date</label>
                  <Input
                    type="date"
                    value={formOfferDate}
                    onChange={(e) => setFormOfferDate(e.target.value)}
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#292444] mb-1">Document Proof URL</label>
                  <Input
                    type="url"
                    placeholder="https://storage.../offer.pdf"
                    value={formProofUrl}
                    onChange={(e) => setFormProofUrl(e.target.value)}
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-[#E8E0D2] flex items-center justify-end gap-3">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setIsSubmitModalOpen(false);
                    resetForm();
                  }}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={submitting}
                >
                  {submitting ? 'Submitting...' : 'Submit for Verification'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Rejection Reason */}
      {isVerifyModalOpen && selectedOutcomeForAction && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-xl border border-[#E8E0D2] animate-in fade-in zoom-in-95">
            <h3 className="text-lg font-bold font-display text-[#292444]">
              Reject Offer Verification
            </h3>
            <p className="text-xs text-[#5E5875] mt-1">
              Provide an institutional rationale for rejecting verification for{' '}
              <span className="font-bold text-[#292444]">{selectedOutcomeForAction.company_name}</span>.
            </p>

            <div className="mt-4">
              <label className="block text-xs font-bold text-[#292444] mb-1">Rejection Reason</label>
              <textarea
                rows={3}
                className="w-full text-xs font-medium bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl p-3 text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
                placeholder="e.g. Candidate submitted interview call letter instead of formal signed appointment offer."
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
              />
            </div>

            <div className="mt-5 flex items-center justify-end gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setIsVerifyModalOpen(false);
                  setSelectedOutcomeForAction(null);
                  setRejectionReason('');
                }}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                className="bg-red-600 hover:bg-red-700 border-none"
                onClick={() => handleVerify(selectedOutcomeForAction.id, 'REJECTED')}
              >
                Confirm Rejection
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
