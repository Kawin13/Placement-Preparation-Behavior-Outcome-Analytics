import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Plus,
  Search,
  CheckCircle2,
  RefreshCw,
  Upload,
  BookOpen,
  AlertCircle,
  Eye,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import {
  fetchQuestionBank,
  updateQuestionStatus,
  generateQuestionsWithAI,
  bulkImportQuestions,
  type QuestionDetail,
  type AIQuestionGenResult,
} from '../../services/practice';

export const QuestionBankManager: React.FC = () => {
  const [questions, setQuestions] = useState<QuestionDetail[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [domainFilter, setDomainFilter] = useState<string>('');
  const [difficultyFilter, setDifficultyFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState(true);

  // Selected question for detail preview
  const [selectedQuestion, setSelectedQuestion] = useState<QuestionDetail | null>(null);

  // AI Generation Modal State
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [aiDomain, setAiDomain] = useState('QUANT');
  const [aiTopic, setAiTopic] = useState('');
  const [aiDifficulty, setAiDifficulty] = useState('MEDIUM');
  const [aiCount, setAiCount] = useState(3);
  const [aiObjectives, setAiObjectives] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState<AIQuestionGenResult | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

  // Manual Question Authoring Modal
  const [isAuthorModalOpen, setIsAuthorModalOpen] = useState(false);
  const [manualTitle, setManualTitle] = useState('');
  const [manualContent, setManualContent] = useState('');
  const [manualDomain, setManualDomain] = useState('QUANT');
  const [manualDifficulty, setManualDifficulty] = useState('MEDIUM');
  const [manualExplanation, setManualExplanation] = useState('');
  const [manualOptions, setManualOptions] = useState([
    { option_text: '', is_correct: true, feedback: 'Correct derivation.' },
    { option_text: '', is_correct: false, feedback: 'Common mistake.' },
    { option_text: '', is_correct: false, feedback: 'Misapplication.' },
    { option_text: '', is_correct: false, feedback: 'Off by factor.' },
  ]);
  const [authorLoading, setAuthorLoading] = useState(false);

  // Bulk Import Modal
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [importJson, setImportJson] = useState('');
  const [importLoading, setImportLoading] = useState(false);

  useEffect(() => {
    loadQuestions();
  }, [page, domainFilter, difficultyFilter, statusFilter]);

  const loadQuestions = async () => {
    setLoading(true);
    try {
      const res = await fetchQuestionBank({
        domain: domainFilter || undefined,
        difficulty: difficultyFilter || undefined,
        status: statusFilter || undefined,
        search: searchQuery || undefined,
        page,
        page_size: pageSize,
      });
      setQuestions(res.items);
      setTotal(res.total);
    } catch (err: any) {
      alert(err.message || 'Failed to load question bank');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadQuestions();
  };

  const handleToggleStatus = async (qId: string, currentStatus: string) => {
    const nextStatus = currentStatus === 'PUBLISHED' ? 'ARCHIVED' : 'PUBLISHED';
    try {
      await updateQuestionStatus(qId, nextStatus);
      await loadQuestions();
      if (selectedQuestion && selectedQuestion.id === qId) {
        setSelectedQuestion({ ...selectedQuestion, status: nextStatus });
      }
    } catch (err: any) {
      alert(err.message || 'Failed to change status');
    }
  };

  const handleTriggerAiGeneration = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiTopic.trim()) {
      alert('Please specify a topic name');
      return;
    }
    setAiLoading(true);
    setAiError(null);
    setAiResult(null);
    try {
      const res = await generateQuestionsWithAI({
        domain: aiDomain,
        topic: aiTopic.trim(),
        difficulty: aiDifficulty,
        question_type: 'MCQ_SINGLE',
        count: aiCount,
        learning_objectives: aiObjectives.trim() || undefined,
      });
      setAiResult(res);
      await loadQuestions();
    } catch (err: any) {
      setAiError(err.message || 'AI generation failed');
    } finally {
      setAiLoading(false);
    }
  };

  const handleCreateManualQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualTitle.trim() || !manualContent.trim()) {
      alert('Please provide a title and question content');
      return;
    }
    setAuthorLoading(true);
    try {
      // Find or create skill on the fly using bulk import endpoint helper or dedicated create
      await bulkImportQuestions([
        {
          title: manualTitle.trim(),
          content: manualContent.trim(),
          skill_name: manualTitle.split(':')[0].trim() || 'General Problem Solving',
          domain: manualDomain,
          question_type: 'MCQ_SINGLE',
          difficulty: manualDifficulty,
          default_points: 1,
          explanation: manualExplanation.trim() || 'Verified standard curriculum solution.',
          options: manualOptions,
        },
      ]);
      setIsAuthorModalOpen(false);
      setManualTitle('');
      setManualContent('');
      setManualExplanation('');
      await loadQuestions();
    } catch (err: any) {
      alert(err.message || 'Failed to create question');
    } finally {
      setAuthorLoading(false);
    }
  };

  const handleImportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setImportLoading(true);
    try {
      const parsed = JSON.parse(importJson);
      const items = Array.isArray(parsed) ? parsed : parsed.questions || [parsed];
      await bulkImportQuestions(items);
      setIsImportModalOpen(false);
      setImportJson('');
      await loadQuestions();
    } catch (err: any) {
      alert(err.message || 'Invalid JSON format');
    } finally {
      setImportLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-[1240px] mx-auto">
      {/* Top Banner */}
      <div className="border-b border-[#E8E0D2] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="p-1.5 rounded-lg bg-[#292444] text-[#FAF6ED]">
              <BookOpen className="w-4 h-4 text-[#FF5B3D]" />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-[#FF5B3D]">
              Institutional Question Bank
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#292444] font-display">
            Assessment & Diagnostic Bank
          </h1>
          <p className="text-xs text-[#5E5875] mt-1">
            Author, review, publish, and generate verified questions with deterministic solution proofs.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            rightIcon={<Upload className="w-3.5 h-3.5" />}
            onClick={() => setIsImportModalOpen(true)}
          >
            Import JSON
          </Button>

          <Button
            variant="secondary"
            size="sm"
            rightIcon={<Plus className="w-3.5 h-3.5" />}
            onClick={() => setIsAuthorModalOpen(true)}
          >
            Author Question
          </Button>

          <Button
            variant="primary"
            size="sm"
            rightIcon={<Sparkles className="w-3.5 h-3.5" />}
            onClick={() => {
              setAiResult(null);
              setAiError(null);
              setIsAiModalOpen(true);
            }}
            className="font-bold shadow-warm"
          >
            Generate with AI
          </Button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card className="p-4 bg-white border border-[#E8E0D2] rounded-xl">
          <span className="text-[11px] font-bold text-[#8E879E] uppercase tracking-wider block mb-1">
            Total Questions
          </span>
          <span className="text-xl font-bold text-[#292444] font-display">{total} items</span>
        </Card>

        <Card className="p-4 bg-white border border-[#E8E0D2] rounded-xl">
          <span className="text-[11px] font-bold text-[#8E879E] uppercase tracking-wider block mb-1">
            Verified Published
          </span>
          <span className="text-xl font-bold text-emerald-700 font-display">
            {questions.filter((q) => q.status === 'PUBLISHED').length} in view
          </span>
        </Card>

        <Card className="p-4 bg-white border border-[#E8E0D2] rounded-xl">
          <span className="text-[11px] font-bold text-[#8E879E] uppercase tracking-wider block mb-1">
            Drafts Awaiting Review
          </span>
          <span className="text-xl font-bold text-[#FF5B3D] font-display">
            {questions.filter((q) => q.status === 'DRAFT').length} in view
          </span>
        </Card>

        <Card className="p-4 bg-white border border-[#E8E0D2] rounded-xl">
          <span className="text-[11px] font-bold text-[#8E879E] uppercase tracking-wider block mb-1">
            Active Filter
          </span>
          <span className="text-xs font-semibold text-[#5E5875] truncate block">
            {domainFilter || 'All Domains'} · {statusFilter || 'All Statuses'}
          </span>
        </Card>
      </div>

      {/* Search & Filters */}
      <Card className="p-4 bg-white border border-[#E8E0D2] rounded-2xl shadow-xs">
        <div className="flex flex-col md:flex-row items-center gap-4">
          <form onSubmit={handleSearchSubmit} className="flex-1 w-full relative">
            <Search className="w-4 h-4 text-[#8E879E] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by question title or problem content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-[#FAF6ED]/50 border border-[#E8E0D2] rounded-xl text-xs text-[#292444] focus:outline-none focus:border-[#FF5B3D]"
            />
          </form>

          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            <select
              value={domainFilter}
              onChange={(e) => {
                setDomainFilter(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444] focus:outline-none focus:border-[#FF5B3D]"
            >
              <option value="">All Domains</option>
              <option value="QUANT">Quantitative Aptitude</option>
              <option value="LOGICAL">Logical Reasoning</option>
              <option value="VERBAL">Verbal Ability</option>
              <option value="PROGRAMMING">Programming</option>
              <option value="SQL">SQL & Database</option>
              <option value="TECH_CORE">Core Technical</option>
              <option value="HR">HR & Behavioral</option>
            </select>

            <select
              value={difficultyFilter}
              onChange={(e) => {
                setDifficultyFilter(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444] focus:outline-none focus:border-[#FF5B3D]"
            >
              <option value="">All Difficulties</option>
              <option value="EASY">Easy</option>
              <option value="MEDIUM">Medium</option>
              <option value="HARD">Hard</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444] focus:outline-none focus:border-[#FF5B3D]"
            >
              <option value="">All Statuses</option>
              <option value="PUBLISHED">Published</option>
              <option value="DRAFT">Draft</option>
              <option value="ARCHIVED">Archived</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Question Table */}
      {loading ? (
        <div className="p-12 text-center">
          <RefreshCw className="w-8 h-8 text-[#FF5B3D] animate-spin mx-auto mb-3" />
          <p className="text-xs text-[#5E5875]">Querying question catalog...</p>
        </div>
      ) : questions.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-[#E8E0D2] rounded-2xl bg-white">
          <BookOpen className="w-10 h-10 text-[#8E879E] mx-auto mb-3" />
          <h3 className="text-base font-bold text-[#292444]">No questions match filters</h3>
          <p className="text-xs text-[#5E5875] mt-1 mb-4">Try clearing filters or generate new questions using Gemini AI.</p>
          <Button variant="secondary" size="sm" onClick={() => setIsAiModalOpen(true)}>
            Open AI Generator
          </Button>
        </div>
      ) : (
        <div className="border border-[#E8E0D2] bg-white rounded-2xl overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#FAF6ED]/70 border-b border-[#E8E0D2] text-[#8E879E] uppercase font-bold text-[10px]">
                <tr>
                  <th className="py-3 px-4">Title & Question</th>
                  <th className="py-3 px-4">Domain / Skill</th>
                  <th className="py-3 px-4">Difficulty</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Accuracy</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E8E0D2]/60">
                {questions.map((q) => (
                  <tr key={q.id} className="hover:bg-[#FAF6ED]/40 transition-colors">
                    <td className="py-3.5 px-4 max-w-sm">
                      <div className="font-bold text-[#292444] line-clamp-1">{q.title}</div>
                      <div className="text-[#5E5875] text-[11px] line-clamp-1 mt-0.5">{q.content}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-semibold text-[#292444]">{q.skill_name || 'General'}</span>
                      <span className="text-[10px] text-[#8E879E] block">{q.domain}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <Badge variant="neutral" className="text-[10px]">
                        {q.difficulty}
                      </Badge>
                    </td>
                    <td className="py-3.5 px-4">
                      <Badge
                        variant={
                          q.status === 'PUBLISHED'
                            ? 'success'
                            : q.status === 'DRAFT'
                            ? 'coral'
                            : 'neutral'
                        }
                        className="text-[10px] font-bold"
                      >
                        {q.status}
                      </Badge>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="text-emerald-700 font-semibold">{q.accuracy_rate}%</span>
                      <span className="text-[10px] text-[#8E879E] block">({q.attempts_count} att.)</span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedQuestion(q)}
                          className="text-xs p-1.5"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </Button>

                        <Button
                          variant={q.status === 'PUBLISHED' ? 'outline' : 'secondary'}
                          size="sm"
                          onClick={() => handleToggleStatus(q.id, q.status)}
                          className="text-xs py-1 px-2.5"
                        >
                          {q.status === 'PUBLISHED' ? 'Archive' : 'Publish'}
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="p-4 border-t border-[#E8E0D2] flex items-center justify-between bg-[#FAF6ED]/30 text-xs">
            <span className="text-[#5E5875]">
              Showing {questions.length} of {total} questions
            </span>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </Button>
              <span className="font-semibold text-[#292444] px-2">Page {page}</span>
              <Button
                variant="secondary"
                size="sm"
                disabled={page * pageSize >= total}
                onClick={() => setPage((p) => p + 1)}
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Question Preview Drawer / Modal */}
      {selectedQuestion && (
        <div className="fixed inset-0 z-50 bg-[#292444]/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-[#E8E0D2] shadow-warm-lg max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden animate-fadeIn">
            <div className="p-6 border-b border-[#E8E0D2] flex items-center justify-between bg-[#FAF6ED]/50">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="neutral" className="text-[10px]">
                    {selectedQuestion.domain}
                  </Badge>
                  <Badge variant="neutral" className="text-[10px]">
                    {selectedQuestion.difficulty}
                  </Badge>
                  <Badge
                    variant={selectedQuestion.status === 'PUBLISHED' ? 'success' : 'coral'}
                    className="text-[10px]"
                  >
                    {selectedQuestion.status}
                  </Badge>
                </div>
                <h3 className="text-lg font-bold text-[#292444] font-display">{selectedQuestion.title}</h3>
              </div>
              <button
                onClick={() => setSelectedQuestion(null)}
                className="w-8 h-8 rounded-full bg-white border border-[#E8E0D2] text-[#5E5875] hover:text-[#292444] flex items-center justify-center"
              >
                ✕
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-5 flex-1">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-[#8E879E] block mb-1">
                  Problem Statement
                </span>
                <p className="text-sm text-[#292444] leading-relaxed bg-[#FAF6ED]/40 p-4 rounded-xl border border-[#E8E0D2]/60">
                  {selectedQuestion.content}
                </p>
              </div>

              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-[#8E879E] block mb-2">
                  Answer Options & Distractor Pedagogical Feedback
                </span>
                <div className="space-y-2">
                  {selectedQuestion.options.map((opt, i) => (
                    <div
                      key={i}
                      className={`p-3 rounded-xl border text-xs ${
                        opt.is_correct
                          ? 'bg-emerald-50 border-emerald-300 text-emerald-950 font-semibold'
                          : 'bg-white border-[#E8E0D2] text-[#5E5875]'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span>{opt.option_text}</span>
                        {opt.is_correct && (
                          <span className="text-[10px] font-bold text-emerald-700 uppercase">
                            ✓ Correct Answer
                          </span>
                        )}
                      </div>
                      {opt.feedback && (
                        <p className="text-[11px] text-[#8E879E] mt-1 pt-1 border-t border-black/5">
                          Feedback: {opt.feedback}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {selectedQuestion.explanation && (
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-[#8E879E] block mb-1">
                    Step-by-Step Proof / Explanation
                  </span>
                  <div className="p-4 bg-[#FAF6ED] rounded-xl border border-[#E8E0D2] text-xs text-[#292444] whitespace-pre-line leading-relaxed">
                    {selectedQuestion.explanation}
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-[#E8E0D2] flex items-center justify-between bg-[#FAF6ED]/30">
              <Button
                variant={selectedQuestion.status === 'PUBLISHED' ? 'outline' : 'primary'}
                size="sm"
                onClick={() => handleToggleStatus(selectedQuestion.id, selectedQuestion.status)}
                className="font-bold shadow-warm"
              >
                {selectedQuestion.status === 'PUBLISHED' ? 'Archive Question' : 'Approve & Publish'}
              </Button>
              <Button variant="secondary" size="sm" onClick={() => setSelectedQuestion(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* AI Question Generation Modal */}
      {isAiModalOpen && (
        <div className="fixed inset-0 z-50 bg-[#292444]/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-[#E8E0D2] shadow-warm-lg max-w-xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-fadeIn">
            <div className="p-6 border-b border-[#E8E0D2] flex items-center justify-between bg-[#FAF6ED]/50">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-[#292444] text-[#FAF6ED]">
                  <Sparkles className="w-5 h-5 text-[#FF5B3D]" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-[#292444] font-display">AI Question Generator</h3>
                  <p className="text-xs text-[#5E5875]">Powered by Google Gemini with Distractor Validation</p>
                </div>
              </div>
              <button
                onClick={() => setIsAiModalOpen(false)}
                className="w-8 h-8 rounded-full bg-white border border-[#E8E0D2] text-[#5E5875] hover:text-[#292444] flex items-center justify-center"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleTriggerAiGeneration} className="p-6 overflow-y-auto space-y-4 flex-1">
              {aiError && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{aiError}</span>
                </div>
              )}

              {aiResult && (
                <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900 space-y-2">
                  <div className="font-bold flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    Generated {aiResult.questions_generated} Draft Questions Successfully!
                  </div>
                  <p className="text-[11px] text-emerald-700">{aiResult.notice}</p>
                </div>
              )}

              <div>
                <label className="text-xs font-bold text-[#292444] block mb-1">Subject Domain</label>
                <select
                  value={aiDomain}
                  onChange={(e) => setAiDomain(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444]"
                >
                  <option value="QUANT">Quantitative Aptitude</option>
                  <option value="LOGICAL">Logical Reasoning</option>
                  <option value="VERBAL">Verbal Ability</option>
                  <option value="PROGRAMMING">Programming</option>
                  <option value="SQL">SQL & Database</option>
                  <option value="TECH_CORE">Core Technical</option>
                  <option value="HR">HR & Behavioral</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-bold text-[#292444] block mb-1">Topic Name</label>
                <input
                  type="text"
                  placeholder="e.g. Ratio and Proportion, Binary Search Trees, DBMS Normalization"
                  value={aiTopic}
                  onChange={(e) => setAiTopic(e.target.value)}
                  required
                  className="w-full px-3.5 py-2.5 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444]"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-bold text-[#292444] block mb-1">Difficulty</label>
                  <select
                    value={aiDifficulty}
                    onChange={(e) => setAiDifficulty(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444]"
                  >
                    <option value="EASY">Easy</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HARD">Hard</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-bold text-[#292444] block mb-1">Number of Questions</label>
                  <input
                    type="number"
                    min={1}
                    max={10}
                    value={aiCount}
                    onChange={(e) => setAiCount(parseInt(e.target.value) || 3)}
                    className="w-full px-3.5 py-2.5 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444]"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-[#292444] block mb-1">
                  Learning Objectives (Optional)
                </label>
                <textarea
                  rows={2}
                  placeholder="Specific concepts, formulas, or pitfalls to test..."
                  value={aiObjectives}
                  onChange={(e) => setAiObjectives(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444]"
                />
              </div>

              <div className="p-3 bg-[#FAF6ED] rounded-xl text-[11px] text-[#5E5875] border border-[#E8E0D2]/60">
                🔒 <strong>Zero PII Policy:</strong> Only topic keywords and pedagogical constraints are sent. Generated questions are saved with status <strong>DRAFT</strong> for staff review.
              </div>

              <div className="pt-4 border-t border-[#E8E0D2] flex items-center justify-end gap-3">
                <Button variant="secondary" size="sm" onClick={() => setIsAiModalOpen(false)}>
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  disabled={aiLoading}
                  rightIcon={aiLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                  className="font-bold shadow-warm"
                >
                  {aiLoading ? 'Synthesizing with Gemini...' : 'Generate Draft Questions'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Manual Authoring Modal */}
      {isAuthorModalOpen && (
        <div className="fixed inset-0 z-50 bg-[#292444]/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-[#E8E0D2] shadow-warm-lg max-w-xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-fadeIn">
            <div className="p-6 border-b border-[#E8E0D2] flex items-center justify-between bg-[#FAF6ED]/50">
              <h3 className="text-lg font-bold text-[#292444] font-display">Author New Question</h3>
              <button
                onClick={() => setIsAuthorModalOpen(false)}
                className="w-8 h-8 rounded-full bg-white border border-[#E8E0D2] text-[#5E5875] hover:text-[#292444] flex items-center justify-center"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateManualQuestion} className="p-6 overflow-y-auto space-y-4 flex-1">
              <div>
                <label className="text-xs font-bold text-[#292444] block mb-1">Title</label>
                <input
                  type="text"
                  placeholder="e.g. Percentage: Successive Increase Problem"
                  value={manualTitle}
                  onChange={(e) => setManualTitle(e.target.value)}
                  required
                  className="w-full px-3.5 py-2.5 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444]"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-[#292444] block mb-1">Problem Statement</label>
                <textarea
                  rows={3}
                  placeholder="Complete question text..."
                  value={manualContent}
                  onChange={(e) => setManualContent(e.target.value)}
                  required
                  className="w-full px-3.5 py-2.5 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444]"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-bold text-[#292444] block mb-1">Domain</label>
                  <select
                    value={manualDomain}
                    onChange={(e) => setManualDomain(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444]"
                  >
                    <option value="QUANT">Quantitative Aptitude</option>
                    <option value="LOGICAL">Logical Reasoning</option>
                    <option value="VERBAL">Verbal Ability</option>
                    <option value="PROGRAMMING">Programming</option>
                    <option value="SQL">SQL & Database</option>
                    <option value="TECH_CORE">Core Technical</option>
                    <option value="HR">HR & Behavioral</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-bold text-[#292444] block mb-1">Difficulty</label>
                  <select
                    value={manualDifficulty}
                    onChange={(e) => setManualDifficulty(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444]"
                  >
                    <option value="EASY">Easy</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HARD">Hard</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-[#292444] block mb-2">Options (Select 1 Correct)</label>
                <div className="space-y-2">
                  {manualOptions.map((opt, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <input
                        type="radio"
                        name="correct_opt"
                        checked={opt.is_correct}
                        onChange={() => {
                          const updated = manualOptions.map((o, idx) => ({
                            ...o,
                            is_correct: idx === i,
                          }));
                          setManualOptions(updated);
                        }}
                      />
                      <input
                        type="text"
                        placeholder={`Option ${i + 1}`}
                        value={opt.option_text}
                        onChange={(e) => {
                          const updated = [...manualOptions];
                          updated[i].option_text = e.target.value;
                          setManualOptions(updated);
                        }}
                        required
                        className="flex-1 px-3 py-1.5 bg-white border border-[#E8E0D2] rounded-lg text-xs"
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-[#292444] block mb-1">Official Solution Proof</label>
                <textarea
                  rows={3}
                  placeholder="Step-by-step mathematical or logical proof..."
                  value={manualExplanation}
                  onChange={(e) => setManualExplanation(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-white border border-[#E8E0D2] rounded-xl text-xs text-[#292444]"
                />
              </div>

              <div className="pt-4 border-t border-[#E8E0D2] flex items-center justify-end gap-3">
                <Button variant="secondary" size="sm" onClick={() => setIsAuthorModalOpen(false)}>
                  Cancel
                </Button>
                <Button variant="primary" size="sm" disabled={authorLoading} className="font-bold shadow-warm">
                  {authorLoading ? 'Saving...' : 'Publish Question'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Bulk Import Modal */}
      {isImportModalOpen && (
        <div className="fixed inset-0 z-50 bg-[#292444]/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-[#E8E0D2] shadow-warm-lg max-w-xl w-full flex flex-col overflow-hidden animate-fadeIn">
            <div className="p-6 border-b border-[#E8E0D2] flex items-center justify-between bg-[#FAF6ED]/50">
              <h3 className="text-lg font-bold text-[#292444] font-display">Bulk Import Questions</h3>
              <button
                onClick={() => setIsImportModalOpen(false)}
                className="w-8 h-8 rounded-full bg-white border border-[#E8E0D2] text-[#5E5875] hover:text-[#292444] flex items-center justify-center"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleImportSubmit} className="p-6 space-y-4">
              <p className="text-xs text-[#5E5875]">
                Paste JSON array of questions with <code>title</code>, <code>content</code>, <code>options</code>, and <code>explanation</code>.
              </p>
              <textarea
                rows={10}
                placeholder={`[\n  {\n    "title": "Sample Problem",\n    "content": "What is 10 + 10?",\n    "domain": "QUANT",\n    "options": [\n      {"option_text": "20", "is_correct": true},\n      {"option_text": "30", "is_correct": false}\n    ]\n  }\n]`}
                value={importJson}
                onChange={(e) => setImportJson(e.target.value)}
                required
                className="w-full p-3 font-mono text-xs bg-[#FAF6ED]/30 border border-[#E8E0D2] rounded-xl text-[#292444]"
              />

              <div className="flex items-center justify-end gap-3">
                <Button variant="secondary" size="sm" onClick={() => setIsImportModalOpen(false)}>
                  Cancel
                </Button>
                <Button variant="primary" size="sm" disabled={importLoading} className="font-bold shadow-warm">
                  {importLoading ? 'Importing...' : 'Upload & Validate'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
