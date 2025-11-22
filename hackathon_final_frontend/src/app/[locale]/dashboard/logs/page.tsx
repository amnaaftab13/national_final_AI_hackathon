
"use client"

import React, { useState, useEffect } from 'react';
import { Activity, Clock, Zap, ArrowRight, CheckCircle, AlertCircle, TrendingUp, Filter, Search, RefreshCw, ChevronDown, ChevronUp, Users, Brain, Handshake } from 'lucide-react';
import { useTranslations, useLocale } from "next-intl";

// ============================================
// 🔧 TypeScript Interfaces
// ============================================

interface MCPCall {
  server: string;
  action: string | null;
  tools_found: number;
  duration: number;
}

interface LLMDecision {
  tool: string;
  agent: string | null;
  model: string | null;
  arguments?: string | null; 
  duration: number;
  tokens: {
    total: number;
    input: number;
    output: number;
  };
  reasoning: string | null;
}

interface LogHandoff {
  from: string;
  to: string;
}

interface FinalOutput {
  agent: string | null;
  model: string | null;
  length: number;
  preview: string | null;
}

interface TraceSummary {
  metrics: {
    agents: number;
    tools: number;
    llm_calls: number;
    mcp_calls: number;
    negotiations: number;
    handoffs: number;
    autonomous_decisions: number;
  };
  tokens: {
    total: number;
    input: number;
    output: number;
  };
  duration: number;
  final_output: string | null;
}

interface LogTrace {
  trace_id: string;
  timestamp: string;
  user_message: string | null;
  mcp_calls: MCPCall[];
  llm_decisions: LLMDecision[];
  handoffs: LogHandoff[];
  final_outputs: FinalOutput[];
  summary: TraceSummary;
}

interface ApiResponse {
  status: 'success' | 'error';
  data?: {
    header: {
      title: string;
      requirements: string[];
      started: string;
    };
    traces: LogTrace[];
    total_traces: number;
  };
  message?: string;
  generated_at?: string;
}

const BASE_URL = process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL;

// ============================================
// 🎨 Main Component
// ============================================

