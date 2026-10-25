import React, { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Input } from '../common/Input';
import {
  fetchTrainingPrograms,
  fetchProgramSessions,
  createTrainingProgram,
  createTrainingSession,
  fetchSessionAttendance,
  recordSessionAttendance,
  fetchProgramEffectiveness,
  type TrainingProgramItem,
  type TrainingSessionItem,
  type AttendanceRecordItem,
  type TrainingEffectivenessReport,
} from '../../services/training';
import { type UserSummary } from '../../services/auth';
import {
  GraduationCap,
  Calendar,
  Clock,
  AlertCircle,
  Plus,
  RefreshCw,
  TrendingUp,
  ShieldAlert,
  UserCheck,
} from 'lucide-react';

export interface TrainingEffectivenessViewProps {
  currentUser: UserSummary | null;
}

export const TrainingEffectivenessView: React.FC<TrainingEffectivenessViewProps> = ({ currentUser }) => {
  const [programs, setPrograms] = useState<TrainingProgramItem[]>([]);
  const [selectedProgram, setSelectedProgram] = useState<TrainingProgramItem | null>(null);
  const [sessions, setSessions] = useState<TrainingSessionItem[]>([]);
  const [selectedSession, setSelectedSession] = useState<TrainingSessionItem | null>(null);
  const [attendance, setAttendance] = useState<AttendanceRecordItem[]>([]);
  const [effectiveness, setEffectiveness] = useState<TrainingEffectivenessReport | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [effectivenessLoading, setEffectivenessLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [domainFilter, setDomainFilter] = useState<string>('ALL');

  // Modal states
  const [isNewProgramModalOpen, setIsNewProgramModalOpen] = useState<boolean>(false);
  const [isNewSessionModalOpen, setIsNewSessionModalOpen] = useState<boolean>(false);

  // New program form state
  const [progTitle, setProgTitle] = useState<string>('');
  const [progDesc, setProgDesc] = useState<string>('');
  const [progDomain, setProgDomain] = useState<string>('QUANT');
  const [progStartDate, setProgStartDate] = useState<string>('');
  const [progEndDate, setProgEndDate] = useState<string>('');
  const [progHours, setProgHours] = useState<number>(20);
  const [programFormSubmitting, setProgramFormSubmitting] = useState<boolean>(false);

  // New session form state
  const [sessDate, setSessDate] = useState<string>('');
  const [sessStartTime, setSessStartTime] = useState<string>('10:00');
  const [sessDuration, setSessDuration] = useState<number>(60);
  const [sessTopic, setSessTopic] = useState<string>('');
  const [sessNotes, setSessNotes] = useState<string>('');
  const [sessionFormSubmitting, setSessionFormSubmitting] = useState<boolean>(false);

  const isTrainerOrStaff =
    currentUser?.role === 'TRAINER' ||
    currentUser?.role === 'PLACEMENT_OFFICER' ||
    currentUser?.role === 'ADMIN' ||
    currentUser?.role === 'SUPER_ADMIN';

  useEffect(() => {
    loadPrograms();
  }, [domainFilter]);

  useEffect(() => {
    if (selectedProgram) {
      loadProgramSessionsAndEffectiveness(selectedProgram.id);
    }
  }, [selectedProgram]);

  useEffect(() => {
    if (selectedSession) {
      loadSessionAttendance(selectedSession.id);
    } else {
      setAttendance([]);
    }
  }, [selectedSession]);

  const loadPrograms = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchTrainingPrograms(domainFilter === 'ALL' ? undefined : domainFilter);
      setPrograms(data);
      if (data.length > 0 && (!selectedProgram || !data.some((p) => p.id === selectedProgram.id))) {
        setSelectedProgram(data[0]);
      } else if (data.length === 0) {
        setSelectedProgram(null);
        setSessions([]);
        setEffectiveness(null);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load training programs');
    } finally {
      setLoading(false);
    }
  };

  const loadProgramSessionsAndEffectiveness = async (programId: string) => {
    try {
      setEffectivenessLoading(true);
      const [sessList, effReport] = await Promise.all([
        fetchProgramSessions(programId),
        fetchProgramEffectiveness(programId).catch(() => null),
      ]);
      setSessions(sessList);
      if (sessList.length > 0) {
        setSelectedSession(sessList[0]);
      } else {
        setSelectedSession(null);
      }
      setEffectiveness(effReport);
    } catch (err: any) {
      console.error('Failed to load session/effectiveness details:', err);
    } finally {
      setEffectivenessLoading(false);
    }
  };

  const loadSessionAttendance = async (sessionId: string) => {
    try {
      const records = await fetchSessionAttendance(sessionId);
      setAttendance(records);
    } catch (err: any) {
      console.error('Failed to load session attendance:', err);
    }
  };

  const handleCreateProgram = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setProgramFormSubmitting(true);
      const created = await createTrainingProgram({
        title: progTitle,
        description: progDesc || null,
        domain: progDomain,
        start_date: progStartDate,
        end_date: progEndDate,
        total_planned_hours: progHours,
      });
      setIsNewProgramModalOpen(false);
      resetProgramForm();
      await loadPrograms();
      setSelectedProgram(created);
    } catch (err: any) {
      alert(`Failed to create program: ${err.message}`);
    } finally {
      setProgramFormSubmitting(false);
    }
  };

  const resetProgramForm = () => {
    setProgTitle('');
    setProgDesc('');
    setProgDomain('QUANT');
    setProgStartDate('');
    setProgEndDate('');
    setProgHours(20);
  };

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProgram) return;
    try {
      setSessionFormSubmitting(true);
      await createTrainingSession({
        program_id: selectedProgram.id,
        session_date: sessDate,
        start_time: sessStartTime || null,
        duration_minutes: sessDuration,
        topic_covered: sessTopic,
        trainer_notes: sessNotes || null,
      });
      setIsNewSessionModalOpen(false);
      resetSessionForm();
      await loadProgramSessionsAndEffectiveness(selectedProgram.id);
    } catch (err: any) {
      alert(`Failed to create session: ${err.message}`);
    } finally {
      setSessionFormSubmitting(false);
    }
  };

  const resetSessionForm = () => {
    setSessDate('');
    setSessStartTime('10:00');
    setSessDuration(60);
    setSessTopic('');
    setSessNotes('');
  };

  const handleUpdateAttendanceStatus = async (userId: string, newStatus: 'PRESENT' | 'ABSENT' | 'EXCUSED') => {
    if (!selectedSession) return;
    try {
      const updatedList = attendance.map((a) =>
        a.user_id === userId ? { user_id: a.user_id, attendance_status: newStatus } : { user_id: a.user_id, attendance_status: a.attendance_status }
      );
      await recordSessionAttendance(selectedSession.id, updatedList);
      await loadSessionAttendance(selectedSession.id);
    } catch (err: any) {
      alert(`Attendance update failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in pb-12">
      {/* Header Banner */}
      <div className="bg-[#292444] text-white rounded-3xl p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2 mb-3">
              <Badge variant="coral" className="text-xs uppercase tracking-wider font-bold">
                Phase 8 · Training Effectiveness
              </Badge>
              <Badge variant="neutral" className="text-xs text-white/80 border-white/20">
                Paired Diagnostic Analytics
              </Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight font-display text-white">
              Institutional Training Effectiveness
            </h1>
            <p className="text-sm text-white/70 mt-2 leading-relaxed">
              Track approved institutional training programmes, verified session attendance, and empirical
              pre/post diagnostic assessment comparisons with explicit non-causal guardrails.
            </p>
          </div>

          {isTrainerOrStaff && (
            <div className="flex flex-wrap items-center gap-3">
              <Button
                variant="primary"
                size="sm"
                onClick={() => setIsNewProgramModalOpen(true)}
                leftIcon={<Plus className="w-4 h-4" />}
              >
                New Training Program
              </Button>
            </div>
          )}
        </div>

        {/* Domain Filter Toolbar */}
        <div className="flex flex-wrap items-center gap-2 mt-6 pt-6 border-t border-white/10">
          <span className="text-xs font-semibold text-white/60 mr-2">Domain:</span>
          {['ALL', 'QUANT', 'LOGICAL', 'VERBAL', 'TECHNICAL'].map((dom) => (
            <button
              key={dom}
              onClick={() => setDomainFilter(dom)}
              className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
                domainFilter === dom
                  ? 'bg-white text-[#292444] shadow-xs'
                  : 'bg-white/10 text-white/80 hover:bg-white/20'
              }`}
            >
              {dom}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid: Programs Selector & Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Programs List */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-wider text-[#292444] font-display">
              Training Programmes ({programs.length})
            </h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={loadPrograms}
              title="Refresh Programs"
              leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
            />
          </div>

          {loading ? (
            <div className="p-8 text-center text-[#5E5875]">
              <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-[#FF5B3D]" />
              <p className="text-xs">Loading training programmes...</p>
            </div>
          ) : error ? (
            <Card className="p-4 bg-red-50 border-red-200 text-red-700 text-xs">
              <p>{error}</p>
            </Card>
          ) : programs.length === 0 ? (
            <Card className="p-6 text-center border-dashed border-[#E8E0D2]">
              <p className="text-xs text-[#5E5875]">No training programmes found for domain: {domainFilter}.</p>
            </Card>
          ) : (
            <div className="space-y-3">
              {programs.map((prog) => {
                const isSelected = selectedProgram?.id === prog.id;
                return (
                  <div
                    key={prog.id}
                    onClick={() => setSelectedProgram(prog)}
                    className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-white border-[#292444] shadow-md ring-1 ring-[#292444]'
                        : 'bg-white border-[#E8E0D2] hover:border-[#292444]/40 shadow-xs'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <Badge variant="neutral" className="text-[10px] font-bold">
                        {prog.domain}
                      </Badge>
                      <span className="text-[11px] text-[#5E5875] font-semibold">
                        {prog.session_count} {prog.session_count === 1 ? 'Session' : 'Sessions'}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-[#292444] font-display mt-2">
                      {prog.title}
                    </h3>
                    {prog.description && (
                      <p className="text-xs text-[#5E5875] mt-1 line-clamp-2">{prog.description}</p>
                    )}

                    <div className="mt-3 pt-3 border-t border-[#E8E0D2]/60 flex items-center justify-between text-xs text-[#5E5875]">
                      <span className="flex items-center gap-1 font-medium">
                        <Calendar className="w-3.5 h-3.5" />
                        {prog.start_date} to {prog.end_date}
                      </span>
                      <span className="font-semibold text-[#292444]">{prog.total_planned_hours}h</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right 2 Columns: Selected Program Detail & Pre/Post Diagnostics */}
        <div className="lg:col-span-2 space-y-6">
          {selectedProgram ? (
            <>
              {/* Pre / Post Diagnostic Evaluation Card */}
              <Card className="p-6 bg-[#FAF6ED] border-[#E8E0D2] shadow-xs">
                <div className="flex items-center justify-between gap-3 mb-4">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-[#FF5B3D]" />
                    <h3 className="text-base font-bold text-[#292444] font-display">
                      Paired Diagnostic Effectiveness Report
                    </h3>
                  </div>
                  <Badge variant="coral" className="text-[10px] font-bold">
                    Comparable Diagnostics
                  </Badge>
                </div>

                {effectivenessLoading ? (
                  <div className="p-6 text-center text-[#5E5875]">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-[#FF5B3D]" />
                    <p className="text-xs">Evaluating matched pre/post assessment windows...</p>
                  </div>
                ) : effectiveness ? (
                  <div className="space-y-5">
                    {/* Metrics Row */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-white p-4 rounded-2xl border border-[#E8E0D2]">
                      <div>
                        <span className="text-[10px] font-bold uppercase text-[#5E5875] block">
                          Baseline Pre-Score
                        </span>
                        <span className="text-xl font-extrabold text-[#292444] font-display mt-1 block">
                          {effectiveness.mean_pre_score !== null ? `${effectiveness.mean_pre_score.toFixed(1)}%` : 'N/A'}
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] font-bold uppercase text-[#5E5875] block">
                          Post-Training Score
                        </span>
                        <span className="text-xl font-extrabold text-[#292444] font-display mt-1 block">
                          {effectiveness.mean_post_score !== null ? `${effectiveness.mean_post_score.toFixed(1)}%` : 'N/A'}
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] font-bold uppercase text-[#5E5875] block">
                          Mean Score Delta (Δ)
                        </span>
                        <span
                          className={`text-xl font-extrabold font-display mt-1 block ${
                            effectiveness.mean_score_delta !== null && effectiveness.mean_score_delta >= 0
                              ? 'text-emerald-600'
                              : 'text-red-600'
                          }`}
                        >
                          {effectiveness.mean_score_delta !== null
                            ? `${effectiveness.mean_score_delta > 0 ? '+' : ''}${effectiveness.mean_score_delta.toFixed(1)}%`
                            : 'N/A'}
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] font-bold uppercase text-[#5E5875] block">
                          Matched Cohort (N)
                        </span>
                        <span className="text-xl font-extrabold text-[#292444] font-display mt-1 block">
                          {effectiveness.matched_pairs_count} pairs
                        </span>
                      </div>
                    </div>

                    {/* Window Documentation & Sample Sizes */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                      <div className="bg-white p-3.5 rounded-xl border border-[#E8E0D2]">
                        <span className="font-bold text-[#292444] block mb-1">Pre-Training Window</span>
                        <p className="text-[#5E5875]">
                          {effectiveness.pre_window_start} to {effectiveness.pre_window_end} (30-day baseline)
                        </p>
                      </div>
                      <div className="bg-white p-3.5 rounded-xl border border-[#E8E0D2]">
                        <span className="font-bold text-[#292444] block mb-1">Post-Training Window</span>
                        <p className="text-[#5E5875]">
                          {effectiveness.post_window_start} to {effectiveness.post_window_end} (30-day follow-up)
                        </p>
                      </div>
                    </div>

                    {/* Attrition & Missing Data Reporting (Task 8) */}
                    <div className="bg-white p-3.5 rounded-xl border border-[#E8E0D2] text-xs">
                      <div className="flex items-center justify-between text-[#292444] font-semibold mb-1">
                        <span>Cohort Sample Size Breakdown:</span>
                        <span>
                          Enrolled: <strong className="text-[#292444]">{effectiveness.total_enrolled_count}</strong> | Matched:{' '}
                          <strong className="text-emerald-600">{effectiveness.matched_pairs_count}</strong> | Incomplete/Missing:{' '}
                          <strong className="text-amber-600">{effectiveness.attrition_missing_count}</strong>
                        </span>
                      </div>
                      {effectiveness.insufficient_data_reasons.length > 0 && (
                        <div className="mt-2 space-y-1">
                          {effectiveness.insufficient_data_reasons.map((r, idx) => (
                            <p key={idx} className="text-amber-700 flex items-center gap-1.5 text-[11px]">
                              <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                              <span>{r}</span>
                            </p>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Non-Causal Policy Guardrail */}
                    <div className="bg-white/80 p-3.5 rounded-xl border border-[#E8E0D2] text-[11px] text-[#5E5875] flex items-start gap-2.5">
                      <ShieldAlert className="w-4 h-4 text-[#FF5B3D] shrink-0 mt-0.5" />
                      <div>
                        <span className="font-bold text-[#292444] block mb-0.5">
                          Methodological Non-Causal Notice (Rule 8 Compliance)
                        </span>
                        {effectiveness.non_causal_disclaimer}
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-[#5E5875]">No paired effectiveness diagnostic data recorded yet.</p>
                )}
              </Card>

              {/* Sessions & Attendance Section */}
              <Card className="p-6">
                <div className="flex items-center justify-between gap-3 mb-4 pb-3 border-b border-[#E8E0D2]">
                  <div>
                    <h3 className="text-base font-bold text-[#292444] font-display">
                      Training Sessions & Attendance Ledger
                    </h3>
                    <p className="text-xs text-[#5E5875] mt-0.5">
                      Sessions and attendance records logged by authorized institutional trainers.
                    </p>
                  </div>
                  {isTrainerOrStaff && (
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => setIsNewSessionModalOpen(true)}
                      leftIcon={<Plus className="w-3.5 h-3.5" />}
                    >
                      Add Session
                    </Button>
                  )}
                </div>

                {sessions.length === 0 ? (
                  <div className="p-8 text-center border-dashed border border-[#E8E0D2] rounded-xl">
                    <Calendar className="w-8 h-8 text-[#5E5875]/40 mx-auto mb-2" />
                    <p className="text-xs text-[#5E5875]">No sessions created for this programme yet.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {/* Session Pills */}
                    <div className="flex items-center gap-2 overflow-x-auto pb-2">
                      {sessions.map((sess, idx) => (
                        <button
                          key={sess.id}
                          onClick={() => setSelectedSession(sess)}
                          className={`px-3.5 py-2 rounded-xl text-xs font-semibold shrink-0 transition-all text-left border ${
                            selectedSession?.id === sess.id
                              ? 'bg-[#292444] text-white border-[#292444] shadow-xs'
                              : 'bg-[#FAF6ED] text-[#5E5875] border-[#E8E0D2] hover:text-[#292444]'
                          }`}
                        >
                          <span className="block font-bold">Session #{idx + 1}</span>
                          <span className="text-[10px] opacity-80 block">{sess.session_date}</span>
                        </button>
                      ))}
                    </div>

                    {/* Selected Session Details & Roll Call */}
                    {selectedSession && (
                      <div className="bg-[#FAF6ED] p-4 rounded-2xl border border-[#E8E0D2] space-y-4">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                          <div>
                            <span className="text-xs font-bold text-[#FF5B3D] uppercase tracking-wider block">
                              Topic Covered
                            </span>
                            <h4 className="text-base font-bold text-[#292444] font-display">
                              {selectedSession.topic_covered}
                            </h4>
                          </div>
                          <div className="text-xs text-[#5E5875] font-medium flex items-center gap-3">
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3.5 h-3.5 text-[#292444]" />
                              {selectedSession.session_date}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5 text-[#292444]" />
                              {selectedSession.duration_minutes} mins
                            </span>
                          </div>
                        </div>

                        {selectedSession.trainer_notes && (
                          <div className="p-3 bg-white rounded-xl border border-[#E8E0D2] text-xs text-[#5E5875]">
                            <strong className="text-[#292444]">Trainer Notes:</strong> {selectedSession.trainer_notes}
                          </div>
                        )}

                        {/* Attendance Roll Call */}
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-bold text-[#292444] flex items-center gap-1.5">
                              <UserCheck className="w-4 h-4 text-[#FF5B3D]" />
                              <span>Attendance Roll Call ({attendance.length} Students Logged)</span>
                            </span>
                          </div>

                          {attendance.length === 0 ? (
                            <p className="text-xs text-[#5E5875] bg-white p-4 rounded-xl border border-[#E8E0D2] text-center">
                              No attendance recorded for this session yet.
                            </p>
                          ) : (
                            <div className="bg-white rounded-xl border border-[#E8E0D2] overflow-hidden divide-y divide-[#E8E0D2]">
                              {attendance.map((rec) => (
                                <div
                                  key={rec.id}
                                  className="p-3 flex items-center justify-between gap-3 text-xs"
                                >
                                  <div>
                                    <span className="font-bold text-[#292444] block">
                                      {rec.student_name || rec.user_id.slice(0, 8)}
                                    </span>
                                    {rec.roll_number && (
                                      <span className="text-[10px] text-[#5E5875] block">{rec.roll_number}</span>
                                    )}
                                  </div>

                                  <div className="flex items-center gap-1.5">
                                    {isTrainerOrStaff ? (
                                      (['PRESENT', 'ABSENT', 'EXCUSED'] as const).map((st) => (
                                        <button
                                          key={st}
                                          onClick={() => handleUpdateAttendanceStatus(rec.user_id, st)}
                                          className={`px-2.5 py-1 rounded-md text-[10px] font-bold transition-all ${
                                            rec.attendance_status === st
                                              ? st === 'PRESENT'
                                                ? 'bg-emerald-600 text-white'
                                                : st === 'ABSENT'
                                                ? 'bg-red-600 text-white'
                                                : 'bg-amber-600 text-white'
                                              : 'bg-[#FAF6ED] text-[#5E5875] hover:text-[#292444] border border-[#E8E0D2]'
                                          }`}
                                        >
                                          {st}
                                        </button>
                                      ))
                                    ) : (
                                      <Badge
                                        variant={
                                          rec.attendance_status === 'PRESENT'
                                            ? 'success'
                                            : rec.attendance_status === 'ABSENT'
                                            ? 'error'
                                            : 'warning'
                                        }
                                      >
                                        {rec.attendance_status}
                                      </Badge>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            </>
          ) : (
            <Card className="p-12 text-center border-dashed border-[#E8E0D2]">
              <GraduationCap className="w-12 h-12 text-[#5E5875]/40 mx-auto mb-3" />
              <h3 className="text-base font-bold text-[#292444]">Select a Training Programme</h3>
              <p className="text-xs text-[#5E5875] mt-1 max-w-sm mx-auto">
                Choose a programme from the list on the left to inspect session logs, student roll call, and
                comparable assessment diagnostic metrics.
              </p>
            </Card>
          )}
        </div>
      </div>

      {/* Modal: Create Program */}
      {isNewProgramModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-xl border border-[#E8E0D2] animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-4 border-b border-[#E8E0D2]">
              <h3 className="text-xl font-bold font-display text-[#292444]">New Training Programme</h3>
              <button
                onClick={() => {
                  setIsNewProgramModalOpen(false);
                  resetProgramForm();
                }}
                className="text-[#5E5875] hover:text-[#292444] p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateProgram} className="mt-5 space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Programme Title *</label>
                <Input
                  required
                  placeholder="e.g. Quantitative Mastery BootCamp"
                  value={progTitle}
                  onChange={(e) => setProgTitle(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Description</label>
                <textarea
                  rows={2}
                  className="w-full text-xs font-medium bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl p-3 text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
                  placeholder="Syllabus scope and institutional training objectives"
                  value={progDesc}
                  onChange={(e) => setProgDesc(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#292444] mb-1">Domain *</label>
                  <select
                    value={progDomain}
                    onChange={(e) => setProgDomain(e.target.value)}
                    className="w-full text-xs font-medium bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl px-3 py-2 text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
                  >
                    <option value="QUANT">QUANT</option>
                    <option value="LOGICAL">LOGICAL</option>
                    <option value="VERBAL">VERBAL</option>
                    <option value="TECHNICAL">TECHNICAL</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#292444] mb-1">Planned Hours *</label>
                  <Input
                    type="number"
                    min="1"
                    required
                    value={progHours.toString()}
                    onChange={(e) => setProgHours(parseInt(e.target.value) || 20)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#292444] mb-1">Start Date *</label>
                  <Input
                    type="date"
                    required
                    value={progStartDate}
                    onChange={(e) => setProgStartDate(e.target.value)}
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#292444] mb-1">End Date *</label>
                  <Input
                    type="date"
                    required
                    value={progEndDate}
                    onChange={(e) => setProgEndDate(e.target.value)}
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-[#E8E0D2] flex items-center justify-end gap-3">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setIsNewProgramModalOpen(false);
                    resetProgramForm();
                  }}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={programFormSubmitting}
                >
                  {programFormSubmitting ? 'Creating...' : 'Create Programme'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Create Session */}
      {isNewSessionModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-xl border border-[#E8E0D2] animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-4 border-b border-[#E8E0D2]">
              <h3 className="text-xl font-bold font-display text-[#292444]">Add Training Session</h3>
              <button
                onClick={() => {
                  setIsNewSessionModalOpen(false);
                  resetSessionForm();
                }}
                className="text-[#5E5875] hover:text-[#292444] p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateSession} className="mt-5 space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Topic Covered *</label>
                <Input
                  required
                  placeholder="e.g. Advanced Recurrence Relations and Factorials"
                  value={sessTopic}
                  onChange={(e) => setSessTopic(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#292444] mb-1">Session Date *</label>
                  <Input
                    type="date"
                    required
                    value={sessDate}
                    onChange={(e) => setSessDate(e.target.value)}
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#292444] mb-1">Start Time</label>
                  <Input
                    type="time"
                    value={sessStartTime}
                    onChange={(e) => setSessStartTime(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Duration (Minutes) *</label>
                <Input
                  type="number"
                  min="15"
                  step="15"
                  required
                  value={sessDuration.toString()}
                  onChange={(e) => setSessDuration(parseInt(e.target.value) || 60)}
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#292444] mb-1">Trainer Notes</label>
                <textarea
                  rows={2}
                  className="w-full text-xs font-medium bg-[#FAF6ED] border border-[#E8E0D2] rounded-xl p-3 text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
                  placeholder="Concepts emphasized, worksheets given, questions discussed"
                  value={sessNotes}
                  onChange={(e) => setSessNotes(e.target.value)}
                />
              </div>

              <div className="pt-4 border-t border-[#E8E0D2] flex items-center justify-end gap-3">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setIsNewSessionModalOpen(false);
                    resetSessionForm();
                  }}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={sessionFormSubmitting}
                >
                  {sessionFormSubmitting ? 'Adding...' : 'Add Session'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
