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
  Key,
} from 'lucide-react';

export interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: UserSummary) => void;
  initialMode?: 'signin' | 'register';
}

type UserRole = 'STUDENT' | 'TRAINER' | 'PLACEMENT_OFFICER' | 'ADMIN';

interface RoleConfig {
  role: UserRole;
  title: string;
  shortLabel: string;
  portalName: string;
  description: string;
  badge: string;
  icon: React.ComponentType<{ className?: string }>;
  accentColor: string;
  idFieldLabel: string;
  idFieldPlaceholder: string;
  deptFieldLabel: string;
  deptFieldPlaceholder: string;
  requiresAccessCode?: boolean;
}

const ROLE_CONFIGS: Record<UserRole, RoleConfig> = {
  STUDENT: {
    role: 'STUDENT',
    title: 'Student Learner',
    shortLabel: 'Student',
    portalName: 'Student Preparation Workspace',
    description: 'Timed drills, cognitive analytics & AI readiness coaching',
    badge: 'Undergraduate / Postgrad',
    icon: GraduationCap,
    accentColor: '#FF5B3D',
    idFieldLabel: 'Roll Number / Student Registration ID',
    idFieldPlaceholder: 'e.g. 26CS042 or USN101',
    deptFieldLabel: 'Academic Department / Major',
    deptFieldPlaceholder: 'e.g. Computer Science & Engineering',
  },
  TRAINER: {
    role: 'TRAINER',
    title: 'Faculty & Technical Trainer',
    shortLabel: 'Trainer',
    portalName: 'Trainer & Faculty Portal',
    description: 'Cohort skill tracking, attendance & drill effectiveness',
    badge: 'Faculty / Mentor',
    icon: BookOpen,
    accentColor: '#4F46E5',
    idFieldLabel: 'Faculty Employee ID',
    idFieldPlaceholder: 'e.g. FAC-2026-88',
    deptFieldLabel: 'Training Track / Domain',
    deptFieldPlaceholder: 'e.g. Quantitative Aptitude & Data Structures',
  },
  PLACEMENT_OFFICER: {
    role: 'PLACEMENT_OFFICER',
    title: 'Placement Officer',
    shortLabel: 'Placement Cell',
    portalName: 'Placement Operations Ledger',
    description: 'Drive management, offer verification & verified audit ledger',
    badge: 'Career Services',
    icon: Briefcase,
    accentColor: '#059669',
    idFieldLabel: 'Placement Staff ID',
    idFieldPlaceholder: 'e.g. TPO-8812',
    deptFieldLabel: 'Placement Division / Cell',
    deptFieldPlaceholder: 'e.g. Corporate Relations & Career Center',
  },
  ADMIN: {
    role: 'ADMIN',
    title: 'College Administrator',
    shortLabel: 'Administrator',
    portalName: 'College Intelligence & Administration Console',
    description: 'Institution-wide metrics, system audit events & governance',
    badge: 'Governance / Leadership',
    icon: Shield,
    accentColor: '#292444',
    idFieldLabel: 'Administrator Staff ID',
    idFieldPlaceholder: 'e.g. ADM-001',
    deptFieldLabel: 'Office / Directorate',
    deptFieldPlaceholder: 'e.g. Office of the Dean / Director',
    requiresAccessCode: true,
  },
};

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  initialMode = 'signin',
}) => {
  const [mode, setMode] = useState<'signin' | 'register' | 'forgot'>(initialMode);
  const [selectedRole, setSelectedRole] = useState<UserRole>('STUDENT');

  // Common Fields
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [institutionId, setInstitutionId] = useState('');
  const [institutions, setInstitutions] = useState<InstitutionItem[]>([]);

  // Role-Specific Fields
  const [rollNumber, setRollNumber] = useState('');
  const [employeeId, setEmployeeId] = useState('');
  const [departmentName, setDepartmentName] = useState('');
  const [accessCode, setAccessCode] = useState('');

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

  const currentRoleCfg = ROLE_CONFIGS[selectedRole];

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
          role: selectedRole,
          roll_number: selectedRole === 'STUDENT' ? rollNumber.trim() : undefined,
          employee_id: selectedRole !== 'STUDENT' ? employeeId.trim() : undefined,
          department_name: departmentName.trim() || undefined,
          access_code: selectedRole === 'ADMIN' ? accessCode.trim() : undefined,
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
          {/* ===================== REGISTRATION MODE ===================== */}
          {mode === 'register' && (
            <>
              {/* Role Selection Grid */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#5E5875] mb-2">
                  Select Your Institutional Role
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {(Object.keys(ROLE_CONFIGS) as UserRole[]).map((rKey) => {
                    const cfg = ROLE_CONFIGS[rKey];
                    const IconComponent = cfg.icon;
                    const isSelected = selectedRole === rKey;
                    return (
                      <button
                        key={rKey}
                        type="button"
                        onClick={() => setSelectedRole(rKey)}
                        className={`text-left p-3 rounded-2xl border transition-all relative ${
                          isSelected
                            ? 'bg-[#FAF6ED] border-[#FF5B3D] shadow-xs ring-1 ring-[#FF5B3D]'
                            : 'bg-white border-[#E8E0D2] hover:border-[#8E879E]'
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <div
                            className={`p-1.5 rounded-lg text-white`}
                            style={{ backgroundColor: cfg.accentColor }}
                          >
                            <IconComponent className="w-3.5 h-3.5" />
                          </div>
                          <span className="font-bold text-xs text-[#292444] line-clamp-1">
                            {cfg.shortLabel}
                          </span>
                        </div>
                        <p className="text-[10px] text-[#5E5875] line-clamp-1">
                          {cfg.portalName}
                        </p>
                      </button>
                    );
                  })}
                </div>

                {/* Target Portal Confirmation Banner */}
                <div className="mt-2.5 p-2.5 rounded-xl bg-[#FAF6ED] border border-[#E8E0D2] flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase font-bold text-[#FF5B3D] tracking-wider">
                      Assigned Portal:
                    </span>
                    <span className="font-extrabold text-[#292444]">
                      {currentRoleCfg.portalName}
                    </span>
                  </div>
                  <Badge variant="neutral" className="text-[10px] py-0 px-2">
                    {selectedRole}
                  </Badge>
                </div>
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

              {/* Dynamic Role-Specific Fields */}
              {selectedRole === 'STUDENT' ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <Input
                    label={currentRoleCfg.idFieldLabel}
                    placeholder={currentRoleCfg.idFieldPlaceholder}
                    value={rollNumber}
                    onChange={(e) => setRollNumber(e.target.value)}
                    leftIcon={<Building className="w-4 h-4" />}
                  />
                  <Input
                    label={currentRoleCfg.deptFieldLabel}
                    placeholder={currentRoleCfg.deptFieldPlaceholder}
                    value={departmentName}
                    onChange={(e) => setDepartmentName(e.target.value)}
                    leftIcon={<BookOpen className="w-4 h-4" />}
                  />
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <Input
                    label={currentRoleCfg.idFieldLabel}
                    placeholder={currentRoleCfg.idFieldPlaceholder}
                    required
                    value={employeeId}
                    onChange={(e) => setEmployeeId(e.target.value)}
                    leftIcon={<Building className="w-4 h-4" />}
                  />
                  <Input
                    label={currentRoleCfg.deptFieldLabel}
                    placeholder={currentRoleCfg.deptFieldPlaceholder}
                    value={departmentName}
                    onChange={(e) => setDepartmentName(e.target.value)}
                    leftIcon={<BookOpen className="w-4 h-4" />}
                  />
                </div>
              )}

              {/* Admin Access Code Verification */}
              {selectedRole === 'ADMIN' && (
                <div>
                  <Input
                    label="Administrator Verification Key"
                    placeholder="Enter security access code (e.g. ADMIN2026)"
                    required
                    value={accessCode}
                    onChange={(e) => setAccessCode(e.target.value)}
                    leftIcon={<Key className="w-4 h-4" />}
                    helperText="Campus security key required for administrator account provisioning."
                  />
                </div>
              )}
            </>
          )}

          {/* ===================== SIGN-IN / COMMON EMAIL ===================== */}
          <div>
            <Input
              label={
                mode === 'register'
                  ? selectedRole === 'STUDENT'
                    ? 'Student Email'
                    : 'Institutional Email'
                  : 'Email Address'
              }
              type="email"
              placeholder={
                mode === 'register'
                  ? `${selectedRole.toLowerCase()}@college.edu`
                  : 'student@college.edu / officer@college.edu'
              }
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
                  <span>Complete {currentRoleCfg.shortLabel} Registration</span>
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
