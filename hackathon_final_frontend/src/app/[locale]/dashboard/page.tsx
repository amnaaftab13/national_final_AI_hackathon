"use client";
import { useEffect, useState } from "react";
import { useTranslations, useLocale } from "next-intl";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LineChart, Line
} from "recharts";

// Type Definitions
interface FinancialSummary {
  total_revenue: number;
  total_costs: number;
  net_profit: number;
  profit_margin_percent: number;
  expected_revenue_increase_percent: number;
  expected_inventory_turnover_increase_percent: number;
}

interface AnalysisSummary {
  total_products_analyzed: number;
  low_selling_products_count: number;
  marketing_campaigns_triggered: number;
  timestamp: string;
}

interface PricingChange {
  product: string;
  current_price: number;
  suggested_price: number;
  discount_percent: number;
  reason: string;
}

interface RecommendationDetails {
  product?: string;
  products?: string[];
  current_stock?: number;
  days_unsold?: number;
  discount_percent?: number;
  expected_units_sold?: number;
  expected_timeframe_days?: number;
  overstocked_units?: Record<string, number>;
  hold_duration_weeks?: number;
  target_audience?: string;
  budget?: number;
  expected_reach?: number;
}

interface RecommendationImpact {
  profit_margin_before?: number;
  profit_margin_after?: number;
  expected_revenue_increase_percent?: number;
  cost_savings?: number;
  inventory_optimization?: string;
  expected_roi?: string;
  expected_conversions?: number;
}

interface TopRecommendation {
  priority: number;
  action: string;
  category: string;
  details: RecommendationDetails;
  impact: RecommendationImpact;
}

interface InventoryAction {
  product: string;
  action: string;
  reason: string;
  units_affected: number;
  hold_duration_weeks?: number;
  discount_percent?: number;
}

interface MarketingSuggestion {
  product: string;
  channel: string;
  campaign_type: string;
  budget: number;
  duration_days: number;
}

interface DashboardData {
  financial_summary: FinancialSummary;
  analysis_summary: AnalysisSummary;
  pricing_changes: PricingChange[];
  top_recommendations: TopRecommendation[];
  inventory_actions: InventoryAction[];
  marketing_suggestions: MarketingSuggestion[];
}

const BASE_URL = process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL;