export default function HackathonLogsViewer() {
  const t = useTranslations("logsPage");
  const locale = useLocale();

  const [logs, setLogs] = useState<LogTrace[]>([]);
  const [headerInfo, setHeaderInfo] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [autoRefresh, setAutoRefresh] = useState<boolean>(false);
  const [expandedTraces, setExpandedTraces] = useState<Set<string>>(new Set());
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatDateTime = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  };

  const fetchLogs = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${BASE_URL}/admin/agent-logs/formatted`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: ApiResponse = await response.json();

      if (result.status === 'success' && result.data) {
        setLogs(result.data.traces);
        setHeaderInfo(result.data.header);
      } else {
        throw new Error(result.message || 'Failed to load logs');
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(`Failed to load logs: ${errorMessage}`);
      console.error('Error fetching logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchLogs, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getAgentColor = (agent: string | null): string => {
    if (!agent) return 'bg-gray-500';

    const colors: Record<string, string> = {
      'Powerful AI Assistant': 'bg-fuchsia-600',
      'SalesAgent': 'bg-blue-600',
      'FinanceAgent': 'bg-teal-600',
      'InventoryAgent': 'bg-orange-600',
      'AnalyticsAgent': 'bg-pink-600',
      'BuyingAgent': 'bg-yellow-600',
      'MarketingAgent': 'bg-red-600',
      'InsightAgent': 'bg-indigo-600',
      'BusinessDecisionAgent': 'bg-cyan-600'
    };
    return colors[agent] || 'bg-gray-500';
  };

  const toggleTraceExpansion = (traceId: string): void => {
    setExpandedTraces(prev => {
      const newSet = new Set(prev);
      if (newSet.has(traceId)) {
        newSet.delete(traceId);
      } else {
        newSet.add(traceId);
      }
      return newSet;
    });
  };

  const allAgents: string[] = [...new Set(
    logs.flatMap(log =>
      log.llm_decisions
        .map(d => d.agent)
        .filter((a): a is string => a !== null)
    )
  )];

  const filteredLogs = logs.filter(log => {
    const traceAgents = log.llm_decisions.map(d => d.agent).filter(a => a !== null);
    if (filter !== 'all' && !traceAgents.includes(filter)) return false;
    if (searchTerm && log.user_message && !log.user_message.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  const CARD_BG = 'bg-black/70 border-gray-800';
  const PRIMARY_COLOR = 'text-cyan-400';
  const SECONDARY_COLOR = 'text-fuchsia-400';
  const ACCENT_COLOR_BG = 'bg-cyan-900/40 border-cyan-500';
  const ACCENT_COLOR_HOVER = 'hover:ring-2 hover:ring-fuchsia-500';
  const BUTTON_PRIMARY = 'bg-fuchsia-600 hover:bg-fuchsia-700 text-white';
  const BUTTON_SECONDARY = 'bg-gray-800 hover:bg-gray-700 text-white';
  const AUTO_REFRESH_BG = 'bg-teal-600 hover:bg-teal-700';

  if (loading && logs.length === 0) {
    return (
      <div className="fixed inset-0 z-[100] flex items-center justify-center overflow-hidden bg-black">
        <video
          autoPlay
          loop
          muted
          src="/loader.mp4"
          className="absolute inset-0 w-full h-full object-cover brightness-110"
        />
        <div className="absolute text-cyan-300 text-xl sm:text-2xl font-bold">
          {t('loading_logs')}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#020202] flex items-center justify-center p-4">
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-6 max-w-md shadow-[0_0_15px_#ff0000]">
          <div className="flex items-center gap-3 text-red-300 mb-3">
            <AlertCircle className="w-6 h-6" />
            <h2 className="text-xl font-bold">{t('error_loading')}</h2>
          </div>
          <p className="text-red-200 mb-4">{error}</p>
          <p className="text-sm text-red-300 mb-4">
            {t('backend_warning')} <code className="bg-red-950 px-2 py-1 rounded">http://localhost:8000</code>
          </p>
          <button
            onClick={fetchLogs}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            {t('retry_button')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#020202] p-3 sm:p-4 md:p-6 lg:p-8 text-white">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6 md:mb-8">
          <h1 className="text-3xl md:text-4xl font-extrabold text-cyan-300 drop-shadow-[0_0_12px_#00fff2] sm:drop-shadow-[0_0_18px_#00fff2] mb-2">
            {t('header_title')}
          </h1>
          <p className="text-fuchsia-300 text-base pb-2 pt-4 md:text-lg drop-shadow-[0_0_8px_#ff00f2]">
            {t('header_subtitle')}
          </p>

          <div className="flex items-center justify-center gap-2 mt-3">
            <Clock className="w-4 h-4 text-cyan-400 animate-pulse" />
            <span className="text-gray-500 text-sm whitespace-pre-wrap font-mono">
              {t('started')}: {formatDateTime(currentTime)}
            </span>
          </div>
        </div>

        {/* Filters & Controls */}
        <div className={`rounded-xl p-4 md:p-6 mb-6 ${CARD_BG} border border-fuchsia-500/30 shadow-[0_0_15px_#a855f7]`}>
          <div className="flex flex-col gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-fuchsia-400" />
                <input
                  type="text"
                  placeholder={t('search_placeholder')}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-gray-800 text-white rounded-lg focus:ring-2 focus:ring-cyan-500 outline-none text-sm md:text-base border border-gray-700"
                />
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-2">
              <div className="flex items-center gap-2 flex-1">
                <Filter className="w-5 h-5 text-cyan-400" />
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="flex-1 px-4 py-3 bg-gray-800 text-white rounded-lg focus:ring-2 focus:ring-cyan-500 outline-none text-sm border border-gray-700"
                >
                  <option value="all">{t('all_agents')}</option>
                  {allAgents.map(agent => (
                    <option key={agent} value={agent}>{agent}</option>
                  ))}
                </select>
              </div>

              <button
                onClick={fetchLogs}
                disabled={loading}
                className={`px-4 py-3 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50 ${BUTTON_PRIMARY}`}
              >
                <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">{t('refresh_button')}</span>
              </button>

              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`px-4 py-3 rounded-lg transition-colors flex items-center justify-center gap-2 ${autoRefresh ? AUTO_REFRESH_BG : BUTTON_SECONDARY
                  } text-white`}
              >
                <Activity className="w-5 h-5" />
                <span className="hidden sm:inline">{autoRefresh ? t('auto_on') : t('auto_off')}</span>
              </button>
            </div>
          </div>

          <div className="mt-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs md:text-sm">
            <div className="text-gray-400">
              {t('showing_traces')} {filteredLogs.length} {t('of_traces')} {logs.length} {t('traces')}
            </div>
            {autoRefresh && (
              <div className="text-teal-400 flex items-center gap-2">
                <div className="w-2 h-2 bg-teal-400 rounded-full animate-pulse"></div>
                {t('auto_refresh_status')}
              </div>
            )}
          </div>
        </div>

        {/* Logs List */}
        <div className="space-y-6">
          {filteredLogs.length === 0 ? (
            <div className={`rounded-xl p-12 text-center ${CARD_BG} border border-cyan-500/30`}>
              <AlertCircle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">{t('no_logs_title')}</h3>
              <p className="text-gray-400">{t('no_logs_desc')}</p>
            </div>
          ) : (
            filteredLogs.map((log) => {
              const isExpanded = expandedTraces.has(log.trace_id);
              const uniqueAgents = [...new Set(log.llm_decisions.map(d => d.agent).filter(a => a !== null))];

              return (
                <div
                  key={log.trace_id}
                  className={`rounded-xl overflow-hidden ${CARD_BG} border border-gray-700 ${ACCENT_COLOR_HOVER} transition-all duration-300 shadow-[0_0_8px_rgba(255,0,255,0.1)]`}
                >
                  {/* Trace Header */}
                  <div
                    className="p-4 md:p-6 cursor-pointer hover:bg-gray-900/50"
                    onClick={() => toggleTraceExpansion(log.trace_id)}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2 flex-wrap">
                          <CheckCircle className="w-5 h-5 md:w-6 md:h-6 text-cyan-400 flex-shrink-0 drop-shadow-[0_0_4px_#00fff2]" />
                          <h3 className="text-lg md:text-xl font-bold text-white break-all">
                            {t('trace_id')}: <span className={PRIMARY_COLOR}>{log.trace_id.substring(0, 8)}...</span>
                          </h3>
                          <span className={`px-3 py-1 ${ACCENT_COLOR_BG} text-cyan-300 rounded-full text-xs md:text-sm font-semibold`}>
                            {t('completed_status')}
                          </span>
                          {isExpanded ? (
                            <ChevronUp className="w-5 h-5 text-fuchsia-400 ml-auto" />
                          ) : (
                            <ChevronDown className="w-5 h-5 text-fuchsia-400 ml-auto" />
                          )}
                        </div>

                        {log.user_message && (
                          <div className="bg-gray-900 rounded-lg p-3 mb-3 border border-fuchsia-500/20">
                            <div className="text-fuchsia-400 text-xs font-semibold mb-1">📥 {t('user_query')}</div>
                            <div className="text-white text-sm md:text-base break-words">{log.user_message}</div>
                          </div>
                        )}

                        <div className="flex flex-wrap gap-2">
                          {uniqueAgents.map((agent, idx) => (
                            <span key={idx} className={`${getAgentColor(agent)} text-white px-3 py-2 rounded-full text-xs font-semibold shadow-md`}>
                              {agent}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="flex items-center gap-4 ml-4">
                        {log.summary.duration > 0 && (
                          <div className="text-right hidden md:block">
                            <div className={`font-semibold flex items-center gap-1 ${PRIMARY_COLOR}`}>
                              <Clock className="w-4 h-4" />
                              {log.summary.duration}s
                            </div>
                            <div className="text-gray-500 text-xs">{t('duration')}</div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="border-t border-gray-800 p-4 md:p-6 bg-black/50">
                      {/* LLM Decisions */}
                      {log.llm_decisions && log.llm_decisions.length > 0 && (
                        <div className="mb-6">
                          <h4 className={`text-lg font-bold text-white mb-4 flex items-center gap-2 ${SECONDARY_COLOR}`}>
                            <Zap className="w-5 h-5 drop-shadow-[0_0_4px_#ff00f2]" />
                            {t('llm_tool_calls')}
                          </h4>

                          <div className="space-y-4">
                            {log.llm_decisions.map((decision, idx) => (
                              <div key={idx} className="bg-gray-900 rounded-lg p-4 relative border border-gray-700">
                                {idx < log.llm_decisions.length - 1 && (
                                  <div className="absolute left-6 top-full w-0.5 h-4 bg-cyan-500" />
                                )}

                                <div className="flex items-start justify-between mb-3">
                                  <div className="flex items-center gap-3 flex-1 min-w-0">
                                    <div className={`w-10 h-10 ${getAgentColor(decision.agent)} rounded-full flex items-center justify-center text-white font-bold flex-shrink-0 shadow-lg`}>
                                      {idx + 1}
                                    </div>
                                    <div className="min-w-0">
                                      <div className="text-white font-bold text-sm md:text-base break-words">
                                        {decision.agent || t('unknown_agent')}
                                      </div>
                                      <div className={`${PRIMARY_COLOR} text-xs md:text-sm break-words`}>
                                        {t('tool_used')}: {decision.tool}
                                      </div>
                                      {decision.model && (
                                        <div className="text-gray-500 text-xs">
                                          {t('model')}: {decision.model}
                                        </div>
                                      )}
                                    </div>
                                  </div>

                                  <div className="text-right ml-2 flex-shrink-0">
                                    {decision.duration > 0 && (
                                      <div className="text-cyan-400 text-sm font-semibold flex items-center gap-1">
                                        <Clock className="w-4 h-4" />
                                        {decision.duration}s
                                      </div>
                                    )}
                                    {decision.tokens.total > 0 && (
                                      <div className="text-gray-500 text-xs">
                                        {decision.tokens.total} {t('tokens')}
                                      </div>
                                    )}
                                  </div>
                                </div>

                                {decision.arguments && decision.arguments !== '{}' && (
                                  <div className="bg-black/40 rounded p-3 mt-3 border border-cyan-500/20 font-mono">
                                    <div className="text-cyan-500 text-xs font-semibold mb-2 uppercase tracking-wider">
                                      🔧 Tool Arguments
                                    </div>
                                    <pre className="text-cyan-100 text-xs overflow-x-auto whitespace-pre-wrap break-all">
                                      {decision.arguments}
                                    </pre>
                                  </div>
                                )}

                                {decision.reasoning && (
                                  <div className="bg-gray-800 rounded p-3 mt-3 border border-fuchsia-500/30">
                                    <div className="text-fuchsia-400 text-xs font-semibold mb-2">
                                      🧠 {t('reasoning')}
                                    </div>
                                    <div className="text-gray-200 text-xs md:text-sm whitespace-pre-wrap">
                                      {decision.reasoning}
                                    </div>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Handoffs */}
                      {log.handoffs && log.handoffs.length > 0 && (
                        <div className="mb-6">
                          <h4 className={`text-lg font-bold text-white mb-4 flex items-center gap-2 ${PRIMARY_COLOR}`}>
                            <ArrowRight className="w-5 h-5 drop-shadow-[0_0_4px_#00fff2]" />
                            {t('agent_handoffs_title')}
                          </h4>

                          <div className="space-y-2">
                            {log.handoffs.map((handoff, idx) => (
                              <div key={idx} className={`bg-cyan-900/30 border border-cyan-500 rounded-lg p-3 flex items-center gap-3 shadow-md`}>
                                <span className="text-white font-semibold text-sm">{handoff.from}</span>
                                <ArrowRight className="w-5 h-5 text-cyan-400" />
                                <span className="text-white font-semibold text-sm">{handoff.to}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Metrics */}
                      {log.summary && (
                        <div className="mb-6">
                          <h4 className={`text-lg font-bold text-white mb-4 flex items-center gap-2 ${SECONDARY_COLOR}`}>
                            <TrendingUp className="w-5 h-5 drop-shadow-[0_0_4px_#ff00f2]" />
                            {t('execution_metrics')}
                          </h4>

                          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                              <div className="text-gray-400 text-xs mb-1">{t('llm_calls')}</div>
                              <div className="text-white text-lg md:text-xl font-bold">{log.summary.metrics.llm_calls ?? 0}</div>
                            </div>
                            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                              <div className="text-gray-400 text-xs mb-1">{t('handoffs_summary')}</div>
                              <div className="text-white text-lg md:text-xl font-bold">{log.summary.metrics.handoffs ?? 0}</div>
                            </div>
                            <div className="bg-gray-800 rounded-lg p-3 border border-fuchsia-500/30">
                              <div className="text-fuchsia-400 text-xs mb-1 flex items-center gap-1">
                                <Handshake className='w-3 h-3' /> {t('negotiations')}
                              </div>
                              <div className="text-fuchsia-400 text-lg md:text-xl font-bold">{log.summary.metrics.negotiations ?? 0}</div>
                            </div>
                            <div className="bg-gray-800 rounded-lg p-3 border border-cyan-500/30">
                              <div className="text-cyan-400 text-xs mb-1 flex items-center gap-1">
                                <Brain className='w-3 h-3' /> {t('autonomous_decisions')}
                              </div>
                              <div className="text-cyan-400 text-lg md:text-xl font-bold">{log.summary.metrics.autonomous_decisions ?? 0}</div>
                            </div>
                            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                              <div className="text-gray-400 text-xs mb-1">{t('total_tokens')}</div>
                              <div className="text-white text-lg md:text-xl font-bold">{log.summary.tokens.total ?? 0}</div>
                            </div>
                            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                              <div className="text-gray-400 text-xs mb-1">{t('duration')}</div>
                              <div className="text-white text-lg md:text-xl font-bold">{log.summary.duration ?? 0}s</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* MCP Orchestration */}
                      {log.mcp_calls && log.mcp_calls.length > 0 && (
                        <div className="mb-6">
                          <h4 className={`text-lg font-bold text-white mb-4 flex items-center gap-2 ${SECONDARY_COLOR}`}>
                            <Activity className="w-5 h-5 drop-shadow-[0_0_4px_#ff00f2]" />
                            {t('mcp_orchestration')}
                          </h4>

                          <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
                            {Object.entries(
                              log.mcp_calls.reduce((acc, call) => {
                                const server = call.server || t('unknown_server');
                                acc[server] = (acc[server] || 0) + 1;
                                return acc;
                              }, {} as Record<string, number>)
                            ).map(([server, count], idx) => (
                              <div key={idx} className="flex items-center justify-between py-2 border-b border-gray-800 last:border-b-0">
                                <span className="text-white text-sm">• {server}</span>
                                <span className="text-cyan-400 text-sm font-semibold">{count} {t('calls_suffix')}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Autonomous Decisions */}
                      {log.summary.metrics.autonomous_decisions > 0 && (
                        <div className="mb-6">
                          <h4 className={`text-lg font-bold text-white mb-4 flex items-center gap-2 `}>
                            <Brain className="w-5 h-5 drop-shadow-[0_0_4px_#00fff2]" />
                            {t('autonomous_title')}
                          </h4>

                          <div className="bg-cyan-900/20 rounded-lg p-4 border border-cyan-500/30">
                            {log.llm_decisions
                              .filter(d => d.tool && (d.tool.includes('transfer') || d.reasoning))
                              .map((decision, idx) => (
                                <div key={idx} className="py-2 border-b border-cyan-800/30 last:border-b-0">
                                  <div className="text-cyan-300 text-sm flex items-start gap-2">
                                    <span className="text-cyan-500">•</span>
                                    <span>{t('agent_chose')} <span className="font-semibold">{decision.tool}</span></span>
                                  </div>
                                  {decision.agent && decision.tool.includes('transfer') && (
                                    <div className="text-cyan-300 text-sm flex items-start gap-2 mt-1">
                                      <span className="text-cyan-500">•</span>
                                      <span>{t('autonomous_handoff')} {decision.agent} → {decision.tool.replace('transfer_to_', '').replace(/_/g, ' ')}</span>
                                    </div>
                                  )}
                                </div>
                              ))}
                          </div>
                        </div>
                      )}

                      {/* Final Output */}
                      {(log.final_outputs && log.final_outputs.length > 0 && log.final_outputs[0].preview) || log.summary.final_output ? (
                        <div className={`rounded-lg ${CARD_BG} border p-4`}>
                          <div className="flex items-center gap-2 mb-3">
                            <CheckCircle className="text-green-400" size={20} />
                            <h4 className="font-semibold text-green-400">{t('final_user_output')}</h4>
                          </div>
                          <div className="bg-gray-900/50 rounded p-3 text-gray-300 text-sm border border-gray-700">
                            {log.final_outputs[0]?.preview || log.summary.final_output}
                          </div>
                        </div>
                      ) : null}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Footer Stats */}
        <div className={`${CARD_BG} rounded-lg border p-6`}>
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
            <TrendingUp className={PRIMARY_COLOR} size={24} />
            {t('system_stats')}
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className={`${ACCENT_COLOR_BG} rounded-lg border p-4 text-center`}>
              <div className={`text-3xl font-bold ${PRIMARY_COLOR}`}>{logs.length}</div>
              <div className="text-gray-400 text-sm mt-1">{t('total_traces_stat')}</div>
            </div>
            <div className={`${ACCENT_COLOR_BG} rounded-lg border p-4 text-center`}>
              <div className={`text-3xl font-bold ${SECONDARY_COLOR}`}>{allAgents.length}</div>
              <div className="text-gray-400 text-sm mt-1">{t('active_agents_stat')}</div>
            </div>
            <div className={`${ACCENT_COLOR_BG} rounded-lg border p-4 text-center`}>
              <div className="text-3xl font-bold text-yellow-400">
                {logs.reduce((sum, log) => sum + (log.summary.metrics.negotiations ?? 0), 0)}
              </div>
              <div className="text-gray-400 text-sm mt-1">{t('total_negotiations_stat')}</div>
            </div>
            <div className={`${ACCENT_COLOR_BG} rounded-lg border p-4 text-center`}>
              <div className="text-3xl font-bold text-green-400">
                {logs.reduce((sum, log) => sum + (log.summary.metrics.autonomous_decisions ?? 0), 0)}
              </div>
              <div className="text-gray-400 text-sm mt-1">{t('total_auto_decisions_stat')}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

