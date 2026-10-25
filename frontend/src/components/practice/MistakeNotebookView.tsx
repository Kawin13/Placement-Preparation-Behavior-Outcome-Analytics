import { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import {
  fetchStudentMistakes,
  updateMistakeEntry,
  type MistakeEntry,
} from '../../services/practice';
import {
  CheckCircle,
  AlertCircle,
  FileEdit,
  Save,
  Check,
  Sparkles,
} from 'lucide-react';

export interface MistakeNotebookViewProps {
  onAskCoach?: (questionContext: {
    questionId: string;
    questionTitle: string;
    studentNotes?: string | null;
    errorTag?: string | null;
  }) => void;
}

export function MistakeNotebookView({ onAskCoach }: MistakeNotebookViewProps = {}) {
  const [mistakes, setMistakes] = useState<MistakeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>('ALL');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editNotes, setEditNotes] = useState<string>('');
  const [savingId, setSavingId] = useState<string | null>(null);

  useEffect(() => {
    loadMistakes();
  }, [selectedFilter]);

  const loadMistakes = async () => {
    try {
      setLoading(true);
      setError(null);
      const filter = selectedFilter === 'ALL' ? undefined : selectedFilter;
      const data = await fetchStudentMistakes(filter);
      setMistakes(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load mistake notebook');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (
    mistakeId: string,
    newStatus: 'UNRESOLVED' | 'REVIEWED' | 'MASTERED'
  ) => {
    try {
      await updateMistakeEntry(mistakeId, { mastery_status: newStatus });
      setMistakes((prev) =>
        prev.map((m) =>
          m.id === mistakeId
            ? {
                ...m,
                mastery_status: newStatus,
                resolved_at: newStatus === 'MASTERED' ? new Date().toISOString() : m.resolved_at,
              }
            : m
        )
      );
    } catch (err: any) {
      alert(err.message || 'Failed to update status');
    }
  };

  const handleSaveNotes = async (mistakeId: string) => {
    try {
      setSavingId(mistakeId);
      const mistake = mistakes.find((m) => m.id === mistakeId);
      await updateMistakeEntry(mistakeId, {
        mastery_status: mistake?.mastery_status || 'UNRESOLVED',
        student_notes: editNotes,
      });
      setMistakes((prev) =>
        prev.map((m) => (m.id === mistakeId ? { ...m, student_notes: editNotes } : m))
      );
      setEditingId(null);
    } catch (err: any) {
      alert(err.message || 'Failed to save notes');
    } finally {
      setSavingId(null);
    }
  };

  const startEditNotes = (m: MistakeEntry) => {
    setEditingId(m.id);
    setEditNotes(m.student_notes || '');
  };

  const unresolvedCount = mistakes.filter((m) => m.mastery_status === 'UNRESOLVED').length;
  const masteredCount = mistakes.filter((m) => m.mastery_status === 'MASTERED').length;

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-[#292444] text-white rounded-3xl p-8 shadow-sm">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="max-w-2xl">
            <Badge variant="warning" className="mb-3 text-xs uppercase tracking-wider font-semibold">
              Formative Error Analysis
            </Badge>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Mistake Notebook</h1>
            <p className="text-white/80 leading-relaxed text-sm">
              Every question missed during practice is automatically logged here. Review recurring misconceptions, record personal insights, and mark concepts as Mastered when verified.
            </p>
          </div>
          <div className="flex gap-3 shrink-0">
            <div className="bg-white/10 px-4 py-2.5 rounded-2xl border border-white/20 text-center">
              <span className="text-xl font-bold text-[#FF5B3D] block">{unresolvedCount}</span>
              <span className="text-[11px] text-white/70 font-semibold uppercase">Unresolved</span>
            </div>
            <div className="bg-white/10 px-4 py-2.5 rounded-2xl border border-white/20 text-center">
              <span className="text-xl font-bold text-emerald-400 block">{masteredCount}</span>
              <span className="text-[11px] text-white/70 font-semibold uppercase">Mastered</span>
            </div>
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap gap-2 mt-6 pt-6 border-t border-white/10">
          {[
            { id: 'ALL', label: 'All Entries' },
            { id: 'UNRESOLVED', label: 'Unresolved' },
            { id: 'REVIEWED', label: 'Under Review' },
            { id: 'MASTERED', label: 'Mastered' },
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

      {/* Error State */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
          <Button variant="secondary" size="sm" onClick={loadMistakes} className="ml-auto">
            Retry
          </Button>
        </div>
      )}

      {/* Loading */}
      {loading ? (
        <div className="py-20 text-center text-[#292444]/60">
          <div className="inline-block w-8 h-8 border-4 border-[#FF5B3D] border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-sm font-medium">Loading mistake notebook...</p>
        </div>
      ) : mistakes.length === 0 ? (
        <Card className="p-12 text-center bg-white border border-[#E8E0D2]">
          <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-[#292444] mb-1">
            {selectedFilter === 'ALL' ? 'Your Mistake Notebook is empty' : 'No entries matching filter'}
          </h3>
          <p className="text-xs text-[#292444]/60 max-w-md mx-auto">
            {selectedFilter === 'ALL'
              ? 'Great work! Take a practice assessment to discover areas for conceptual reinforcement.'
              : 'Try selecting a different filter above.'}
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {mistakes.map((m) => {
            const isEditing = editingId === m.id;
            const statusVariant =
              m.mastery_status === 'MASTERED'
                ? 'success'
                : m.mastery_status === 'REVIEWED'
                ? 'warning'
                : 'error';

            return (
              <Card
                key={m.id}
                className="p-6 bg-white border border-[#E8E0D2] shadow-sm rounded-3xl space-y-4"
              >
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#E8E0D2]/60">
                  <div className="flex items-center gap-3">
                    <Badge variant={statusVariant} className="text-[11px] font-bold">
                      {m.mastery_status}
                    </Badge>
                    {m.skill_domain && (
                      <Badge variant="neutral" className="text-[11px]">
                        {m.skill_domain}
                      </Badge>
                    )}
                    <span className="text-xs text-[#292444]/60">
                      Logged {new Date(m.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {onAskCoach && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          onAskCoach({
                            questionId: m.question_id,
                            questionTitle: m.question_title,
                            studentNotes: m.student_notes,
                            errorTag: m.error_tag,
                          })
                        }
                        className="text-xs text-[#292444] hover:border-[#FF5B3D]/50"
                        leftIcon={<Sparkles className="w-3.5 h-3.5 text-[#FF5B3D]" />}
                      >
                        Ask AI Coach
                      </Button>
                    )}
                    {m.mastery_status !== 'MASTERED' ? (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleUpdateStatus(m.id, 'MASTERED')}
                        className="text-xs text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border-emerald-200"
                      >
                        <Check className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                        Mark Mastered
                      </Button>
                    ) : (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleUpdateStatus(m.id, 'UNRESOLVED')}
                        className="text-xs text-[#292444]/60"
                      >
                        Reopen
                      </Button>
                    )}
                  </div>
                </div>

                {/* Question Info */}
                <div>
                  <h3 className="text-sm font-bold text-[#292444] mb-2">{m.question_title}</h3>
                  <p className="text-xs text-[#292444]/80 leading-relaxed whitespace-pre-wrap bg-[#FAF6ED] p-4 rounded-2xl border border-[#E8E0D2]">
                    {m.question_content}
                  </p>
                </div>

                {/* Personal Notes Box */}
                <div className="pt-2">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-[#292444]/60 uppercase tracking-wider flex items-center gap-1.5">
                      <FileEdit className="w-3.5 h-3.5" />
                      My Correction Notes
                    </span>
                    {!isEditing && (
                      <button
                        onClick={() => startEditNotes(m)}
                        className="text-xs text-[#FF5B3D] hover:underline font-medium"
                      >
                        {m.student_notes ? 'Edit Notes' : 'Add Note'}
                      </button>
                    )}
                  </div>

                  {isEditing ? (
                    <div className="space-y-2">
                      <textarea
                        value={editNotes}
                        onChange={(e) => setEditNotes(e.target.value)}
                        placeholder="Explain why you missed this question and what concept or formula to remember next time..."
                        className="w-full text-xs p-3 rounded-2xl border border-[#FF5B3D] focus:ring-1 focus:ring-[#FF5B3D] outline-none min-h-[80px]"
                      />
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => setEditingId(null)}
                          className="text-xs"
                        >
                          Cancel
                        </Button>
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => handleSaveNotes(m.id)}
                          disabled={savingId === m.id}
                          className="text-xs"
                        >
                          <Save className="w-3 h-3 mr-1" />
                          {savingId === m.id ? 'Saving...' : 'Save Note'}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-[#292444]/70 italic bg-white p-3 rounded-2xl border border-[#E8E0D2]">
                      {m.student_notes || 'No correction notes added yet.'}
                    </p>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
