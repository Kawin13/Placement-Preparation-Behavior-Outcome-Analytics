import { useState } from 'react';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { X, Target, AlertCircle } from 'lucide-react';
import { createGoal, type LearningGoal, type LearningGoalCreate } from '../../services/student';

interface CreateGoalModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (newGoal: LearningGoal) => void;
}

export function CreateGoalModal({ isOpen, onClose, onSuccess }: CreateGoalModalProps) {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('QUANTITATIVE_APTITUDE');
  const [targetType, setTargetType] = useState('MINUTES_PRACTICED');
  const [targetValue, setTargetValue] = useState('120');
  const [deadline, setDeadline] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const val = parseFloat(targetValue);
    if (isNaN(val) || val <= 0) {
      setError('Target value must be greater than 0.');
      return;
    }

    if (title.trim().length < 3) {
      setError('Goal title must be at least 3 characters.');
      return;
    }

    setIsLoading(true);

    try {
      const payload: LearningGoalCreate = {
        title: title.trim(),
        category,
        target_type: targetType,
        target_value: val,
        deadline: deadline ? new Date(deadline).toISOString() : undefined,
      };

      const goal = await createGoal(payload);
      onSuccess(goal);
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create learning goal');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#292444]/60 backdrop-blur-xs animate-in fade-in">
      <div className="bg-white rounded-3xl border border-[#E8E0D2] p-6 sm:p-8 max-w-md w-full shadow-warm-lg">
        <div className="flex items-center justify-between pb-4 border-b border-[#E8E0D2] mb-6">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-center text-[#FF5B3D]">
              <Target className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-[#292444] font-display">New Learning Goal</h3>
              <p className="text-xs text-[#5E5875]">Set an actionable preparation milestone</p>
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
          <Input
            label="Goal Title"
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Master Arithmetic Drills, Practice 50 DSA Problems"
          />

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-[#5E5875]">Target Discipline</label>
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
              <option value="GENERAL">General Milestone</option>
            </select>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-[#5E5875]">Metric Type</label>
              <select
                value={targetType}
                onChange={(e) => setTargetType(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-[#E8E0D2] bg-white text-sm text-[#292444] focus:outline-none focus:ring-2 focus:ring-[#FF5B3D]/20 focus:border-[#FF5B3D]"
              >
                <option value="MINUTES_PRACTICED">Practice Minutes</option>
                <option value="QUESTIONS_COUNT">Questions Solved</option>
                <option value="ACCURACY_PERCENT">Target Accuracy %</option>
              </select>
            </div>

            <Input
              label="Target Goal"
              type="number"
              min="1"
              required
              value={targetValue}
              onChange={(e) => setTargetValue(e.target.value)}
              placeholder="120"
            />
          </div>

          <Input
            label="Target Completion Date (Optional)"
            type="date"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
          />

          <div className="pt-4 flex justify-end gap-3 border-t border-[#E8E0D2]">
            <Button variant="outline" size="sm" type="button" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" isLoading={isLoading}>
              Create Goal
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
