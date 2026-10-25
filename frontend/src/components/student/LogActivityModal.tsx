import { useState } from 'react';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { X, BookOpenCheck, AlertCircle } from 'lucide-react';
import { createActivity, type PreparationActivity, type PreparationActivityCreate } from '../../services/student';

interface LogActivityModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (newActivity: PreparationActivity) => void;
}

export function LogActivityModal({ isOpen, onClose, onSuccess }: LogActivityModalProps) {
  const [activityType, setActivityType] = useState('PRACTICE_SESSION');
  const [category, setCategory] = useState('QUANTITATIVE_APTITUDE');
  const [topic, setTopic] = useState('');
  const [durationMinutes, setDurationMinutes] = useState('45');
  const [completionState, setCompletionState] = useState('COMPLETED');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const dur = parseInt(durationMinutes, 10);
    if (isNaN(dur) || dur < 1 || dur > 720) {
      setError('Duration must be between 1 and 720 minutes.');
      return;
    }

    if (topic.trim().length < 2) {
      setError('Please provide a specific topic (at least 2 characters).');
      return;
    }

    setIsLoading(true);

    try {
      const payload: PreparationActivityCreate = {
        activity_type: activityType,
        category,
        topic: topic.trim(),
        duration_minutes: dur,
        completion_state: completionState,
        notes: notes.trim() ? notes.trim() : undefined,
      };

      const act = await createActivity(payload);
      onSuccess(act);
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to record activity');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#292444]/60 backdrop-blur-xs animate-in fade-in">
      <div className="bg-white rounded-3xl border border-[#E8E0D2] p-6 sm:p-8 max-w-lg w-full shadow-warm-lg">
        <div className="flex items-center justify-between pb-4 border-b border-[#E8E0D2] mb-6">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D]">
              <BookOpenCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-[#292444] font-display">Log Preparation Activity</h3>
              <p className="text-xs text-[#5E5875]">Record authentic practice, self-study, or mock drills</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-[#5E5875] hover:bg-[#FAF6ED] hover:text-[#292444] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mb-5 p-3 rounded-xl bg-[#FFF5F3] border border-[#FF5B3D]/30 flex items-start gap-2.5 text-[#FF5B3D] text-xs">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-[#5E5875]">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-[#E8E0D2] bg-white text-sm text-[#292444] focus:outline-none focus:ring-2 focus:ring-[#FF5B3D]/20 focus:border-[#FF5B3D]"
              >
                <option value="QUANTITATIVE_APTITUDE">Quantitative Aptitude</option>
                <option value="LOGICAL_REASONING">Logical Reasoning</option>
                <option value="VERBAL_ABILITY">Verbal Ability</option>
                <option value="PROGRAMMING">Programming & DSA</option>
                <option value="SQL">SQL & Databases</option>
                <option value="CORE_TECHNICAL">Core Technical Concepts</option>
                <option value="HR_BEHAVIORAL">HR & Behavioral STAR</option>
                <option value="GENERAL">General Placement Prep</option>
              </select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-[#5E5875]">Activity Type</label>
              <select
                value={activityType}
                onChange={(e) => setActivityType(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-[#E8E0D2] bg-white text-sm text-[#292444] focus:outline-none focus:ring-2 focus:ring-[#FF5B3D]/20 focus:border-[#FF5B3D]"
              >
                <option value="PRACTICE_SESSION">Practice Drill</option>
                <option value="MOCK_TEST">Timed Mock Assessment</option>
                <option value="CONCEPT_REVISION">Concept Revision</option>
                <option value="MISTAKE_REVIEW">Mistake Review</option>
                <option value="SELF_STUDY">Self-Directed Study</option>
              </select>
            </div>
          </div>

          <Input
            label="Topic / Subject Matter"
            type="text"
            required
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. Time & Work, Dynamic Programming, Syllogisms"
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Duration (Minutes)"
              type="number"
              min="1"
              max="720"
              required
              value={durationMinutes}
              onChange={(e) => setDurationMinutes(e.target.value)}
              placeholder="45"
            />

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-[#5E5875]">Completion State</label>
              <select
                value={completionState}
                onChange={(e) => setCompletionState(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-[#E8E0D2] bg-white text-sm text-[#292444] focus:outline-none focus:ring-2 focus:ring-[#FF5B3D]/20 focus:border-[#FF5B3D]"
              >
                <option value="COMPLETED">Completed</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="ABANDONED">Partially Done / Paused</option>
              </select>
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-[#5E5875]">Study Notes / Reflection</label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Mastered LCM shortcut for 3-pipe work rate questions. Identified formula gap in geometric progressions."
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#E8E0D2] bg-white text-sm text-[#292444] focus:outline-none focus:ring-2 focus:ring-[#FF5B3D]/20 focus:border-[#FF5B3D] resize-none"
            />
          </div>

          <div className="pt-4 flex justify-end gap-3 border-t border-[#E8E0D2]">
            <Button variant="outline" size="sm" type="button" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" isLoading={isLoading}>
              Record Activity
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
