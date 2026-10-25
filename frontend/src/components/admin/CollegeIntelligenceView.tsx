import React, { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Input } from '../common/Input';
import {
  fetchCollegeIntelligenceOverview,
  exportCollegeIntelligenceCsv,
  fetchAdminUsers,
  updateUserStatus,
  createStaffUser,
  fetchAdminDepartments,
  createDepartment,
  fetchAdminCohorts,
  createCohort,
  fetchAuditLogs,
  exportAuditLogsCsv,
  fetchContentBankSummary,
  type CollegeIntelligenceOverview,
  type DepartmentItem,
  type CohortItem,
  type AuditLogItem,
  type ContentBankSummary,
} from '../../services/admin';
import { type UserSummary } from '../../services/auth';
import {
  TrendingUp,
  ShieldCheck,
  ShieldAlert,
  Award,
  Clock,
  Filter,
  Download,
  Plus,
  RefreshCw,
  Search,
  GraduationCap,
} from 'lucide-react';

export interface CollegeIntelligenceViewProps {
  currentUser: UserSummary | null;
}

export const CollegeIntelligenceView: React.FC<CollegeIntelligenceViewProps> = ({ currentUser }) => {
  const [activeTab, setActiveTab] = useState<'dossier' | 'users' | 'structure' | 'content' | 'audit'>('dossier');

  // Dossier State
  const [overview, setOverview] = useState<CollegeIntelligenceOverview | null>(null);
  const [loadingOverview, setLoadingOverview] = useState<boolean>(true);
  const [overviewError, setOverviewError] = useState<string | null>(null);
  const [selectedDeptId, setSelectedDeptId] = useState<string>('');
  const [selectedCohortId, setSelectedCohortId] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  // Dropdown options
  const [departments, setDepartments] = useState<DepartmentItem[]>([]);
  const [cohorts, setCohorts] = useState<CohortItem[]>([]);

  // User Accounts State
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [userRoleFilter, setUserRoleFilter] = useState<string>('ALL');
  const [userSearch, setUserSearch] = useState<string>('');
  const [loadingUsers, setLoadingUsers] = useState<boolean>(false);
  const [isNewStaffModalOpen, setIsNewStaffModalOpen] = useState<boolean>(false);

  // New staff form state
  const [newStaffEmail, setNewStaffEmail] = useState<string>('');
  const [newStaffName, setNewStaffName] = useState<string>('');
  const [newStaffPassword, setNewStaffPassword] = useState<string>('');
  const [newStaffRole, setNewStaffRole] = useState<string>('TRAINER');
  const [staffFormSubmitting, setStaffFormSubmitting] = useState<boolean>(false);

  // Academic Structure State
  const [isNewDeptModalOpen, setIsNewDeptModalOpen] = useState<boolean>(false);
  const [newDeptName, setNewDeptName] = useState<string>('');
  const [newDeptCode, setNewDeptCode] = useState<string>('');
  const [isNewCohortModalOpen, setIsNewCohortModalOpen] = useState<boolean>(false);
  const [newCohortDeptId, setNewCohortDeptId] = useState<string>('');
  const [newCohortYear, setNewCohortYear] = useState<number>(new Date().getFullYear());
  const [newCohortSection, setNewCohortSection] = useState<string>('A');

  // Audit Logs State
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [loadingAudit, setLoadingAudit] = useState<boolean>(false);

  // Content Bank State
  const [contentSummary, setContentSummary] = useState<ContentBankSummary | null>(null);
  const [loadingContent, setLoadingContent] = useState<boolean>(false);

  const isAdmin = currentUser?.role === 'ADMIN' || currentUser?.role === 'SUPER_ADMIN';

  useEffect(() => {
    loadAcademicFilters();
  }, []);

  useEffect(() => {
    if (activeTab === 'dossier') {
      loadOverview();
    } else if (activeTab === 'users') {
      loadUsers();
    } else if (activeTab === 'audit') {
      loadAuditLogs();
    } else if (activeTab === 'content') {
      loadContentSummary();
    }
  }, [activeTab, selectedDeptId, selectedCohortId]);

  const loadAcademicFilters = async () => {
    try {
      const [depts, cohs] = await Promise.all([
        fetchAdminDepartments().catch(() => []),
        fetchAdminCohorts().catch(() => []),
      ]);
      setDepartments(depts);
      setCohorts(cohs);
      if (depts.length > 0 && !newCohortDeptId) {
        setNewCohortDeptId(depts[0].id);
      }
    } catch (e) {
      console.error('Failed to load academic options:', e);
    }
  };

  const loadOverview = async () => {
    try {
      setLoadingOverview(true);
      setOverviewError(null);
      const data = await fetchCollegeIntelligenceOverview({
        department_id: selectedDeptId || undefined,
        cohort_id: selectedCohortId || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      });
      setOverview(data);
    } catch (err: any) {
      setOverviewError(err.message || 'Failed to load intelligence dossier');
    } finally {
      setLoadingOverview(false);
    }
  };

  const loadUsers = async () => {
    try {
      setLoadingUsers(true);
      const data = await fetchAdminUsers({
        role: userRoleFilter === 'ALL' ? undefined : userRoleFilter,
        search: userSearch || undefined,
        limit: 100,
      });
      setUsers(data);
    } catch (err: any) {
      console.error('Failed to load users:', err);
    } finally {
      setLoadingUsers(false);
    }
  };

  const loadAuditLogs = async () => {
    try {
      setLoadingAudit(true);
      const logs = await fetchAuditLogs({ limit: 100 });
      setAuditLogs(logs);
    } catch (err: any) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoadingAudit(false);
    }
  };

  const loadContentSummary = async () => {
    try {
      setLoadingContent(true);
      const data = await fetchContentBankSummary();
      setContentSummary(data);
    } catch (err: any) {
      console.error('Failed to load content summary:', err);
    } finally {
      setLoadingContent(false);
    }
  };

  const handleToggleUserStatus = async (user: UserSummary) => {
    if (user.id === currentUser?.id) {
      alert('You cannot deactivate your own administrative account.');
      return;
    }
    const newStatus = !user.is_active;
    const actionWord = newStatus ? 'activate' : 'deactivate';
    if (!window.confirm(`Are you sure you want to ${actionWord} the account for ${user.full_name}?`)) {
      return;
    }
    try {
      await updateUserStatus(user.id, newStatus);
      await loadUsers();
    } catch (err: any) {
      alert(`Status update failed: ${err.message}`);
    }
  };

  const handleCreateStaff = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setStaffFormSubmitting(true);
      await createStaffUser({
        email: newStaffEmail,
        password: newStaffPassword,
        full_name: newStaffName,
        role: newStaffRole,
      });
      setIsNewStaffModalOpen(false);
      setNewStaffEmail('');
      setNewStaffName('');
      setNewStaffPassword('');
      await loadUsers();
    } catch (err: any) {
      alert(`Staff provisioning failed: ${err.message}`);
    } finally {
      setStaffFormSubmitting(false);
    }
  };

  const handleCreateDepartment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createDepartment({ name: newDeptName, code: newDeptCode });
      setIsNewDeptModalOpen(false);
      setNewDeptName('');
      setNewDeptCode('');
      await loadAcademicFilters();
    } catch (err: any) {
      alert(`Department creation failed: ${err.message}`);
    }
  };

  const handleCreateCohort = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createCohort({
        department_id: newCohortDeptId,
        graduation_year: newCohortYear,
        section: newCohortSection || null,
      });
      setIsNewCohortModalOpen(false);
      await loadAcademicFilters();
    } catch (err: any) {
      alert(`Cohort creation failed: ${err.message}`);
    }
  };

  const handleExportIntelligenceCsv = async () => {
    try {
      const csvData = await exportCollegeIntelligenceCsv({
        department_id: selectedDeptId || undefined,
        cohort_id: selectedCohortId || undefined,
      });
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `college_intelligence_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err: any) {
      alert(`Export failed: ${err.message}`);
    }
  };

  const handleExportAuditLogsCsv = async () => {
    try {
      const csvData = await exportAuditLogsCsv();
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `security_audit_trail_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err: any) {
      alert(`Audit export failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in pb-16">
      {/* Executive Console Banner */}
      <div className="bg-[#292444] text-white rounded-3xl p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2 mb-3">
              <Badge variant="coral" className="text-xs uppercase tracking-wider font-bold">
                Phase 9 · Institutional Intelligence
              </Badge>
              <Badge variant="neutral" className="text-xs text-white/80 border-white/20">
                Accreditation & Administrative Suite
              </Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight font-display text-white">
              College Intelligence & Administration Console
            </h1>
            <p className="text-sm text-white/70 mt-2 leading-relaxed">
              Institutional intelligence synthesizing preparation volume, diagnostic skill accuracy, training program
              impact, and verified placement conversion with strict small-cell privacy ($N &lt; 5$) enforcement.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportIntelligenceCsv}
              leftIcon={<Download className="w-4 h-4" />}
              className="text-white border-white/20 hover:bg-white/10"
            >
              Export Intelligence CSV
            </Button>
            {isAdmin && (
              <Button
                variant="primary"
                size="sm"
                onClick={() => setIsNewStaffModalOpen(true)}
                leftIcon={<Plus className="w-4 h-4" />}
              >
                Provision Staff
              </Button>
            )}
          </div>
        </div>

        {/* Console Sub-Navigation Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 mt-8 pt-6 border-t border-white/10">
          <button
            onClick={() => setActiveTab('dossier')}
            className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
              activeTab === 'dossier'
                ? 'bg-white text-[#292444] shadow-xs'
                : 'bg-white/10 text-white/80 hover:bg-white/20'
            }`}
          >
            Executive Dossier (4 Pillars)
          </button>
          {isAdmin && (
            <button
              onClick={() => setActiveTab('users')}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                activeTab === 'users'
                  ? 'bg-white text-[#292444] shadow-xs'
                  : 'bg-white/10 text-white/80 hover:bg-white/20'
              }`}
            >
              User Accounts
            </button>
          )}
          {isAdmin && (
            <button
              onClick={() => setActiveTab('structure')}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                activeTab === 'structure'
                  ? 'bg-white text-[#292444] shadow-xs'
                  : 'bg-white/10 text-white/80 hover:bg-white/20'
              }`}
            >
              Academic Structure
            </button>
          )}
          <button
            onClick={() => setActiveTab('content')}
            className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
              activeTab === 'content'
                ? 'bg-white text-[#292444] shadow-xs'
                : 'bg-white/10 text-white/80 hover:bg-white/20'
            }`}
          >
            Content Bank
          </button>
          {isAdmin && (
            <button
              onClick={() => setActiveTab('audit')}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                activeTab === 'audit'
                  ? 'bg-white text-[#292444] shadow-xs'
                  : 'bg-white/10 text-white/80 hover:bg-white/20'
              }`}
            >
              Security Audit Trail
            </button>
          )}
        </div>
      </div>

      {/* TAB 1: EXECUTIVE DOSSIER */}
      {activeTab === 'dossier' && (
        <div className="space-y-6">
          {/* Filter Bar */}
          <div className="bg-white p-4 rounded-2xl border border-[#E8E0D2] shadow-xs flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-1.5 text-xs font-bold text-[#5E5875]">
                <Filter className="w-4 h-4 text-[#FF5B3D]" />
                <span>Filters:</span>
              </div>

              {/* Department Selector */}
              <select
                value={selectedDeptId}
                onChange={(e) => {
                  setSelectedDeptId(e.target.value);
                  setSelectedCohortId('');
                }}
                className="text-xs font-medium bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl px-3 py-1.5 text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
              >
                <option value="">All Departments</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} ({d.code})
                  </option>
                ))}
              </select>

              {/* Cohort Selector */}
              <select
                value={selectedCohortId}
                onChange={(e) => setSelectedCohortId(e.target.value)}
                className="text-xs font-medium bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl px-3 py-1.5 text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
              >
                <option value="">All Cohorts</option>
                {cohorts
                  .filter((c) => !selectedDeptId || c.department_id === selectedDeptId)
                  .map((c) => (
                    <option key={c.id} value={c.id}>
                      Class of {c.graduation_year} {c.section ? `Section ${c.section}` : ''}
                    </option>
                  ))}
              </select>

              {/* Date Filters */}
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="text-xs font-medium bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl px-2.5 py-1.5 text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
                title="Start Date"
              />
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="text-xs font-medium bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl px-2.5 py-1.5 text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
                title="End Date"
              />
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={loadOverview}
              leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
            >
              Refresh Intelligence
            </Button>
          </div>

          {loadingOverview ? (
            <div className="p-12 text-center text-[#5E5875]">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-[#FF5B3D]" />
              <p className="text-sm">Synthesizing institutional metrics from PostgreSQL...</p>
            </div>
          ) : overviewError ? (
            <Card className="p-6 border-red-200 bg-red-50 text-red-700 text-xs">
              <p className="font-bold mb-1">Failed to synthesize metrics</p>
              <p>{overviewError}</p>
            </Card>
          ) : overview ? (
            <div className="space-y-6">
              {/* Privacy Suppression Banner if N < 5 */}
              {overview.is_suppressed ? (
                <Card className="p-6 bg-amber-50 border-amber-200 text-amber-900 rounded-3xl">
                  <div className="flex items-start gap-3">
                    <ShieldAlert className="w-6 h-6 text-amber-600 shrink-0 mt-0.5" />
                    <div>
                      <h3 className="text-base font-bold font-display">
                        Small-Cell Privacy Suppression Enforced
                      </h3>
                      <p className="text-xs text-amber-800 mt-1 leading-relaxed">
                        {overview.suppression_reason}
                      </p>
                      <div className="mt-3 text-[11px] font-semibold text-amber-900 bg-amber-100/80 px-3 py-1.5 rounded-xl inline-block">
                        Active Sample Size: <strong>N = {overview.cohort_sample_size} students</strong> (Threshold: N &ge; 5)
                      </div>
                    </div>
                  </div>
                </Card>
              ) : (
                <>
                  {/* 4-Pillar Executive Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                    {/* Pillar 1 Card */}
                    <Card className="p-5 bg-white border-[#E8E0D2] shadow-xs flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-[#FF5B3D]">
                            Pillar 1 · Preparation
                          </span>
                          <Clock className="w-4 h-4 text-[#5E5875]" />
                        </div>
                        <h4 className="text-xs font-semibold text-[#5E5875]">Total Preparation Hours</h4>
                        <div className="text-3xl font-extrabold font-display text-[#292444] mt-1">
                          {overview.engagement?.total_preparation_hours || 0}h
                        </div>
                        <div className="mt-3 pt-3 border-t border-[#E8E0D2]/60 text-xs space-y-1 text-[#5E5875]">
                          <div className="flex justify-between">
                            <span>Active Students:</span>
                            <strong className="text-[#292444]">{overview.engagement?.active_students_count || 0}</strong>
                          </div>
                          <div className="flex justify-between">
                            <span>Total Enrolled:</span>
                            <strong className="text-[#292444]">{overview.engagement?.total_enrolled_students || 0}</strong>
                          </div>
                        </div>
                      </div>
                      <div className="mt-3 text-[11px] text-emerald-600 font-semibold bg-emerald-50 px-2 py-1 rounded-md text-center">
                        Goal Completion: {overview.engagement?.goal_completion_rate !== null ? `${overview.engagement?.goal_completion_rate}%` : 'N/A'}
                      </div>
                    </Card>

                    {/* Pillar 2 Card */}
                    <Card className="p-5 bg-white border-[#E8E0D2] shadow-xs flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-[#FF5B3D]">
                            Pillar 2 · Assessments
                          </span>
                          <TrendingUp className="w-4 h-4 text-[#5E5875]" />
                        </div>
                        <h4 className="text-xs font-semibold text-[#5E5875]">Overall Accuracy Rate</h4>
                        <div className="text-3xl font-extrabold font-display text-[#292444] mt-1">
                          {overview.assessments?.overall_accuracy_percentage !== null
                            ? `${overview.assessments?.overall_accuracy_percentage}%`
                            : 'N/A'}
                        </div>
                        <div className="mt-3 pt-3 border-t border-[#E8E0D2]/60 text-xs space-y-1 text-[#5E5875]">
                          <div className="flex justify-between">
                            <span>Evaluations Logged:</span>
                            <strong className="text-[#292444]">{overview.assessments?.total_evaluations || 0}</strong>
                          </div>
                          <div className="flex justify-between">
                            <span>Academic Domains:</span>
                            <strong className="text-[#292444]">{overview.assessments?.domain_breakdown.length || 0}</strong>
                          </div>
                        </div>
                      </div>
                      <div className="mt-3 text-[11px] text-[#292444] font-semibold bg-[#FAF6ED] px-2 py-1 rounded-md text-center border border-[#E8E0D2]">
                        Standardized & Time-Stamped
                      </div>
                    </Card>

                    {/* Pillar 3 Card */}
                    <Card className="p-5 bg-white border-[#E8E0D2] shadow-xs flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-[#FF5B3D]">
                            Pillar 3 · Training
                          </span>
                          <GraduationCap className="w-4 h-4 text-[#5E5875]" />
                        </div>
                        <h4 className="text-xs font-semibold text-[#5E5875]">Training Attendance Rate</h4>
                        <div className="text-3xl font-extrabold font-display text-[#292444] mt-1">
                          {overview.training?.overall_attendance_rate !== null
                            ? `${overview.training?.overall_attendance_rate}%`
                            : 'N/A'}
                        </div>
                        <div className="mt-3 pt-3 border-t border-[#E8E0D2]/60 text-xs space-y-1 text-[#5E5875]">
                          <div className="flex justify-between">
                            <span>Programs Running:</span>
                            <strong className="text-[#292444]">{overview.training?.total_programs_count || 0}</strong>
                          </div>
                          <div className="flex justify-between">
                            <span>Sessions Delivered:</span>
                            <strong className="text-[#292444]">{overview.training?.total_sessions_delivered || 0}</strong>
                          </div>
                        </div>
                      </div>
                      <div className="mt-3 text-[11px] text-blue-700 font-semibold bg-blue-50 px-2 py-1 rounded-md text-center">
                        Verified Trainer Roll Call
                      </div>
                    </Card>

                    {/* Pillar 4 Card */}
                    <Card className="p-5 bg-white border-[#E8E0D2] shadow-xs flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-[#FF5B3D]">
                            Pillar 4 · Placement
                          </span>
                          <Award className="w-4 h-4 text-[#5E5875]" />
                        </div>
                        <h4 className="text-xs font-semibold text-[#5E5875]">Verified Placement Rate</h4>
                        <div className="text-3xl font-extrabold font-display text-[#292444] mt-1 text-emerald-600">
                          {overview.placement?.verified_placement_rate !== null
                            ? `${overview.placement?.verified_placement_rate}%`
                            : '0%'}
                        </div>
                        <div className="mt-3 pt-3 border-t border-[#E8E0D2]/60 text-xs space-y-1 text-[#5E5875]">
                          <div className="flex justify-between">
                            <span>Verified Offers:</span>
                            <strong className="text-[#292444]">{overview.placement?.verified_offers_count || 0}</strong>
                          </div>
                          <div className="flex justify-between">
                            <span>Mean Verified CTC:</span>
                            <strong className="text-[#292444]">
                              {overview.placement?.mean_verified_ctc_lpa !== null
                                ? `₹${overview.placement?.mean_verified_ctc_lpa} LPA`
                                : 'N/A'}
                            </strong>
                          </div>
                        </div>
                      </div>
                      <div className="mt-3 text-[11px] text-amber-700 font-semibold bg-amber-50 px-2 py-1 rounded-md text-center">
                        Pending Verification: {overview.placement?.pending_review_count || 0}
                      </div>
                    </Card>
                  </div>

                  {/* Detailed Drilldowns: Domain Accuracy & Tier Breakdown */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Domain Accuracy Breakdown */}
                    <Card className="p-6">
                      <h4 className="text-sm font-bold uppercase tracking-wider text-[#292444] font-display mb-3 flex items-center justify-between">
                        <span>Assessment Accuracy by Domain</span>
                        <Badge variant="neutral" className="text-[10px]">Pillar 2</Badge>
                      </h4>

                      {overview.assessments?.domain_breakdown.length === 0 ? (
                        <p className="text-xs text-[#5E5875]">No assessment attempts recorded in this selection.</p>
                      ) : (
                        <div className="space-y-3">
                          {overview.assessments?.domain_breakdown.map((dom) => (
                            <div key={dom.domain} className="space-y-1">
                              <div className="flex items-center justify-between text-xs">
                                <span className="font-bold text-[#292444]">{dom.domain_name}</span>
                                <span className="font-semibold text-[#5E5875]">
                                  {dom.accuracy_percentage !== null ? `${dom.accuracy_percentage}%` : 'N/A'} ({dom.correct_attempts}/{dom.total_attempts})
                                </span>
                              </div>
                              <div className="w-full bg-[#FAF6ED] h-2 rounded-full overflow-hidden border border-[#E8E0D2]">
                                <div
                                  className={`h-full rounded-full transition-all ${
                                    dom.accuracy_percentage && dom.accuracy_percentage >= 70
                                      ? 'bg-emerald-500'
                                      : dom.accuracy_percentage && dom.accuracy_percentage >= 50
                                      ? 'bg-amber-500'
                                      : 'bg-[#FF5B3D]'
                                  }`}
                                  style={{ width: `${dom.accuracy_percentage || 0}%` }}
                                />
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </Card>

                    {/* Verified Placement Tier Distribution */}
                    <Card className="p-6">
                      <h4 className="text-sm font-bold uppercase tracking-wider text-[#292444] font-display mb-3 flex items-center justify-between">
                        <span>Verified Offers by Industry Tier</span>
                        <Badge variant="neutral" className="text-[10px]">Pillar 4</Badge>
                      </h4>

                      {overview.placement?.tier_distribution.length === 0 ? (
                        <p className="text-xs text-[#5E5875]">No verified offers recorded in this selection.</p>
                      ) : (
                        <div className="space-y-3">
                          {overview.placement?.tier_distribution.map((td) => (
                            <div
                              key={td.tier}
                              className="p-3 bg-[#FAF6ED] rounded-xl border border-[#E8E0D2] flex items-center justify-between text-xs"
                            >
                              <div>
                                <span className="font-bold text-[#292444] block">{td.tier_label}</span>
                                <span className="text-[10px] text-[#5E5875] block mt-0.5">
                                  {td.mean_ctc !== null ? `Avg CTC: ₹${td.mean_ctc} LPA` : 'Undisclosed'}
                                </span>
                              </div>
                              <Badge variant="coral" className="font-extrabold text-xs">
                                {td.count} {td.count === 1 ? 'Offer' : 'Offers'}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      )}
                    </Card>
                  </div>
                </>
              )}

              {/* Observational Non-Causal Policy Notice */}
              <div className="bg-[#FAF6ED] border border-[#E8E0D2] rounded-2xl p-5 text-xs text-[#5E5875] flex items-start gap-3">
                <ShieldCheck className="w-5 h-5 text-[#292444] shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-[#292444] block mb-0.5">
                    Observational Attribution Policy & Methodological Guardrails (Rule 8 Compliance)
                  </span>
                  {overview.non_causal_notice}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      )}

      {/* TAB 2: USER ACCOUNTS (ADMIN ONLY) */}
      {activeTab === 'users' && isAdmin && (
        <Card className="p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E8E0D2]">
            <div>
              <h3 className="text-base font-bold text-[#292444] font-display">Institutional User Accounts</h3>
              <p className="text-xs text-[#5E5875]">Manage user accounts, roles, and authorization states.</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-[#5E5875] absolute left-3 top-2.5" />
                <Input
                  placeholder="Search user..."
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  className="pl-8 text-xs py-1.5 w-48"
                />
              </div>
              <select
                value={userRoleFilter}
                onChange={(e) => setUserRoleFilter(e.target.value)}
                className="text-xs font-medium bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl px-2.5 py-1.5 text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
              >
                <option value="ALL">All Roles</option>
                <option value="STUDENT">Student</option>
                <option value="TRAINER">Trainer</option>
                <option value="PLACEMENT_OFFICER">Placement Officer</option>
                <option value="ADMIN">Admin</option>
              </select>
              <Button variant="ghost" size="sm" onClick={loadUsers} leftIcon={<RefreshCw className="w-3.5 h-3.5" />} />
            </div>
          </div>

          {loadingUsers ? (
            <div className="p-8 text-center text-[#5E5875]">
              <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-[#FF5B3D]" />
              <p className="text-xs">Loading institutional users...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-[#E8E0D2] text-[#5E5875] uppercase text-[10px]">
                    <th className="py-2.5">User</th>
                    <th className="py-2.5">Email</th>
                    <th className="py-2.5">Role</th>
                    <th className="py-2.5">Account Status</th>
                    <th className="py-2.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E8E0D2]">
                  {users.map((u) => (
                    <tr key={u.id} className="hover:bg-[#FAF6ED]/60 transition-colors">
                      <td className="py-3 font-bold text-[#292444]">{u.full_name}</td>
                      <td className="py-3 text-[#5E5875]">{u.email}</td>
                      <td className="py-3">
                        <Badge
                          variant={
                            u.role === 'ADMIN'
                              ? 'coral'
                              : u.role === 'PLACEMENT_OFFICER'
                              ? 'success'
                              : u.role === 'TRAINER'
                              ? 'warning'
                              : 'neutral'
                          }
                          className="text-[10px]"
                        >
                          {u.role}
                        </Badge>
                      </td>
                      <td className="py-3">
                        {u.is_active ? (
                          <Badge variant="success" hasDot className="text-[10px]">Active</Badge>
                        ) : (
                          <Badge variant="error" hasDot className="text-[10px]">Deactivated</Badge>
                        )}
                      </td>
                      <td className="py-3 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleToggleUserStatus(u)}
                          className={`text-xs h-7 px-2 ${u.is_active ? 'text-red-600 hover:bg-red-50' : 'text-emerald-600 hover:bg-emerald-50'}`}
                        >
                          {u.is_active ? 'Deactivate' : 'Activate'}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {/* TAB 3: ACADEMIC STRUCTURE (ADMIN ONLY) */}
      {activeTab === 'structure' && isAdmin && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Departments */}
          <Card className="p-6">
            <div className="flex items-center justify-between pb-3 border-b border-[#E8E0D2] mb-4">
              <div>
                <h3 className="text-base font-bold text-[#292444] font-display">Academic Departments</h3>
                <p className="text-xs text-[#5E5875]">Registered degree departments.</p>
              </div>
              <Button
                variant="primary"
                size="sm"
                onClick={() => setIsNewDeptModalOpen(true)}
                leftIcon={<Plus className="w-3.5 h-3.5" />}
              >
                Add Department
              </Button>
            </div>

            <div className="space-y-2">
              {departments.map((d) => (
                <div
                  key={d.id}
                  className="p-3 bg-[#FAF6ED] rounded-xl border border-[#E8E0D2] flex items-center justify-between text-xs"
                >
                  <span className="font-bold text-[#292444]">{d.name}</span>
                  <Badge variant="neutral" className="text-[10px] font-mono">{d.code}</Badge>
                </div>
              ))}
            </div>
          </Card>

          {/* Cohorts */}
          <Card className="p-6">
            <div className="flex items-center justify-between pb-3 border-b border-[#E8E0D2] mb-4">
              <div>
                <h3 className="text-base font-bold text-[#292444] font-display">Graduation Cohorts</h3>
                <p className="text-xs text-[#5E5875]">Academic graduation classes.</p>
              </div>
              <Button
                variant="primary"
                size="sm"
                onClick={() => setIsNewCohortModalOpen(true)}
                leftIcon={<Plus className="w-3.5 h-3.5" />}
              >
                Add Cohort
              </Button>
            </div>

            <div className="space-y-2">
              {cohorts.map((c) => (
                <div
                  key={c.id}
                  className="p-3 bg-[#FAF6ED] rounded-xl border border-[#E8E0D2] flex items-center justify-between text-xs"
                >
                  <span className="font-bold text-[#292444]">
                    Class of {c.graduation_year} {c.section ? `· Section ${c.section}` : ''}
                  </span>
                  <span className="text-[10px] text-[#5E5875]">ID: {c.id.slice(0, 8)}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* TAB 4: CONTENT BANK SUMMARY */}
      {activeTab === 'content' && (
        <Card className="p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#E8E0D2]">
            <div>
              <h3 className="text-base font-bold text-[#292444] font-display">Content & Question Bank Telemetry</h3>
              <p className="text-xs text-[#5E5875]">Curated academic assessments and domain coverage.</p>
            </div>
            <Button variant="ghost" size="sm" onClick={loadContentSummary} leftIcon={<RefreshCw className="w-3.5 h-3.5" />} />
          </div>

          {loadingContent ? (
            <div className="p-8 text-center text-[#5E5875]">
              <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-[#FF5B3D]" />
              <p className="text-xs">Loading question bank telemetry...</p>
            </div>
          ) : contentSummary ? (
            <div className="space-y-5">
              <div className="grid grid-cols-3 gap-4 bg-[#FAF6ED] p-4 rounded-2xl border border-[#E8E0D2]">
                <div>
                  <span className="text-[10px] font-bold uppercase text-[#5E5875] block">Total Questions</span>
                  <span className="text-2xl font-bold font-display text-[#292444] mt-1 block">
                    {contentSummary.total_questions}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] font-bold uppercase text-[#5E5875] block">Active Domains</span>
                  <span className="text-2xl font-bold font-display text-[#292444] mt-1 block">
                    {contentSummary.domains.length}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] font-bold uppercase text-[#5E5875] block">Published Assessments</span>
                  <span className="text-2xl font-bold font-display text-[#292444] mt-1 block">
                    {contentSummary.published_assessments}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {contentSummary.domains.map((d) => (
                  <div key={d.domain} className="p-4 bg-white rounded-xl border border-[#E8E0D2] shadow-xs">
                    <Badge variant="coral" className="text-[10px] mb-2">{d.domain}</Badge>
                    <div className="text-sm font-bold text-[#292444] mt-1">
                      {d.question_count} Questions
                    </div>
                    <div className="text-xs text-[#5E5875] mt-1">
                      {d.total_attempts} Student Attempts
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </Card>
      )}

      {/* TAB 5: AUDIT TRAIL (ADMIN ONLY) */}
      {activeTab === 'audit' && isAdmin && (
        <Card className="p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#E8E0D2]">
            <div>
              <h3 className="text-base font-bold text-[#292444] font-display">Security & Governance Audit Trail</h3>
              <p className="text-xs text-[#5E5875]">Immutable log of administrative and security events.</p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportAuditLogsCsv}
                leftIcon={<Download className="w-3.5 h-3.5" />}
              >
                Export Audit CSV
              </Button>
              <Button variant="ghost" size="sm" onClick={loadAuditLogs} leftIcon={<RefreshCw className="w-3.5 h-3.5" />} />
            </div>
          </div>

          {loadingAudit ? (
            <div className="p-8 text-center text-[#5E5875]">
              <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-[#FF5B3D]" />
              <p className="text-xs">Loading audit trail...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-[#E8E0D2] text-[#5E5875] uppercase text-[10px]">
                    <th className="py-2.5">Timestamp (UTC)</th>
                    <th className="py-2.5">Action</th>
                    <th className="py-2.5">Entity</th>
                    <th className="py-2.5">Actor User</th>
                    <th className="py-2.5">IP Address</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E8E0D2]">
                  {auditLogs.map((l) => (
                    <tr key={l.id} className="hover:bg-[#FAF6ED]/60 transition-colors">
                      <td className="py-2.5 text-[#5E5875] font-mono text-[11px]">
                        {new Date(l.created_at).toLocaleString()}
                      </td>
                      <td className="py-2.5 font-bold text-[#292444]">{l.action}</td>
                      <td className="py-2.5 text-[#5E5875]">{l.entity_type}:{l.entity_id || 'N/A'}</td>
                      <td className="py-2.5 text-[#5E5875] font-mono text-[10px]">
                        {l.actor_user_id ? l.actor_user_id.slice(0, 8) : 'SYSTEM'}
                      </td>
                      <td className="py-2.5 text-[#5E5875] font-mono text-[10px]">{l.ip_address || '127.0.0.1'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {/* Modal: Provision Staff Account */}
      {isNewStaffModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-xl border border-[#E8E0D2] animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-4 border-b border-[#E8E0D2]">
              <h3 className="text-xl font-bold font-display text-[#292444]">Provision Staff User</h3>
              <button onClick={() => setIsNewStaffModalOpen(false)} className="text-[#5E5875] p-1">✕</button>
            </div>

            <form onSubmit={handleCreateStaff} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Full Name *</label>
                <Input required value={newStaffName} onChange={(e) => setNewStaffName(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Institutional Email *</label>
                <Input type="email" required value={newStaffEmail} onChange={(e) => setNewStaffEmail(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Temporary Password *</label>
                <Input type="password" required value={newStaffPassword} onChange={(e) => setNewStaffPassword(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Institutional Role *</label>
                <select
                  value={newStaffRole}
                  onChange={(e) => setNewStaffRole(e.target.value)}
                  className="w-full text-xs font-medium bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl px-3 py-2 text-[#292444]"
                >
                  <option value="TRAINER">Trainer / Faculty</option>
                  <option value="PLACEMENT_OFFICER">Placement Officer</option>
                  <option value="ADMIN">Administrator</option>
                </select>
              </div>

              <div className="pt-4 border-t border-[#E8E0D2] flex justify-end gap-3">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsNewStaffModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm" disabled={staffFormSubmitting}>
                  {staffFormSubmitting ? 'Provisioning...' : 'Provision Staff'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: New Department */}
      {isNewDeptModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-3xl max-w-sm w-full p-6 shadow-xl border border-[#E8E0D2]">
            <h3 className="text-lg font-bold font-display text-[#292444] mb-4">Add Department</h3>
            <form onSubmit={handleCreateDepartment} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Department Name *</label>
                <Input required placeholder="Computer Science" value={newDeptName} onChange={(e) => setNewDeptName(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Department Code *</label>
                <Input required placeholder="CS" value={newDeptCode} onChange={(e) => setNewDeptCode(e.target.value)} />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsNewDeptModalOpen(false)}>Cancel</Button>
                <Button type="submit" variant="primary" size="sm">Create</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: New Cohort */}
      {isNewCohortModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-3xl max-w-sm w-full p-6 shadow-xl border border-[#E8E0D2]">
            <h3 className="text-lg font-bold font-display text-[#292444] mb-4">Add Cohort</h3>
            <form onSubmit={handleCreateCohort} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Department *</label>
                <select
                  value={newCohortDeptId}
                  onChange={(e) => setNewCohortDeptId(e.target.value)}
                  className="w-full text-xs bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl px-3 py-2 text-[#292444]"
                >
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>{d.name} ({d.code})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Graduation Year *</label>
                <Input
                  type="number"
                  required
                  value={newCohortYear.toString()}
                  onChange={(e) => setNewCohortYear(parseInt(e.target.value) || 2026)}
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Section</label>
                <Input placeholder="A" value={newCohortSection} onChange={(e) => setNewCohortSection(e.target.value)} />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsNewCohortModalOpen(false)}>Cancel</Button>
                <Button type="submit" variant="primary" size="sm">Create Cohort</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
