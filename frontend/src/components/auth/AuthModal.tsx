import React, { useState, useEffect } from 'react';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { Badge } from '../common/Badge';
import {
  loginUser,
  registerStudent,
  fetchInstitutions,
  requestPasswordReset,
  type UserSummary,
  type InstitutionItem,
} from '../../services/auth';
import { X, Lock, Mail, User, Building, AlertCircle, CheckCircle2 } from 'lucide-react';

export interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: UserSummary) => void;
  initialMode?: 'signin' | 'register';
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  initialMode = 'signin',
}) => {
  const [mode, setMode] = useState<'signin' | 'register' | 'forgot'>(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [rollNumber, setRollNumber] = useState('');
  const [institutionId, setInstitutionId] = useState('');
  const [institutions, setInstitutions] = useState<InstitutionItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    setMode(initialMode);
    setErrorMsg(null);
    setSuccessMsg(null);
  }, [initialMode, isOpen]);

  useEffect(() => {
    if (isOpen) {
      fetchInstitutions().then((data) => {
        setInstitutions(data);
        if (data.length > 0 && !institutionId) {
          setInstitutionId(data[0].id);
        }
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      if (mode === 'signin') {
        const res = await loginUser(email, password);
        onSuccess(res.user);
        onClose();
      } else if (mode === 'register') {
        if (!institutionId) {
          throw new Error('Please select an active college institution');
        }
        const res = await registerStudent({
          email,
          password,
          full_name: fullName,
          institution_id: institutionId,
          roll_number: rollNumber || undefined,
        });
        onSuccess(res.user);
        onClose();
      } else if (mode === 'forgot') {
        const res = await requestPasswordReset(email);
        setSuccessMsg(res.message);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred during authentication');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#292444]/60 backdrop-blur-xs animate-in fade-in">
      <div className="bg-white rounded-3xl border border-[#E8E0D2] p-6 sm:p-8 max-w-md w-full shadow-warm-lg relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 text-[#8E879E] hover:text-[#292444] transition-colors p-1"
          aria-label="Close dialog"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="mb-6">
          <Badge variant="coral" className="mb-2">
            Secure Access · Phase 3
          </Badge>
          <h2 className="text-2xl font-extrabold text-[#292444] font-display">
            {mode === 'signin'
              ? 'Sign in to your account'
              : mode === 'register'
              ? 'Student Registration'
              : 'Reset your password'}
          </h2>
          <p className="text-xs text-[#5E5875] mt-1">
            {mode === 'signin'
              ? 'Enter your institutional credentials to continue.'
              : mode === 'register'
              ? 'Create a verified student learning account.'
              : 'Enter your email to receive a password reset token.'}
          </p>
        </div>

        {/* Mode Selector Tabs */}
        {mode !== 'forgot' && (
          <div className="flex bg-[#F5EFE3] p-1 rounded-xl mb-6 border border-[#E8E0D2]">
            <button
              type="button"
              onClick={() => {
                setMode('signin');
                setErrorMsg(null);
              }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                mode === 'signin' ? 'bg-white text-[#292444] shadow-xs' : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setMode('register');
                setErrorMsg(null);
              }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                mode === 'register' ? 'bg-white text-[#292444] shadow-xs' : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Student Register
            </button>
          </div>
        )}

        {/* Error / Success Alerts */}
        {errorMsg && (
          <div className="mb-4 p-3 rounded-xl bg-[#FEF2F2] border border-[#FECACA] flex items-start gap-2.5 text-xs text-[#B91C1C]">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <p className="font-medium leading-relaxed">{errorMsg}</p>
          </div>
        )}

        {successMsg && (
          <div className="mb-4 p-3 rounded-xl bg-[#F0FDF4] border border-[#BBF7D0] flex items-start gap-2.5 text-xs text-[#15803D]">
            <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
            <p className="font-medium leading-relaxed">{successMsg}</p>
          </div>
        )}

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <>
              <Input
                label="Full Name"
                placeholder="e.g. Kawin Sundararajan"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                leftIcon={<User className="w-4 h-4" />}
              />

              <div className="text-left">
                <label className="block text-xs font-bold uppercase tracking-wider text-[#5E5875] mb-2">
                  College Institution
                </label>
                <div className="relative">
                  <select
                    className="w-full bg-white text-[#292444] border border-[#E8E0D2] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[#FF5B3D] focus:ring-4 focus:ring-[#FF5B3D]/20 transition-all"
                    value={institutionId}
                    onChange={(e) => setInstitutionId(e.target.value)}
                    required
                  >
                    {institutions.length === 0 ? (
                      <option value="">No institutions registered</option>
                    ) : (
                      institutions.map((inst) => (
                        <option key={inst.id} value={inst.id}>
                          {inst.name} ({inst.code})
                        </option>
                      ))
                    )}
                  </select>
                </div>
              </div>

              <Input
                label="Roll Number / Registration ID (Optional)"
                placeholder="e.g. 26CS042"
                value={rollNumber}
                onChange={(e) => setRollNumber(e.target.value)}
                leftIcon={<Building className="w-4 h-4" />}
              />
            </>
          )}

          <Input
            label="Email Address"
            type="email"
            placeholder="student@college.edu"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            leftIcon={<Mail className="w-4 h-4" />}
          />

          {mode !== 'forgot' && (
            <div>
              <Input
                label="Password"
                type="password"
                placeholder="Minimum 8 characters"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                leftIcon={<Lock className="w-4 h-4" />}
                helperText={mode === 'register' ? 'Requires upper, lower, digit, and special symbol' : undefined}
              />
              {mode === 'signin' && (
                <div className="mt-1.5 text-right">
                  <button
                    type="button"
                    onClick={() => {
                      setMode('forgot');
                      setErrorMsg(null);
                    }}
                    className="text-xs text-[#5E5875] hover:text-[#FF5B3D] font-semibold transition-colors"
                  >
                    Forgot password?
                  </button>
                </div>
              )}
            </div>
          )}

          <div className="pt-2">
            <Button variant="primary" size="md" type="submit" isLoading={isLoading} className="w-full">
              {mode === 'signin'
                ? 'Sign In to Portal'
                : mode === 'register'
                ? 'Complete Registration'
                : 'Send Reset Link'}
            </Button>
          </div>

          {mode === 'forgot' && (
            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => {
                  setMode('signin');
                  setErrorMsg(null);
                  setSuccessMsg(null);
                }}
                className="text-xs text-[#5E5875] hover:text-[#292444] font-semibold"
              >
                ← Back to Sign In
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};