export default function DashboardCenter() {
  const t = useTranslations("dashboardPage");
  const tAlerts = useTranslations("dashboardAlerts");
  const locale = useLocale();

  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await fetch(`${BASE_URL}/admin/dashboard-data`, {
          cache: "no-store",
        });

        if (!res.ok) {
          throw new Error(tAlerts("fetch_fail"));
        }

        const json = await res.json();
        setData(json.dashboard);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : tAlerts("network_error");
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [tAlerts]);

  if (loading) {
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
          {t("loading")}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black text-red-400 text-base sm:text-lg md:text-xl font-bold px-4 text-center">
        {tAlerts("fetch_fail")}<br />{error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black text-white text-base sm:text-lg md:text-xl px-4 text-center">
        {tAlerts("no_data")}
      </div>
    );
  }

  const financial = data.financial_summary;
  const analysis = data.analysis_summary;
  const pricingChanges = data.pricing_changes || [];
  const topRecommendations = data.top_recommendations || [];
  const inventoryActions = data.inventory_actions || [];
  const marketingSuggestions = data.marketing_suggestions || [];

  const pieData = [
    {
      name: t("low_selling_label"),
      value: analysis?.low_selling_products_count ?? 0,
    },
    {
      name: t("other_label"),
      value: (analysis?.total_products_analyzed ?? 0) -
        (analysis?.low_selling_products_count ?? 0),
    }
  ];

  const COLORS = ["#a855f7", "#06b6d4"];

  return (
    <div className="bg-[#020202] min-h-screen p-3 sm:p-4 md:p-6 lg:p-8 text-white">
      {/* Stats Cards Grid - Fully Responsive */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-6 mb-6 md:mb-8">
        <div className="neon-card bg-black/70 border border-cyan-500 p-4 sm:p-5 md:p-6 rounded-lg sm:rounded-xl shadow-[0_0_15px_#00f0ff] sm:shadow-[0_0_25px_#00f0ff]">
          <h2 className="text-xs sm:text-sm font-semibold opacity-70">{t("total_revenue_label")}</h2>
          <p className="text-xl sm:text-2xl md:text-3xl font-extrabold mt-1 sm:mt-2 text-cyan-300 drop-shadow-[0_0_8px_#00fff2] sm:drop-shadow-[0_0_12px_#00fff2] break-words">
            {t("currency")} {financial?.total_revenue.toLocaleString()}
          </p>
        </div>

        <div className="neon-card bg-black/70 border border-fuchsia-500 p-4 sm:p-5 md:p-6 rounded-lg sm:rounded-xl shadow-[0_0_15px_#ff00ff] sm:shadow-[0_0_25px_#ff00ff]">
          <h2 className="text-xs sm:text-sm font-semibold opacity-70">{t("low_selling_products_label")}</h2>
          <p className="text-xl sm:text-2xl md:text-3xl font-extrabold mt-1 sm:mt-2 text-fuchsia-300 drop-shadow-[0_0_8px_#ff00f2] sm:drop-shadow-[0_0_12px_#ff00f2]">
            {analysis?.low_selling_products_count}
          </p>
        </div>

        <div className="neon-card bg-black/70 border border-blue-500 p-4 sm:p-5 md:p-6 rounded-lg sm:rounded-xl shadow-[0_0_15px_#00eaff] sm:shadow-[0_0_25px_#00eaff]">
          <h2 className="text-xs sm:text-sm font-semibold opacity-70">{t("inventory_boost_label")}</h2>
          <p className="text-xl sm:text-2xl md:text-3xl font-extrabold mt-1 sm:mt-2 text-blue-300 drop-shadow-[0_0_8px_#00d0ff] sm:drop-shadow-[0_0_12px_#00d0ff]">
            {financial?.expected_inventory_turnover_increase_percent}%
          </p>
        </div>

        <div className="neon-card bg-black/70 border border-green-500 p-4 sm:p-5 md:p-6 rounded-lg sm:rounded-xl shadow-[0_0_15px_#00ff88] sm:shadow-[0_0_25px_#00ff88]">
          <h2 className="text-xs sm:text-sm font-semibold opacity-70">{t("revenue_increase_label")}</h2>
          <p className="text-xl sm:text-2xl md:text-3xl font-extrabold mt-1 sm:mt-2 text-green-300 drop-shadow-[0_0_8px_#00ff88] sm:drop-shadow-[0_0_12px_#00ff88]">
            {financial?.expected_revenue_increase_percent}%
          </p>
        </div>
      </div>

      {/* Charts Grid - Responsive Stacking */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-5 md:gap-6 mb-6 md:mb-8">
        {/* Pie Chart */}
        <div className="bg-black/70 p-4 sm:p-5 rounded-lg sm:rounded-xl border border-purple-500 shadow-[0_0_15px_#a855f7aa] sm:shadow-[0_0_22px_#a855f7aa]">
          <h3 className="text-purple-400 text-base sm:text-lg font-bold mb-3 sm:mb-4">{t("product_performance_heading")}</h3>
          <ResponsiveContainer width="100%" height={220} className="sm:hidden">
            <PieChart>
              <Pie 
                data={pieData} 
                dataKey="value" 
                nameKey="name"
                innerRadius={40} 
                outerRadius={70} 
                stroke="none"
                label={{
                  fill: "#ffffff",
                  fontSize: 11,
                  fontWeight: "bold",
                }}
              >
                {pieData.map((_: any, i: number) => (
                  <Cell 
                    key={i} 
                    fill={COLORS[i % COLORS.length]}
                    style={{
                      filter: `drop-shadow(0 0 10px ${COLORS[i % COLORS.length]})`
                    }}
                  />
                ))}
              </Pie>
              <Legend 
                wrapperStyle={{ 
                  color: "#e0e0e0",
                  fontSize: "12px"
                }} 
                iconType="circle" 
              />
            </PieChart>
          </ResponsiveContainer>
          <ResponsiveContainer width="100%" height={280} className="hidden sm:block">
            <PieChart>
              <Pie 
                data={pieData} 
                dataKey="value" 
                nameKey="name"
                innerRadius={60} 
                outerRadius={95} 
                stroke="none"
                label={{
                  fill: "#ffffff",
                  fontSize: 13,
                  fontWeight: "bold",
                }}
              >
                {pieData.map((_: any, i: number) => (
                  <Cell 
                    key={i} 
                    fill={COLORS[i % COLORS.length]}
                    style={{
                      filter: `drop-shadow(0 0 15px ${COLORS[i % COLORS.length]})`
                    }}
                  />
                ))}
              </Pie>
              <Legend 
                wrapperStyle={{ 
                  color: "#e0e0e0",
                  fontSize: "14px"
                }} 
                iconType="circle" 
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Pricing Bar Chart */}
        <div className="bg-black/70 p-4 sm:p-5 rounded-lg sm:rounded-xl border border-cyan-500 shadow-[0_0_15px_#06b6d4aa] sm:shadow-[0_0_22px_#06b6d4aa] lg:col-span-2">
          <h3 className="text-cyan-400 text-base sm:text-lg font-bold mb-3 sm:mb-4">{t("pricing_suggestions_heading")}</h3>
          <ResponsiveContainer width="100%" height={220} className="sm:hidden">
            <BarChart data={pricingChanges}>
              <defs>
                <linearGradient id="purpleGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#a855f7" stopOpacity={0.9}/>
                  <stop offset="100%" stopColor="#a855f7" stopOpacity={0.4}/>
                </linearGradient>
                <linearGradient id="cyanGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.9}/>
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.4}/>
                </linearGradient>
              </defs>
              <XAxis
                dataKey="product"
                stroke="#4b5563"
                tick={{ fill: '#9ca3af', fontSize: 9 }}
                interval={0}
                angle={-45}
                textAnchor="end"
                height={50}
              />
              <YAxis 
                stroke="#4b5563"
                tick={{fill: '#9ca3af', fontSize: 10}}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'rgba(10, 10, 10, 0.95)', 
                  border: '1px solid #a855f7',
                  borderRadius: '8px',
                  boxShadow: '0 0 20px rgba(168, 85, 247, 0.5)',
                  padding: '8px',
                  fontSize: '12px'
                }}
                cursor={{fill: 'rgba(168, 85, 247, 0.08)'}}
              />
              <Bar 
                dataKey="suggested_price" 
                fill="url(#purpleGrad)" 
                name={t("suggested_price_label")}
                radius={[6, 6, 0, 0]}
              />
              <Bar 
                dataKey="current_price" 
                fill="url(#cyanGrad)" 
                name={t("current_price_label")}
                radius={[6, 6, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
          <ResponsiveContainer width="100%" height={280} className="hidden sm:block">
            <BarChart data={pricingChanges}>
              <defs>
                <linearGradient id="purpleGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#a855f7" stopOpacity={0.9}/>
                  <stop offset="100%" stopColor="#a855f7" stopOpacity={0.4}/>
                </linearGradient>
                <linearGradient id="cyanGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.9}/>
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.4}/>
                </linearGradient>
              </defs>
              <XAxis
                dataKey="product"
                stroke="#4b5563"
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                interval={0}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis 
                stroke="#4b5563"
                tick={{fill: '#9ca3af'}}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'rgba(10, 10, 10, 0.95)', 
                  border: '1px solid #a855f7',
                  borderRadius: '12px',
                  boxShadow: '0 0 30px rgba(168, 85, 247, 0.5)',
                  padding: '12px'
                }}
                cursor={{fill: 'rgba(168, 85, 247, 0.08)'}}
              />
              <Bar 
                dataKey="suggested_price" 
                fill="url(#purpleGrad)" 
                name={t("suggested_price_label")}
                radius={[10, 10, 0, 0]}
              />
              <Bar 
                dataKey="current_price" 
                fill="url(#cyanGrad)" 
                name={t("current_price_label")}
                radius={[10, 10, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Line Chart - Responsive Height */}
      <div className="bg-black/70 p-4 sm:p-5 rounded-lg sm:rounded-xl border border-emerald-500 shadow-[0_0_15px_#10b981aa] sm:shadow-[0_0_22px_#10b981aa] mb-6 md:mb-8">
        <h3 className="text-emerald-300 text-base sm:text-lg font-bold mb-3 sm:mb-4">{t("price_comparison_heading")}</h3>
        <ResponsiveContainer width="100%" height={220} className="sm:hidden">
          <LineChart data={pricingChanges}>
            <defs>
              <linearGradient id="purpleLine" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#a855f7" stopOpacity={0.8}/>
                <stop offset="100%" stopColor="#a855f7" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="cyanLine" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.8}/>
                <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="product" 
              stroke="#4b5563" 
              style={{fontSize: '9px'}}
              tick={{fill: '#9ca3af'}}
            />
            <YAxis 
              stroke="#4b5563"
              tick={{fill: '#9ca3af', fontSize: 10}}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'rgba(10, 10, 10, 0.95)', 
                border: '1px solid #10b981',
                borderRadius: '8px',
                boxShadow: '0 0 20px rgba(16, 185, 129, 0.4)',
                fontSize: '12px'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="suggested_price" 
              stroke="#a855f7" 
              strokeWidth={3} 
              name={t("suggested_price_label")}
              dot={{fill: '#a855f7', r: 4, strokeWidth: 1, stroke: '#1a1a1a'}}
              activeDot={{r: 6, fill: '#a855f7', stroke: '#ffffff', strokeWidth: 2}}
              style={{
                filter: 'drop-shadow(0 0 6px #a855f7)'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="current_price" 
              stroke="#06b6d4" 
              strokeWidth={3} 
              name={t("current_price_label")}
              dot={{fill: '#06b6d4', r: 4, strokeWidth: 1, stroke: '#1a1a1a'}}
              activeDot={{r: 6, fill: '#06b6d4', stroke: '#ffffff', strokeWidth: 2}}
              style={{
                filter: 'drop-shadow(0 0 6px #06b6d4)'
              }}
            />
          </LineChart>
        </ResponsiveContainer>
        <ResponsiveContainer width="100%" height={280} className="hidden sm:block">
          <LineChart data={pricingChanges}>
            <defs>
              <linearGradient id="purpleLine" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#a855f7" stopOpacity={0.8}/>
                <stop offset="100%" stopColor="#a855f7" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="cyanLine" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.8}/>
                <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="product" 
              stroke="#4b5563" 
              style={{fontSize: '11px'}}
              tick={{fill: '#9ca3af'}}
            />
            <YAxis 
              stroke="#4b5563"
              tick={{fill: '#9ca3af'}}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'rgba(10, 10, 10, 0.95)', 
                border: '1px solid #10b981',
                borderRadius: '12px',
                boxShadow: '0 0 30px rgba(16, 185, 129, 0.4)'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="suggested_price" 
              stroke="#a855f7" 
              strokeWidth={4} 
              name={t("suggested_price_label")}
              dot={{fill: '#a855f7', r: 6, strokeWidth: 2, stroke: '#1a1a1a'}}
              activeDot={{r: 8, fill: '#a855f7', stroke: '#ffffff', strokeWidth: 2}}
              style={{
                filter: 'drop-shadow(0 0 8px #a855f7)'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="current_price" 
              stroke="#06b6d4" 
              strokeWidth={4} 
              name={t("current_price_label")}
              dot={{fill: '#06b6d4', r: 6, strokeWidth: 2, stroke: '#1a1a1a'}}
              activeDot={{r: 8, fill: '#06b6d4', stroke: '#ffffff', strokeWidth: 2}}
              style={{
                filter: 'drop-shadow(0 0 8px #06b6d4)'
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Top Recommendations - Mobile Optimized */}
      <div className="relative bg-gradient-to-b from-black/90 to-black/60 p-4 sm:p-5 md:p-6 rounded-lg sm:rounded-xl border border-yellow-400/40 shadow-[0_0_25px_#facc15aa] sm:shadow-[0_0_35px_#facc15aa] mb-6 md:mb-8 backdrop-blur-md">
        <div className="absolute top-0 left-0 w-full h-[2px] sm:h-[3px] bg-gradient-to-r from-transparent via-yellow-400 to-transparent animate-scan"></div>

        <h3 className="text-yellow-300 text-lg sm:text-xl font-extrabold mb-4 sm:mb-5 tracking-wide flex items-center gap-2 drop-shadow-[0_0_8px_#facc15]">
          <span className="text-xl sm:text-2xl">🎯</span> {t("top_recommendations_heading")}
        </h3>

        <div className="space-y-4 sm:space-y-5">
          {topRecommendations.map((rec: TopRecommendation, idx: number) => (
            <div
              key={idx}
              className="relative bg-black/40 p-4 sm:p-5 rounded-lg border border-yellow-500/30 hover:border-yellow-400 hover:shadow-[0_0_20px_#facc15cc] sm:hover:shadow-[0_0_28px_#facc15cc] transition-all duration-300 backdrop-blur-sm group"
            >
              <div className="absolute -top-2 -left-2 sm:-top-3 sm:-left-3 w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-yellow-500 text-black font-bold text-base sm:text-lg flex items-center justify-center shadow-[0_0_10px_#facc15] sm:shadow-[0_0_15px_#facc15] animate-pulse">
                {rec.priority}
              </div>

              <div className="flex-1 ml-8 sm:ml-10">
                <h4 className="text-yellow-200 font-semibold text-base sm:text-lg mb-2 group-hover:text-white transition break-words">
                  {rec.action}
                </h4>

                <div className="text-gray-300 text-xs sm:text-sm leading-relaxed space-y-1">
                  <p className="text-yellow-300/80 break-words">
                    <strong className="text-yellow-400">{t("category_label")}:</strong> {rec.category}
                  </p>
                  {rec.details.product && (
                    <p className="break-words"><strong className="text-emerald-400">{t("product_label")}:</strong> {rec.details.product}</p>
                  )}
                  {rec.details.products && (
                    <p className="break-words"><strong className="text-emerald-400">{t("products_label")}:</strong> {rec.details.products.join(', ')}</p>
                  )}
                  {rec.details.discount_percent && (
                    <p><strong className="text-blue-400">{t("discount_label")}:</strong> {rec.details.discount_percent}%</p>
                  )}
                  {rec.details.expected_units_sold && (
                    <p><strong className="text-pink-400">{t("sales_label")}:</strong> {rec.details.expected_units_sold} {t("units_label")}</p>
                  )}
                  {rec.details.budget && (
                    <p className="break-words"><strong className="text-purple-400">{t("budget_label")}:</strong> {t("currency")} {rec.details.budget.toLocaleString()}</p>
                  )}
                </div>

                {rec.impact && (
                  <div className="mt-3 p-2 sm:p-3 bg-green-900/10 border border-green-500/30 rounded-lg shadow-[0_0_15px_#22c55e33]">
                    <p className="text-green-300 text-xs sm:text-sm font-semibold">{t("impact_label")}:</p>
                    <p className="text-green-200 text-xs leading-relaxed break-words">
                      {rec.impact.expected_revenue_increase_percent && (
                        <>{t("revenue_label")}: +{rec.impact.expected_revenue_increase_percent}%<br /></>
                      )}
                      {rec.impact.cost_savings && (
                        <>{t("cost_savings_label")}: {t("currency")} {rec.impact.cost_savings.toLocaleString()}<br /></>
                      )}
                      {rec.impact.expected_roi && (
                        <>{t("roi_label")}: {rec.impact.expected_roi}</>
                      )}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Two Column Section - Stacks on Mobile */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-5 md:gap-6 mb-6 md:mb-8">
        {/* Inventory Actions */}
        <div className="bg-black/70 p-4 sm:p-5 md:p-6 rounded-lg sm:rounded-xl border border-orange-500 shadow-[0_0_15px_#f97316aa] sm:shadow-[0_0_22px_#f97316aa]">
          <h3 className="text-orange-400 text-lg sm:text-xl font-bold mb-4 sm:mb-5 flex items-center gap-2">
            <span className="text-xl sm:text-2xl">📦</span> {t("inventory_actions_heading")}
          </h3>
          <div className="space-y-3">
            {inventoryActions.map((action: InventoryAction, idx: number) => (
              <div key={idx} className="bg-black/50 p-3 sm:p-4 rounded-lg border border-orange-500/30">
                <h4 className="text-orange-300 font-semibold text-sm sm:text-base mb-2 break-words">{action.product}</h4>
                <div className="text-gray-300 text-xs sm:text-sm space-y-1">
                  <p className="break-words"><strong>{t("action_label")}:</strong> <span className="text-orange-200">{action.action.replace(/_/g, ' ').toUpperCase()}</span></p>
                  <p className="break-words"><strong>{t("reason_label")}:</strong> {action.reason}</p>
                  <p><strong>{t("units_label")}:</strong> {action.units_affected}</p>
                  {action.discount_percent && <p><strong>{t("discount_label")}:</strong> {action.discount_percent}%</p>}
                  {action.hold_duration_weeks && <p><strong>{t("duration_label")}:</strong> {action.hold_duration_weeks} {t("weeks_label")}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-black/70 p-4 sm:p-5 md:p-6 rounded-lg sm:rounded-xl border border-pink-500 shadow-[0_0_15px_#ec4899aa] sm:shadow-[0_0_22px_#ec4899aa]">
          <h3 className="text-pink-400 text-lg sm:text-xl font-bold mb-4 sm:mb-5 flex items-center gap-2">
            <span className="text-xl sm:text-2xl">📢</span> {t("marketing_campaigns_heading")}
          </h3>
          <div className="space-y-3">
            {marketingSuggestions.map((campaign: MarketingSuggestion, idx: number) => (
              <div key={idx} className="bg-black/50 p-3 sm:p-4 rounded-lg border border-pink-500/30">
                <h4 className="text-pink-300 font-semibold text-sm sm:text-base mb-2 break-words">{campaign.product}</h4>
                <div className="text-gray-300 text-xs sm:text-sm space-y-1">
                  <p className="break-words"><strong>{t("channel_label")}:</strong> {campaign.channel}</p>
                  <p className="break-words"><strong>{t("type_label")}:</strong> {campaign.campaign_type}</p>
                  <p className="break-words"><strong>{t("budget_label")}:</strong> {t("currency")} {campaign.budget.toLocaleString()}</p>
                  <p><strong>{t("duration_label")}:</strong> {campaign.duration_days} {t("days_label")}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-black/70 p-4 sm:p-5 md:p-6 rounded-lg sm:rounded-xl border border-indigo-500 shadow-[0_0_15px_#6366f1aa] sm:shadow-[0_0_22px_#6366f1aa]">
        <h3 className="text-indigo-400 text-lg sm:text-xl font-bold mb-4 sm:mb-5 flex items-center gap-2">
          <span className="text-xl sm:text-2xl">💰</span> {t("detailed_pricing_heading")}
        </h3>
        <div className="overflow-x-auto -mx-4 sm:mx-0">
          <div className="inline-block min-w-full align-middle px-4 sm:px-0">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-indigo-900/30 text-indigo-300">
                <tr>
                  <th className="p-2 sm:p-3 border border-indigo-700 whitespace-nowrap">{t("product_label")}</th>
                  <th className="p-2 sm:p-3 border border-indigo-700 whitespace-nowrap">{t("current_price_label")}</th>
                  <th className="p-2 sm:p-3 border border-indigo-700 whitespace-nowrap">{t("suggested_price_label")}</th>
                  <th className="p-2 sm:p-3 border border-indigo-700 whitespace-nowrap">{t("discount_label")}</th>
                  <th className="p-2 sm:p-3 border border-indigo-700 min-w-[200px]">{t("reason_label")}</th>
                </tr>
              </thead>
              <tbody className="text-gray-300">
                {pricingChanges.map((item: PricingChange, idx: number) => (
                  <tr key={idx} className="hover:bg-indigo-900/20 transition-colors">
                    <td className="p-2 sm:p-3 border border-indigo-700/50 font-semibold whitespace-nowrap">{item.product}</td>
                    <td className="p-2 sm:p-3 border border-indigo-700/50 whitespace-nowrap">{t("currency")} {item.current_price.toLocaleString()}</td>
                    <td className="p-2 sm:p-3 border border-indigo-700/50 text-green-400 whitespace-nowrap">{t("currency")} {item.suggested_price.toLocaleString()}</td>
                    <td className="p-2 sm:p-3 border border-indigo-700/50 text-red-400 whitespace-nowrap">{item.discount_percent}%</td>
                    <td className="p-2 sm:p-3 border border-indigo-700/50 text-xs">{item.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  );
}