import React, { useState, useEffect, useRef } from 'react';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { Badge } from '../common/Badge';
import {
  loginUser,
  registerUser,
  detectUserRole,
  fetchInstitutions,
  requestPasswordReset,
  type UserSummary,
  type InstitutionItem,
  type DetectRoleResponse,
} from '../../services/auth';
import {
  X,
  Lock,
  Mail,
  User,
  Building,
  AlertCircle,
  CheckCircle2,
  GraduationCap,
  BookOpen,
  Briefcase,
  Shield,
  Sparkles,
  ArrowRight,
  Loader2,
} from 'lucide-react';

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

  // Common Fields
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [institutionId, setInstitutionId] = useState('');
  const [institutions, setInstitutions] = useState<InstitutionItem[]>([]);
  const [rollNumber, setRollNumber] = useState('');

  // Status & Live Detection State
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectedInfo, setDetectedInfo] = useState<DetectRoleResponse | null>(null);

  const debounceTimerRef = useRef<any>(null);

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

  // Real-time live email role & portal detection
  useEffect(() => {
    if (mode !== 'signin') {
      setDetectedInfo(null);
      setIsDetecting(false);
      return;
    }

    const cleanEmail = email.trim();
    if (!cleanEmail || !cleanEmail.includes('@') || cleanEmail.length < 5) {
      setDetectedInfo(null);
      setIsDetecting(false);
      return;
    }

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    setIsDetecting(true);
    debounceTimerRef.current = setTimeout(async () => {
      try {
        const info = await detectUserRole(cleanEmail);
        setDetectedInfo(info);
      } catch {
        setDetectedInfo(null);
      } finally {
        setIsDetecting(false);
      }
    }, 280);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [email, mode]);

  if (!isOpen) return null;

  const handleQuickFill = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setErrorMsg(null);
  };

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
          throw new Error('Please select an active college institution.');
        }

        const payload = {
          email: email.trim(),
          password,
          full_name: fullName.trim(),
          institution_id: institutionId,
          roll_number: rollNumber.trim() || undefined,
        };

        const res = await registerUser(payload);
        onSuccess(res.user);
        onClose();
      } else if (mode === 'forgot') {
        const res = await requestPasswordReset(email);
        setSuccessMsg(res.message || 'If an account exists, a reset link has been dispatched.');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'An authentication error occurred. Please verify your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-[#292444]/65 backdrop-blur-xs animate-in fade-in overflow-y-auto">
      <div className="bg-white rounded-3xl border border-[#E8E0D2] p-5 sm:p-7 max-w-lg w-full shadow-warm-lg relative my-8 max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-[#8E879E] hover:text-[#292444] transition-colors p-1.5 rounded-full hover:bg-[#FAF6ED]"
          aria-label="Close dialog"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="mb-5">
          <div className="flex items-center gap-2 mb-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold tracking-wide uppercase bg-[#FAF6ED] text-[#FF5B3D] border border-[#E8E0D2]">
              <Sparkles className="w-3.5 h-3.5" />
              Institutional Authentication
            </span>
          </div>

          <h2 className="text-2xl font-black text-[#292444] font-display tracking-tight">
            {mode === 'signin'
              ? 'Access Your Campus Portal'
              : mode === 'register'
              ? 'Join Your Institutional Portal'
              : 'Password Recovery'}
          </h2>
          <p className="text-xs text-[#5E5875] mt-1 leading-relaxed">
            {mode === 'signin'
              ? 'Enter your institutional email. The platform automatically identifies your role and directs you to your designated portal.'
              : mode === 'register'
              ? 'Select your institutional role to provision access to the matching workspace and analytical tools.'
              : 'Enter your registered email address to receive secure recovery credentials.'}
          </p>
        </div>

        {/* Mode Selector Tabs */}
        {mode !== 'forgot' && (
          <div className="flex bg-[#F5EFE3] p-1 rounded-xl mb-5 border border-[#E8E0D2]">
            <button
              type="button"
              onClick={() => {
                setMode('signin');
                setErrorMsg(null);
              }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                mode === 'signin'
                  ? 'bg-white text-[#292444] shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Sign In (Auto-Detect Role)
            </button>
            <button
              type="button"
              onClick={() => {
                setMode('register');
                setErrorMsg(null);
              }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                mode === 'register'
                  ? 'bg-white text-[#292444] shadow-xs'
                  : 'text-[#5E5875] hover:text-[#292444]'
              }`}
            >
              Register Portal Account
            </button>
          </div>
        )}

        {/* Alerts */}
        {errorMsg && (
          <div className="mb-4 p-3 rounded-xl bg-[#FEF2F2] border border-[#FECACA] flex items-start gap-2.5 text-xs text-[#B91C1C]">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <p className="font-semibold leading-relaxed">{errorMsg}</p>
          </div>
        )}

        {successMsg && (
          <div className="mb-4 p-3 rounded-xl bg-[#F0FDF4] border border-[#BBF7D0] flex items-start gap-2.5 text-xs text-[#15803D]">
            <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
            <p className="font-semibold leading-relaxed">{successMsg}</p>
          </div>
        )}

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* ===================== REGISTRATION MODE (STUDENT ONLY) ===================== */}
          {mode === 'register' && (
            <>
              {/* Student Portal Notice */}
              <div className="p-3.5 rounded-2xl bg-[#FAF6ED] border border-[#E8E0D2] text-xs">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] uppercase font-bold text-[#FF5B3D] tracking-wider">
                    Student Preparation Portal
                  </span>
                </div>
                <p className="text-[11px] text-[#5E5875] leading-relaxed">
                  Self-registration is available for students. Faculty, Trainer, and Placement Officer credentials are securely provisioned by your campus administrator.
                </p>
              </div>

              {/* Full Name */}
              <Input
                label="Full Name"
                placeholder="e.g. Kawin Sundararajan"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                leftIcon={<User className="w-4 h-4" />}
              />

              {/* College Institution Dropdown */}
              <div className="text-left">
                <label className="block text-xs font-bold uppercase tracking-wider text-[#5E5875] mb-1.5">
                  Institutional College
                </label>
                <div className="relative">
                  <select
                    className="w-full bg-white text-[#292444] border border-[#E8E0D2] rounded-xl px-4 py-2.5 text-xs sm:text-sm focus:outline-none focus:border-[#FF5B3D] focus:ring-3 focus:ring-[#FF5B3D]/15 transition-all"
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

              {/* Student Roll Number (Optional) */}
              <div>
                <Input
                  label="Roll / Registration Number (Optional)"
                  placeholder="e.g. 26CS001"
                  value={rollNumber}
                  onChange={(e) => setRollNumber(e.target.value)}
                  leftIcon={<Building className="w-4 h-4" />}
                />
              </div>
            </>
          )}

          {/* ===================== SIGN-IN / COMMON EMAIL ===================== */}
          <div>
            <Input
              label={mode === 'register' ? 'Student Email' : 'Email Address'}
              type="email"
              placeholder={mode === 'register' ? 'student@college.edu' : 'student@college.edu / officer@college.edu'}
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              leftIcon={<Mail className="w-4 h-4" />}
            />

            {/* LIVE AUTOMATIC ROLE & PORTAL DETECTION BADGE (SIGN-IN MODE) */}
            {mode === 'signin' && (
              <div className="mt-2 min-h-[36px]">
                {isDetecting ? (
                  <div className="flex items-center gap-2 p-2 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] text-xs text-[#5E5875] animate-pulse">
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-[#FF5B3D]" />
                    <span>Detecting institutional role and designated portal...</span>
                  </div>
                ) : detectedInfo?.exists ? (
                  <div className="p-2.5 rounded-xl bg-[#F0FDF4] border border-[#86EFAC] text-xs transition-all">
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-1.5 font-bold text-[#15803D]">
                        <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                        <span>Verified Account: {detectedInfo.full_name}</span>
                      </div>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-[#DCFCE7] text-[#166534] border border-[#86EFAC]">
                        {detectedInfo.role}
                      </span>
                    </div>
                    <div className="mt-1 flex items-center gap-1.5 text-[11px] text-[#166534] font-medium">
                      <span>Target Portal:</span>
                      <strong className="underline decoration-[#86EFAC] underline-offset-2">
                        {detectedInfo.portal_name}
                      </strong>
                    </div>
                  </div>
                ) : detectedInfo && !detectedInfo.exists && detectedInfo.portal_name ? (
                  <div className="p-2.5 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] text-xs flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-[#5E5875]">
                      <Sparkles className="w-3.5 h-3.5 text-[#FF5B3D]" />
                      <span>Inferred Target: <strong>{detectedInfo.portal_name}</strong></span>
                    </div>
                    {detectedInfo.role && (
                      <Badge variant="neutral" className="text-[10px]">
                        {detectedInfo.role}
                      </Badge>
                    )}
                  </div>
                ) : null}
              </div>
            )}
          </div>

          {/* Password Field */}
          {mode !== 'forgot' && (
            <div>
              <Input
                label="Password"
                type="password"
                placeholder="Enter account password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                leftIcon={<Lock className="w-4 h-4" />}
                helperText={
                  mode === 'register'
                    ? 'Requires minimum 8 characters with upper, lower, number, and symbol.'
                    : undefined
                }
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

          {/* Quick Demo Credentials in Sign-In Mode */}
          {mode === 'signin' && (
            <div className="pt-1 border-t border-[#E8E0D2]/60">
              <span className="block text-[10px] uppercase font-bold text-[#8E879E] tracking-wider mb-1.5">
                Quick Demo Portal Logins:
              </span>
              <div className="grid grid-cols-2 gap-1.5">
                <button
                  type="button"
                  onClick={() => handleQuickFill('student@college.edu', 'Student@2026!')}
                  className="px-2 py-1.5 rounded-lg border border-[#E8E0D2] bg-[#FAF6ED] hover:bg-white text-[11px] font-semibold text-[#292444] text-left transition-colors flex items-center gap-1.5"
                >
                  <GraduationCap className="w-3.5 h-3.5 text-[#FF5B3D]" />
                  <span>Student</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickFill('trainer@college.edu', 'Trainer@2026!')}
                  className="px-2 py-1.5 rounded-lg border border-[#E8E0D2] bg-[#FAF6ED] hover:bg-white text-[11px] font-semibold text-[#292444] text-left transition-colors flex items-center gap-1.5"
                >
                  <BookOpen className="w-3.5 h-3.5 text-[#4F46E5]" />
                  <span>Trainer</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickFill('officer@college.edu', 'Officer@2026!')}
                  className="px-2 py-1.5 rounded-lg border border-[#E8E0D2] bg-[#FAF6ED] hover:bg-white text-[11px] font-semibold text-[#292444] text-left transition-colors flex items-center gap-1.5"
                >
                  <Briefcase className="w-3.5 h-3.5 text-[#059669]" />
                  <span>Placement Officer</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickFill('admin@college.edu', 'Admin@2026!')}
                  className="px-2 py-1.5 rounded-lg border border-[#E8E0D2] bg-[#FAF6ED] hover:bg-white text-[11px] font-semibold text-[#292444] text-left transition-colors flex items-center gap-1.5"
                >
                  <Shield className="w-3.5 h-3.5 text-[#292444]" />
                  <span>Admin Console</span>
                </button>
              </div>
            </div>
          )}

          {/* Submit Action Button */}
          <div className="pt-2">
            <Button
              variant="primary"
              size="md"
              type="submit"
              isLoading={isLoading}
              className="w-full flex items-center justify-center gap-2 text-sm font-bold shadow-warm-sm"
            >
              {mode === 'signin' ? (
                <>
                  <span>
                    {detectedInfo?.portal_name
                      ? `Sign In to ${detectedInfo.portal_name}`
                      : 'Sign In to Portal'}
                  </span>
                  <ArrowRight className="w-4 h-4" />
                </>
              ) : mode === 'register' ? (
                <>
                  <span>Complete Student Registration</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              ) : (
                'Send Recovery Link'
              )}
            </Button>
          </div>

          {/* Back to Sign In Link */}
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
