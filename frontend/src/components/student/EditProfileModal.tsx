import { useState } from 'react';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { X, UserCheck, AlertCircle } from 'lucide-react';
import { updateStudentProfile, type StudentProfileDetailed, type StudentProfileUpdateRequest } from '../../services/student';

interface EditProfileModalProps {
  isOpen: boolean;
  profile: StudentProfileDetailed;
  onClose: () => void;
  onSuccess: (updated: StudentProfileDetailed) => void;
}

export function EditProfileModal({ isOpen, profile, onClose, onSuccess }: EditProfileModalProps) {
  const [fullName, setFullName] = useState(profile.user_full_name);
  const [rollNumber, setRollNumber] = useState(profile.roll_number);
  const [cgpa, setCgpa] = useState(profile.cgpa !== null ? profile.cgpa.toString() : '');
  const [placementStatus, setPlacementStatus] = useState(profile.placement_status);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const payload: StudentProfileUpdateRequest = {
        full_name: fullName.trim(),
        roll_number: rollNumber.trim().toUpperCase(),
        placement_status: placementStatus,
      };

      if (cgpa.trim() !== '') {
        const numCgpa = parseFloat(cgpa);
        if (isNaN(numCgpa) || numCgpa < 0 || numCgpa > 10) {
          throw new Error('CGPA must be a valid number between 0.00 and 10.00');
        }
        payload.cgpa = numCgpa;
      }

      const updated = await updateStudentProfile(payload);
      onSuccess(updated);
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
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
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-[#292444] font-display">Edit Student Profile</h3>
              <p className="text-xs text-[#5E5875]">Update approved institutional profile fields</p>
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
            label="Full Name"
            type="text"
            required
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />

          <Input
            label="Roll / Registration Number"
            type="text"
            required
            value={rollNumber}
            onChange={(e) => setRollNumber(e.target.value)}
            helperText="Must be unique within your institution."
          />

          <Input
            label="Cumulative GPA (0.00 - 10.00)"
            type="number"
            step="0.01"
            min="0"
            max="10"
            value={cgpa}
            onChange={(e) => setCgpa(e.target.value)}
            placeholder="e.g. 8.50"
          />

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-[#5E5875]">
              Placement Readiness Status
            </label>
            <select
              value={placementStatus}
              onChange={(e) => setPlacementStatus(e.target.value as any)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#E8E0D2] bg-white text-sm text-[#292444] focus:outline-none focus:ring-2 focus:ring-[#FF5B3D]/20 focus:border-[#FF5B3D] transition-colors"
            >
              <option value="NOT_PLACED">Not Placed (Actively Preparing)</option>
              <option value="IN_PROCESS">In Process (Interviewing / Shortlisted)</option>
              <option value="PLACED">Placed (Offer Received)</option>
              <option value="OPTED_OUT">Opted Out (Higher Studies / Family)</option>
            </select>
          </div>

          <div className="pt-4 flex justify-end gap-3 border-t border-[#E8E0D2]">
            <Button variant="outline" size="sm" type="button" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" isLoading={isLoading}>
              Save Profile
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
