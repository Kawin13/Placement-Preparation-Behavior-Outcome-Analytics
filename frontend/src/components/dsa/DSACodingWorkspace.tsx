import React, { useState, useEffect } from 'react';
import {
  fetchProblemDetails,
  runDSACode,
  submitDSASolution,
  fetchSubmissionHistory,
  fetchProblemEditorial,
  type DSAProblemDetail,
  type DSARunCodeResponse,
  type DSASubmitResponse,
  type DSASubmissionHistoryItem,
  type DSAEditorialResponse,
} from '../../services/dsa';

interface Props {
  problemSlug: string;
  onBack: () => void;
}

export const DSACodingWorkspace: React.FC<Props> = ({ problemSlug, onBack }) => {
  const [problem, setProblem] = useState<DSAProblemDetail | null>(null);
  const [language, setLanguage] = useState<'python' | 'java'>('python');
  const [code, setCode] = useState<string>('');

  // Tabs on Left Pane: description | hints | submissions | editorial
  const [leftTab, setLeftTab] = useState<'description' | 'hints' | 'submissions' | 'editorial'>('description');
  const [revealedHints, setRevealedHints] = useState<number>(0);
  const [submissions, setSubmissions] = useState<DSASubmissionHistoryItem[]>([]);
  const [editorial, setEditorial] = useState<DSAEditorialResponse | null>(null);

  // Bottom Console Tabs: testcases | result
  const [consoleTab, setConsoleTab] = useState<'testcases' | 'result'>('testcases');
  const [activeTestCaseIndex, setActiveTestCaseIndex] = useState<number>(0);
  const [customInput, setCustomInput] = useState<string>('');
  const [useCustomInput, setUseCustomInput] = useState<boolean>(false);

  // Execution states
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [runResult, setRunResult] = useState<DSARunCodeResponse | null>(null);
  const [submitResult, setSubmitResult] = useState<DSASubmitResponse | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProblem();
  }, [problemSlug]);

  useEffect(() => {
    if (problem) {
      const starter = problem.starter_code[language] || '';
      setCode(starter);
    }
  }, [language, problem]);

  const loadProblem = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchProblemDetails(problemSlug);
      setProblem(data);
      if (data.starter_code[language]) {
        setCode(data.starter_code[language]);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load problem');
    } finally {
      setLoading(false);
    }
  };

  const loadSubmissions = async () => {
    try {
      const data = await fetchSubmissionHistory(problemSlug);
      setSubmissions(data);
    } catch (err) {
      console.error('Failed to load submissions', err);
    }
  };

  const loadEditorial = async () => {
    try {
      const data = await fetchProblemEditorial(problemSlug);
      setEditorial(data);
    } catch (err) {
      console.error('Failed to load editorial', err);
    }
  };

  const handleTabChange = (tab: 'description' | 'hints' | 'submissions' | 'editorial') => {
    setLeftTab(tab);
    if (tab === 'submissions') loadSubmissions();
    if (tab === 'editorial') loadEditorial();
  };

  const handleResetCode = () => {
    if (problem && problem.starter_code[language]) {
      if (window.confirm('Reset code to initial starter template?')) {
        setCode(problem.starter_code[language]);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const target = e.currentTarget;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      const newCode = code.substring(0, start) + '    ' + code.substring(end);
      setCode(newCode);
      setTimeout(() => {
        target.selectionStart = target.selectionEnd = start + 4;
      }, 0);
    }
  };

  const handleRunCode = async () => {
    try {
      setIsRunning(true);
      setSubmitResult(null);
      setConsoleTab('result');
      const res = await runDSACode(problemSlug, {
        language,
        code,
        custom_input: useCustomInput ? customInput : undefined,
      });
      setRunResult(res);
    } catch (err: any) {
      alert(`Run Code failed: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = async () => {
    try {
      setIsSubmitting(true);
      setRunResult(null);
      setConsoleTab('result');
      const res = await submitDSASolution(problemSlug, {
        language,
        code,
        hints_viewed: revealedHints,
      });
      setSubmitResult(res);
      // Reload problem progress if newly solved
      if (res.verdict === 'ACCEPTED' && problem) {
        setProblem({ ...problem, user_status: 'SOLVED' });
      }
    } catch (err: any) {
      alert(`Submission failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[500px] flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-3 border-[#FF5B3D] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm font-semibold text-gray-600">Launching Coding Workspace...</p>
        </div>
      </div>
    );
  }

  if (error || !problem) {
    return (
      <div className="p-8 text-center bg-white rounded-2xl border border-[#E8E0D2] shadow-sm max-w-lg mx-auto">
        <p className="text-rose-600 font-bold mb-4">{error || 'Problem not found'}</p>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-[#292444] text-white rounded-xl text-xs font-semibold hover:bg-[#1E1B2E]"
        >
          ← Back to Problem Library
        </button>
      </div>
    );
  }

  const getDifficultyBadge = (diff: string) => {
    switch (diff) {
      case 'EASY':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'MEDIUM':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'HARD':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="space-y-4 animate-fadeIn">
      {/* Top Workspace Header Bar */}
      <div className="bg-white px-5 py-3 rounded-2xl border border-[#E8E0D2] shadow-sm flex flex-wrap items-center justify-between gap-4">
        {/* Left: Back & Title */}
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-1.5 rounded-lg border border-[#E8E0D2] text-gray-600 hover:bg-[#FAF6ED] transition-colors text-xs font-semibold flex items-center gap-1"
          >
            ← <span>Problems</span>
          </button>
          <div className="h-4 w-px bg-[#E8E0D2]" />
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-gray-400">#{problem.problem_number}</span>
            <h1 className="text-base font-extrabold text-[#292444]">{problem.title}</h1>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getDifficultyBadge(problem.difficulty)}`}>
              {problem.difficulty}
            </span>
            {problem.user_status === 'SOLVED' && (
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-700">
                ✓ Solved
              </span>
            )}
          </div>
        </div>

        {/* Right: Language Selector & Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 font-medium">Language:</span>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as any)}
              className="text-xs font-semibold border border-[#E8E0D2] rounded-lg px-3 py-1.5 bg-[#FAF6ED] text-[#292444] focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
            >
              <option value="python">Python 3.12</option>
              <option value="java">Java 21 LTS</option>
            </select>
          </div>

          <button
            onClick={handleResetCode}
            className="px-2.5 py-1.5 text-xs text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors border border-transparent hover:border-gray-200"
            title="Reset to starter code"
          >
            ↺ Reset
          </button>
        </div>
      </div>

      {/* Main Dual-Pane Studio */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 h-[calc(100vh-175px)] min-h-[600px]">
        {/* LEFT PANE: Problem Specs & Pedagogical Material (5 Cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-[#E8E0D2] shadow-sm flex flex-col overflow-hidden">
          {/* Left Tabs Bar */}
          <div className="flex items-center border-b border-[#E8E0D2] px-4 bg-[#FAF6ED]/50 text-xs font-semibold">
            {[
              { id: 'description', label: 'Description' },
              { id: 'hints', label: `Hints (${problem.hints.length})` },
              { id: 'submissions', label: 'Submissions' },
              { id: 'editorial', label: 'Editorial' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id as any)}
                className={`py-3 px-3 transition-colors relative border-b-2 ${
                  leftTab === tab.id
                    ? 'border-[#FF5B3D] text-[#FF5B3D] font-bold'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Left Content Area */}
          <div className="p-5 overflow-y-auto flex-1 text-xs space-y-5 text-gray-700">
            {leftTab === 'description' && (
              <>
                {/* Description */}
                <div>
                  <h3 className="font-bold text-[#292444] text-sm mb-2">Problem Statement</h3>
                  <div className="whitespace-pre-line leading-relaxed text-gray-800">
                    {problem.description}
                  </div>
                </div>

                {/* Examples */}
                {problem.examples.length > 0 && (
                  <div className="space-y-3">
                    <h4 className="font-bold text-[#292444] uppercase tracking-wider text-[11px]">
                      Examples
                    </h4>
                    {problem.examples.map((ex, idx) => (
                      <div
                        key={idx}
                        className="bg-[#FAF6ED]/70 p-3.5 rounded-xl border border-[#E8E0D2] space-y-1.5 font-mono text-[11px]"
                      >
                        <div className="text-gray-500 font-sans font-bold text-xs">Example {idx + 1}:</div>
                        <div>
                          <span className="text-gray-500">Input: </span>
                          <span className="text-[#292444] font-semibold">{ex.input}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Output: </span>
                          <span className="text-emerald-700 font-bold">{ex.output}</span>
                        </div>
                        {ex.explanation && (
                          <div className="text-gray-600 font-sans text-xs pt-1">
                            <span className="font-semibold text-gray-700">Explanation: </span>
                            {ex.explanation}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Constraints */}
                {problem.constraints && (
                  <div className="space-y-1.5">
                    <h4 className="font-bold text-[#292444] uppercase tracking-wider text-[11px]">
                      Constraints
                    </h4>
                    <div className="bg-gray-50 p-3 rounded-xl border border-gray-200 font-mono text-[11px] text-gray-800 whitespace-pre-line">
                      {problem.constraints}
                    </div>
                  </div>
                )}

                {/* Expected Complexity */}
                {(problem.expected_time_complexity || problem.expected_space_complexity) && (
                  <div className="flex items-center gap-4 p-3 bg-indigo-50 border border-indigo-100 rounded-xl text-indigo-900 text-xs">
                    {problem.expected_time_complexity && (
                      <div>
                        <span className="font-bold">Expected Time: </span>
                        <code>{problem.expected_time_complexity}</code>
                      </div>
                    )}
                    {problem.expected_space_complexity && (
                      <div>
                        <span className="font-bold">Expected Space: </span>
                        <code>{problem.expected_space_complexity}</code>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}

            {leftTab === 'hints' && (
              <div className="space-y-4">
                <p className="text-gray-500 text-xs">
                  Unlock progressive clues without spoiling the complete solution:
                </p>
                {problem.hints.length === 0 ? (
                  <p className="text-gray-400">No hints available for this problem.</p>
                ) : (
                  problem.hints.map((hint, idx) => {
                    const isRevealed = idx < revealedHints;
                    return (
                      <div
                        key={idx}
                        className={`p-3.5 rounded-xl border transition-all ${
                          isRevealed
                            ? 'bg-amber-50 border-amber-200 text-amber-900'
                            : 'bg-gray-50 border-gray-200 text-gray-400'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-xs">Hint {idx + 1}</span>
                          {!isRevealed && idx === revealedHints && (
                            <button
                              onClick={() => setRevealedHints(revealedHints + 1)}
                              className="px-2.5 py-1 rounded bg-[#FF5B3D] text-white text-[11px] font-semibold hover:bg-[#e0482b]"
                            >
                              Reveal Hint
                            </button>
                          )}
                        </div>
                        {isRevealed ? (
                          <p className="text-xs leading-relaxed">{hint}</p>
                        ) : (
                          <p className="text-[11px] italic">Locked hint. Click Reveal when ready.</p>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            )}

            {leftTab === 'submissions' && (
              <div className="space-y-3">
                <h4 className="font-bold text-[#292444] text-xs">Submission History</h4>
                {submissions.length === 0 ? (
                  <p className="text-gray-400 py-4">No submissions yet for this problem.</p>
                ) : (
                  <div className="divide-y divide-gray-100">
                    {submissions.map((s) => (
                      <div key={s.id} className="py-2.5 flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                              s.verdict === 'ACCEPTED'
                                ? 'bg-emerald-100 text-emerald-700'
                                : 'bg-rose-100 text-rose-700'
                            }`}
                          >
                            {s.verdict}
                          </span>
                          <span className="text-gray-500 text-[11px] capitalize">{s.language}</span>
                        </div>
                        <div className="text-right text-[11px] text-gray-500">
                          <span>{s.runtime_ms ? `${s.runtime_ms} ms` : '—'}</span>
                          <span className="mx-1">•</span>
                          <span>{new Date(s.submitted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {leftTab === 'editorial' && (
              <div className="space-y-4">
                {editorial?.editorial ? (
                  <div className="prose prose-sm max-w-none text-gray-800 leading-relaxed whitespace-pre-line">
                    {editorial.editorial}
                  </div>
                ) : (
                  <p className="text-gray-400 py-4">Editorial solution is being compiled.</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT PANE: Code Console & Test Runner (7 Cols) */}
        <div className="lg:col-span-7 flex flex-col space-y-4">
          {/* Top Code Editor Area */}
          <div className="flex-1 bg-[#1E1B2E] rounded-2xl border border-[#292444]/30 shadow-sm flex flex-col overflow-hidden">
            {/* Editor Top Bar */}
            <div className="flex items-center justify-between px-4 py-2.5 bg-[#171424] border-b border-white/5 text-xs text-gray-400">
              <span className="font-mono text-[11px] text-gray-300">
                {language === 'python' ? 'solution.py' : 'Main.java'}
              </span>
              <span className="text-[10px] text-gray-500">Tab key supported (4 spaces)</span>
            </div>

            {/* Code Textarea with line numbers feeling */}
            <div className="flex-1 relative p-3">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                onKeyDown={handleKeyDown}
                spellCheck={false}
                className="w-full h-full bg-transparent text-gray-100 font-mono text-xs leading-relaxed focus:outline-none resize-none selection:bg-[#FF5B3D]/30"
                placeholder="// Write your solution here..."
              />
            </div>
          </div>

          {/* Bottom Console Drawer: Test Cases & Results */}
          <div className="bg-white rounded-2xl border border-[#E8E0D2] shadow-sm flex flex-col h-64 overflow-hidden">
            {/* Console Header Tabs */}
            <div className="flex items-center justify-between border-b border-[#E8E0D2] px-4 bg-[#FAF6ED]/50 text-xs">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setConsoleTab('testcases')}
                  className={`py-2 px-3 border-b-2 font-semibold transition-colors ${
                    consoleTab === 'testcases'
                      ? 'border-[#FF5B3D] text-[#FF5B3D]'
                      : 'border-transparent text-gray-500 hover:text-gray-800'
                  }`}
                >
                  Test Cases
                </button>
                <button
                  onClick={() => setConsoleTab('result')}
                  className={`py-2 px-3 border-b-2 font-semibold transition-colors ${
                    consoleTab === 'result'
                      ? 'border-[#FF5B3D] text-[#FF5B3D]'
                      : 'border-transparent text-gray-500 hover:text-gray-800'
                  }`}
                >
                  Test Result {runResult || submitResult ? '●' : ''}
                </button>
              </div>

              {/* Action Buttons: Run Code & Submit */}
              <div className="flex items-center gap-2 py-1.5">
                <button
                  onClick={handleRunCode}
                  disabled={isRunning || isSubmitting}
                  className="px-3.5 py-1.5 rounded-lg border border-[#292444] text-[#292444] hover:bg-[#292444] hover:text-white transition-colors text-xs font-bold disabled:opacity-50 flex items-center gap-1.5"
                >
                  {isRunning ? (
                    <>
                      <span className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
                      <span>Running...</span>
                    </>
                  ) : (
                    <>
                      <span>▶</span>
                      <span>Run Code</span>
                    </>
                  )}
                </button>

                <button
                  onClick={handleSubmit}
                  disabled={isRunning || isSubmitting}
                  className="px-4 py-1.5 rounded-lg bg-[#FF5B3D] text-white hover:bg-[#e0482b] transition-all text-xs font-bold shadow-sm disabled:opacity-50 flex items-center gap-1.5"
                >
                  {isSubmitting ? (
                    <>
                      <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Grading...</span>
                    </>
                  ) : (
                    <>
                      <span>⚡</span>
                      <span>Submit Solution</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Console Body */}
            <div className="p-4 overflow-y-auto flex-1 text-xs">
              {consoleTab === 'testcases' && (
                <div className="space-y-3">
                  {/* Case Pill Selector */}
                  <div className="flex items-center gap-2">
                    {problem.sample_test_cases.map((_, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          setActiveTestCaseIndex(idx);
                          setUseCustomInput(false);
                        }}
                        className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                          !useCustomInput && activeTestCaseIndex === idx
                            ? 'bg-[#292444] text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        Case {idx + 1}
                      </button>
                    ))}
                    <button
                      onClick={() => setUseCustomInput(true)}
                      className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                        useCustomInput
                          ? 'bg-[#292444] text-white'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      + Custom Input
                    </button>
                  </div>

                  {/* Case Details */}
                  {!useCustomInput ? (
                    problem.sample_test_cases[activeTestCaseIndex] && (
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <span className="text-[10px] uppercase font-bold text-gray-400 block mb-1">
                            Input (stdin)
                          </span>
                          <pre className="bg-[#FAF6ED] p-2.5 rounded-lg border border-[#E8E0D2] font-mono text-xs overflow-x-auto text-[#292444]">
                            {problem.sample_test_cases[activeTestCaseIndex].input_data}
                          </pre>
                        </div>
                        <div>
                          <span className="text-[10px] uppercase font-bold text-gray-400 block mb-1">
                            Expected Output
                          </span>
                          <pre className="bg-[#FAF6ED] p-2.5 rounded-lg border border-[#E8E0D2] font-mono text-xs overflow-x-auto text-[#292444]">
                            {problem.sample_test_cases[activeTestCaseIndex].expected_output}
                          </pre>
                        </div>
                      </div>
                    )
                  ) : (
                    <div>
                      <span className="text-[10px] uppercase font-bold text-gray-400 block mb-1">
                        Custom Stdin Input
                      </span>
                      <textarea
                        value={customInput}
                        onChange={(e) => setCustomInput(e.target.value)}
                        placeholder="Type test case input matching the input format..."
                        className="w-full h-20 p-2.5 font-mono text-xs bg-[#FAF6ED] border border-[#E8E0D2] rounded-lg focus:outline-none focus:ring-1 focus:ring-[#FF5B3D]"
                      />
                    </div>
                  )}
                </div>
              )}

              {consoleTab === 'result' && (
                <div>
                  {isRunning || isSubmitting ? (
                    <div className="py-8 text-center text-gray-500">
                      <div className="w-5 h-5 border-2 border-[#FF5B3D] border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                      <p className="text-xs">
                        {isRunning ? 'Executing test cases...' : 'Authoritative evaluation against hidden cases...'}
                      </p>
                    </div>
                  ) : submitResult ? (
                    /* Submit Result View */
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-3 py-1 rounded-lg text-xs font-extrabold ${
                              submitResult.verdict === 'ACCEPTED'
                                ? 'bg-emerald-100 text-emerald-700'
                                : 'bg-rose-100 text-rose-700'
                            }`}
                          >
                            {submitResult.verdict === 'ACCEPTED' ? '✓ Accepted' : submitResult.verdict}
                          </span>
                          <span className="text-xs font-semibold text-gray-700">
                            {submitResult.test_cases_passed} / {submitResult.total_test_cases} Test Cases Passed
                          </span>
                        </div>
                        <div className="text-xs text-gray-500 font-mono">
                          Runtime: {submitResult.runtime_ms ?? '—'} ms
                        </div>
                      </div>

                      {submitResult.verdict === 'ACCEPTED' && (
                        <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 text-emerald-800 text-xs">
                          🎉 Solution accepted! All test cases passed successfully.
                          {submitResult.is_first_solve && ' Your progress has been updated!'}
                        </div>
                      )}

                      {submitResult.error_message && (
                        <div className="bg-rose-50 p-3 rounded-xl border border-rose-200 text-rose-900 font-mono text-xs whitespace-pre-wrap">
                          {submitResult.error_message}
                        </div>
                      )}
                    </div>
                  ) : runResult ? (
                    /* Run Code Result View */
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span
                          className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                            runResult.status === 'SUCCESS' || runResult.status === 'ACCEPTED'
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-rose-100 text-rose-700'
                          }`}
                        >
                          {runResult.status}
                        </span>
                      </div>

                      {runResult.compilation_error && (
                        <pre className="bg-rose-50 text-rose-800 p-3 rounded-lg text-[11px] font-mono whitespace-pre-wrap">
                          {runResult.compilation_error}
                        </pre>
                      )}

                      {runResult.results.length > 0 && (
                        <div className="space-y-2">
                          {runResult.results.map((r, i) => (
                            <div
                              key={i}
                              className={`p-2.5 rounded-lg border text-xs ${
                                r.passed
                                  ? 'bg-emerald-50/50 border-emerald-200'
                                  : 'bg-rose-50/50 border-rose-200'
                              }`}
                            >
                              <div className="flex items-center justify-between font-bold mb-1">
                                <span>Case {r.case_index}</span>
                                <span className={r.passed ? 'text-emerald-600' : 'text-rose-600'}>
                                  {r.passed ? 'Passed' : 'Failed'} ({r.execution_time_ms} ms)
                                </span>
                              </div>
                              <div className="font-mono text-[11px] text-gray-700">
                                <div>
                                  <span className="text-gray-400">Actual: </span>
                                  {r.actual_output || '[Empty]'}
                                </div>
                                {r.expected_output && (
                                  <div>
                                    <span className="text-gray-400">Expected: </span>
                                    {r.expected_output}
                                  </div>
                                )}
                                {r.error && <div className="text-rose-600 mt-1">{r.error}</div>}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {runResult.custom_result && (
                        <div className="p-2.5 rounded-lg border bg-gray-50 border-gray-200 text-xs font-mono">
                          <span className="font-bold font-sans text-gray-700 block mb-1">Custom Input Result:</span>
                          <div>
                            <span className="text-gray-400">Stdout: </span>
                            {runResult.custom_result.actual_output || '[Empty]'}
                          </div>
                          {runResult.custom_result.error && (
                            <div className="text-rose-600">{runResult.custom_result.error}</div>
                          )}
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-gray-400 text-center py-6">
                      Click "Run Code" to test against public test cases or "Submit Solution" for full grading.
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
