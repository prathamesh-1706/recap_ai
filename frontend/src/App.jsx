import { useEffect, useState } from "react";

import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  Clock3,
  CreditCard,
  LayoutDashboard,
  Menu,
  MoreHorizontal,
  PanelLeftClose,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  XCircle,
  Zap,
} from "lucide-react";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "./App.css";


function StatCard({
  icon: Icon,
  label,
  value,
  change,
  positive = true,
  description,
}) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <div className="stat-icon">
          <Icon size={18} />
        </div>

        <span
          className={
            positive
              ? "change positive"
              : "change negative"
          }
        >
          {positive ? (
            <ArrowUpRight size={14} />
          ) : (
            <ArrowDownRight size={14} />
          )}

          {change}
        </span>
      </div>

      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-description">
        {description}
      </div>
    </div>
  );
}


function RiskBar({ label, value, amount }) {
  return (
    <div className="risk-row">
      <div className="risk-header">
        <span>{label}</span>
        <strong>{value}%</strong>
      </div>

      <div className="risk-track">
        <div
          className="risk-fill"
          style={{ width: `${value}%` }}
        />
      </div>

      <span className="risk-amount">
        {amount}
      </span>
    </div>
  );
}


function App() {
  const [dashboard, setDashboard] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [simulating, setSimulating] = useState(false);
  const [simulationResult, setSimulationResult] =
    useState(null);

  const [scenario, setScenario] =
    useState("insufficient_funds");


  // =========================================================
  // FETCH DASHBOARD
  // =========================================================

  const fetchDashboard = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/dashboard"
      );

      if (!response.ok) {
        throw new Error(
          `Dashboard API returned ${response.status}`
        );
      }

      const data = await response.json();

      setDashboard(data);
      setError(null);
    } catch (err) {
      console.error(
        "Failed to load dashboard:",
        err
      );

      setError(err.message);
    } finally {
      setLoading(false);
    }
  };


  // =========================================================
  // FETCH AUDIT LOGS
  // =========================================================

  const fetchAuditLogs = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/audit-logs"
      );

      if (!response.ok) {
        throw new Error(
          `Audit Logs API returned ${response.status}`
        );
      }

      const data = await response.json();

      setAuditLogs(
        Array.isArray(data) ? data : []
      );
    } catch (err) {
      console.error(
        "Failed to load audit logs:",
        err
      );

      // Don't break the whole dashboard
      setAuditLogs([]);
    }
  };


  // =========================================================
  // INITIAL LOAD + AUTO REFRESH
  // =========================================================

  useEffect(() => {
    fetchDashboard();
    fetchAuditLogs();

    const interval = setInterval(() => {
      fetchDashboard();
      fetchAuditLogs();
    }, 5000);

    return () => {
      clearInterval(interval);
    };
  }, []);


  // =========================================================
  // SIMULATE PAYMENT
  // =========================================================

  const simulatePayment = async () => {
    setSimulating(true);
    setSimulationResult(null);
    setError(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/simulator/generate",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            scenario,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Simulator API returned ${response.status}`
        );
      }

      const data = await response.json();

      setSimulationResult(data);


      // Refresh dashboard
      await fetchDashboard();

      // Refresh audit logs
      await fetchAuditLogs();

    } catch (err) {
      console.error(
        "Simulation failed:",
        err
      );

      setError(err.message);

    } finally {
      setSimulating(false);
    }
  };


  // =========================================================
  // LOADING STATE
  // =========================================================

  if (loading) {
    return (
      <div className="app-shell">
        <main className="main">
          <div className="content">
            <section className="hero">
              <div>
                <div className="eyebrow">
                  <Sparkles size={14} />
                  AI-POWERED RECOVERY
                </div>

                <h1>
                  Loading RECAP...
                </h1>

                <p>
                  Connecting to the live recovery
                  intelligence engine.
                </p>
              </div>
            </section>
          </div>
        </main>
      </div>
    );
  }


  // =========================================================
  // ERROR STATE
  // =========================================================

  if (error || !dashboard) {
    return (
      <div className="app-shell">
        <main className="main">
          <div className="content">
            <section className="hero">
              <div>
                <div className="eyebrow">
                  <AlertTriangle size={14} />
                  CONNECTION ERROR
                </div>

                <h1>
                  RECAP API unavailable.
                </h1>

                <p>
                  Start the FastAPI backend and
                  refresh the dashboard.
                </p>

                {error && (
                  <p
                    style={{
                      marginTop: "12px",
                      opacity: 0.6,
                    }}
                  >
                    {error}
                  </p>
                )}
              </div>
            </section>
          </div>
        </main>
      </div>
    );
  }


  // =========================================================
  // SAFE DATA EXTRACTION
  // =========================================================

  const stats = dashboard.stats || {};

  const recoveryTrend =
    Array.isArray(
      dashboard.recovery_trend
    )
      ? dashboard.recovery_trend
      : [];

  const decisions =
    Array.isArray(dashboard.decisions)
      ? dashboard.decisions
      : [];

  const riskBreakdown =
    Array.isArray(
      dashboard.risk_breakdown
    )
      ? dashboard.risk_breakdown
      : [];

  const latestDecision =
    decisions.length > 0
      ? decisions[0]
      : null;


  // =========================================================
  // RISK DATA
  // =========================================================

  const riskTotal =
    riskBreakdown.reduce(
      (sum, item) =>
        sum + (Number(item.count) || 0),
      0
    ) || 1;

  const riskData =
    riskBreakdown.map((item) => ({
      ...item,

      percentage: Math.round(
        ((Number(item.count) || 0) /
          riskTotal) *
          100
      ),
    }));


  // =========================================================
  // AI CONFIDENCE
  // =========================================================

  const averageConfidence =
    decisions.length > 0
      ? Math.round(
          (decisions.reduce(
            (sum, decision) =>
              sum +
              (Number(
                decision.confidence
              ) || 0),
            0
          ) /
            decisions.length) *
            100
        )
      : 0;


  return (
    <div className="app-shell">

      {/* =====================================================
          SIDEBAR
      ====================================================== */}

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-mark">
            <Zap
              size={19}
              fill="currentColor"
            />
          </div>

          <div>
            <div className="brand-name">
              RECAP
            </div>

            <div className="brand-subtitle">
              Revenue Intelligence
            </div>
          </div>

        </div>


        <div className="workspace">
          <span className="workspace-dot" />

          <span>
            Production
          </span>

          <ChevronRight size={14} />
        </div>


        <nav className="nav">

          <div className="nav-section">
            COMMAND CENTER
          </div>


          <a
            className="nav-item active"
            href="#overview"
          >
            <LayoutDashboard size={18} />
            Overview
          </a>


          <a
            className="nav-item"
            href="#payments"
          >
            <CreditCard size={18} />

            Payments

            <span className="nav-count">
              {stats.total_payments ?? 0}
            </span>
          </a>


          <a
            className="nav-item"
            href="#recovery"
          >
            <RefreshCw size={18} />
            Recovery
          </a>


          <a
            className="nav-item"
            href="#ai"
          >
            <BrainCircuit size={18} />

            AI Decisions

            <span className="ai-dot" />
          </a>


          <a
            className="nav-item"
            href="#risk"
          >
            <AlertTriangle size={18} />
            Risk
          </a>


          <div className="nav-section second">
            SYSTEM
          </div>


          <a
            className="nav-item"
            href="#audit"
          >
            <ShieldCheck size={18} />
            Audit Logs
          </a>


          <a
            className="nav-item"
            href="#simulator"
          >
            <Activity size={18} />
            Simulator
          </a>

        </nav>


        <div className="sidebar-bottom">

          <div className="system-card">

            <div className="system-card-header">
              <span className="online-pulse" />
              <span>
                All systems operational
              </span>
            </div>

            <div className="system-meta">
              API
              <span>Healthy</span>
            </div>

            <div className="system-meta">
              AI
              <span>Ollama</span>
            </div>

          </div>


          <div className="profile">

            <div className="avatar">
              P
            </div>

            <div className="profile-info">
              <strong>
                Prathamesh
              </strong>

              <span>
                Administrator
              </span>
            </div>

            <MoreHorizontal size={18} />

          </div>

        </div>

      </aside>


      {/* =====================================================
          MAIN
      ====================================================== */}

      <main className="main">

        {/* TOPBAR */}

        <header className="topbar">

          <div className="mobile-menu">
            <Menu size={20} />
          </div>


          <div className="breadcrumbs">

            <span>
              Command Center
            </span>

            <ChevronRight size={14} />

            <strong>
              Overview
            </strong>

          </div>


          <div className="topbar-actions">

            <div className="live-status">
              <span className="live-dot" />
              Live
            </div>

            <button className="icon-button">
              <Clock3 size={18} />
            </button>

            <button className="icon-button">
              <PanelLeftClose size={18} />
            </button>

          </div>

        </header>


        <div
          className="content"
          id="overview"
        >

          {/* HERO */}

          <section className="hero">

            <div>

              <div className="eyebrow">
                <Sparkles size={14} />
                AI-POWERED RECOVERY
              </div>

              <h1>
                Good evening, prathamesh.
              </h1>

              <p>
                RECAP is monitoring payment events
                and generating intelligent recovery
                recommendations in real time.
              </p>

            </div>

          </section>


          {/* =================================================
              STATS
          ================================================== */}

          <section className="stats-grid">

            <StatCard
              icon={CircleDollarSign}
              label="Recovery Opportunity"
              value={`₹${(
                Number(
                  stats.recovered_amount
                ) || 0
              ).toLocaleString("en-IN")}`}
              change="LIVE"
              description="Estimated value from approved recovery actions"
            />


            <StatCard
              icon={TrendingUp}
              label="Recovery Action Rate"
              value={`${stats.recovery_rate ?? 0}%`}
              change="LIVE"
              description="Actionable approved recommendations"
            />


            <StatCard
              icon={CreditCard}
              label="Payment Events"
              value={
                stats.total_payments ?? 0
              }
              change="LIVE"
              description="Processed by RECAP"
            />


            <StatCard
              icon={XCircle}
              label="Failed Payments"
              value={
                stats.failed_payments ?? 0
              }
              change="LIVE"
              description="Payments requiring recovery decisions"
            />

          </section>


          {/* =================================================
              RECOVERY + AI
          ================================================== */}

          <section className="main-grid">

            {/* RECOVERY CHART */}

            <div
              className="panel recovery-panel"
              id="recovery"
            >

              <div className="panel-header">

                <div>

                  <div className="panel-title">
                    Recovery performance
                  </div>

                  <div className="panel-subtitle">
                    Recovery opportunity and
                    recommendation attempts
                  </div>

                </div>


                <div className="chart-legend">

                  <span>
                    <i className="legend-dot recovery" />
                    Recovery opportunity
                  </span>

                  <span>
                    <i className="legend-dot attempts" />
                    Attempts
                  </span>

                </div>

              </div>


              <div className="chart">

                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >

                  <AreaChart
                    data={recoveryTrend}
                  >

                    <defs>

                      <linearGradient
                        id="recoveryGradient"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >

                        <stop
                          offset="0%"
                          stopOpacity={0.24}
                        />

                        <stop
                          offset="100%"
                          stopOpacity={0}
                        />

                      </linearGradient>

                    </defs>


                    <CartesianGrid
                      vertical={false}
                      stroke="rgba(255,255,255,0.055)"
                    />


                    <XAxis
                      dataKey="day"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 11 }}
                    />


                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 11 }}
                    />


                    <Tooltip />


                    <Area
                      type="monotone"
                      dataKey="attempts"
                      strokeWidth={2}
                      fill="transparent"
                    />


                    <Area
                      type="monotone"
                      dataKey="recovered"
                      strokeWidth={2}
                      fill="url(#recoveryGradient)"
                    />

                  </AreaChart>

                </ResponsiveContainer>

              </div>

            </div>


            {/* AI PANEL */}

            <div
              className="panel ai-panel"
              id="ai"
            >

              <div className="panel-header">

                <div>

                  <div className="panel-title">
                    AI recovery agent
                  </div>

                  <div className="panel-subtitle">
                    Local intelligence engine
                  </div>

                </div>


                <span className="status-badge">
                  <span className="status-dot" />
                  ONLINE
                </span>

              </div>


              <div className="ai-model">

                <div className="ai-model-icon">
                  <BrainCircuit size={22} />
                </div>

                <div>

                  <strong>
                    gemma3:4b
                  </strong>

                  <span>
                    Ollama Local Agent
                  </span>

                </div>

              </div>


              <div className="ai-metrics">

                <div>
                  <span>
                    Decisions
                  </span>

                  <strong>
                    {decisions.length}
                  </strong>
                </div>


                <div>
                  <span>
                    AI handled
                  </span>

                  <strong>
                    {decisions.length}
                  </strong>
                </div>


                <div>
                  <span>
                    Fallback
                  </span>

                  <strong>
                    0
                  </strong>
                </div>


                <div>
                  <span>
                    Avg. confidence
                  </span>

                  <strong>
                    {averageConfidence}%
                  </strong>
                </div>

              </div>


              <div className="ai-message">

                <Sparkles size={16} />

                <div>

                  <strong>
                    AI intelligence active
                  </strong>

                  <span>
                    Every recommendation is
                    validated by the Policy Engine.
                  </span>

                </div>

              </div>

            </div>

          </section>


          {/* =================================================
              SIMULATOR
          ================================================== */}

          <section
            className="panel simulator-panel"
            id="simulator"
          >

            <div className="panel-header">

              <div>

                <div className="panel-title">
                  Payment Simulator
                </div>

                <div className="panel-subtitle">
                  Generate a synthetic payment event
                  and run it through RECAP
                </div>

              </div>


              <span className="status-badge">
                <span className="status-dot" />
                LIVE
              </span>

            </div>


            <div className="simulator-controls">

              <div className="simulator-field">

                <label>
                  Failure scenario
                </label>


                <select
                  value={scenario}
                  onChange={(event) =>
                    setScenario(
                      event.target.value
                    )
                  }
                  disabled={simulating}
                >

                  <option value="temporary_failure">
                    Temporary Failure
                  </option>

                  <option value="insufficient_funds">
                    Insufficient Funds
                  </option>

                  <option value="payment_method_problem">
                    Payment Method Problem
                  </option>

                  <option value="risk_failure">
                    Risk Failure
                  </option>

                  <option value="unknown_failure">
                    Unknown Failure
                  </option>

                  <option value="successful_payment">
                    Successful Payment
                  </option>

                </select>

              </div>


              <button
                className="simulate-button"
                onClick={simulatePayment}
                disabled={simulating}
              >

                <Zap size={16} />

                {simulating
                  ? "Processing..."
                  : "Simulate Payment"}

              </button>

            </div>


            {simulationResult && (

              <div className="simulation-result">

                <div className="simulation-result-header">

                  <div>

                    <span>
                      Latest simulation
                    </span>

                    <strong>
                      {simulationResult.payment_id}
                    </strong>

                  </div>


                  <span className="approved-badge">

                    <CheckCircle2 size={14} />

                    {simulationResult.policy_decision}

                  </span>

                </div>


                <div className="simulation-metrics">

                  <div>

                    <span>
                      Risk
                    </span>

                    <strong>
                      {(
                        simulationResult.risk_category ||
                        "unknown"
                      ).replace(
                        /_/g,
                        " "
                      )}
                    </strong>

                  </div>


                  <div>

                    <span>
                      AI Recommendation
                    </span>

                    <strong>
                      {simulationResult.recommended_action ||
                        "N/A"}
                    </strong>

                  </div>


                  <div>

                    <span>
                      Confidence
                    </span>

                    <strong>
                      {Math.round(
                        (Number(
                          simulationResult.confidence
                        ) || 0) * 100
                      )}
                      %
                    </strong>

                  </div>


                  <div>

                    <span>
                      Estimated Recovery
                    </span>

                    <strong>
                      ₹
                      {(
                        Number(
                          simulationResult.estimated_recovery_amount
                        ) || 0
                      ).toLocaleString("en-IN")}
                    </strong>

                  </div>

                </div>


                <div className="simulation-reason">

                  <BrainCircuit size={15} />

                  <span>
                    {simulationResult.reason ||
                      "No reason provided."}
                  </span>

                </div>

              </div>

            )}

          </section>


          {/* =================================================
              RISK + LATEST DECISION
          ================================================== */}

          <section
            className="lower-grid"
            id="risk"
          >

            {/* RISK */}

            <div className="panel">

              <div className="panel-header">

                <div>

                  <div className="panel-title">
                    Risk distribution
                  </div>

                  <div className="panel-subtitle">
                    Classification of payment failures
                  </div>

                </div>

              </div>


              <div className="risk-list">

                {riskData.length === 0 ? (

                  <div className="audit-empty">

                    <ShieldCheck size={18} />

                    <span>
                      No risk data available yet.
                    </span>

                  </div>

                ) : (

                  riskData.map((risk) => (

                    <RiskBar
                      key={risk.category}
                      label={(
                        risk.category ||
                        "unknown"
                      ).replace(
                        /_/g,
                        " "
                      )}
                      value={risk.percentage}
                      amount={`${risk.count} event${
                        risk.count === 1
                          ? ""
                          : "s"
                      }`}
                    />

                  ))

                )}

              </div>

            </div>


            {/* LATEST DECISION */}

            <div
              className="panel decision-highlight"
            >

              <div className="panel-header">

                <div>

                  <div className="panel-title">
                    Latest AI decision
                  </div>

                  <div className="panel-subtitle">
                    {latestDecision?.payment_id ??
                      "No decisions yet"}
                  </div>

                </div>


                <span className="approved-badge">

                  <CheckCircle2 size={14} />

                  {latestDecision?.status ??
                    "N/A"}

                </span>

              </div>


              {latestDecision ? (

                <>

                  <div className="decision-action">

                    <div className="action-icon">
                      <RefreshCw size={23} />
                    </div>


                    <div>

                      <span>
                        Recommended action
                      </span>

                      <strong>
                        {latestDecision.action}
                      </strong>

                    </div>


                    <div className="confidence">

                      <strong>
                        {Math.round(
                          (Number(
                            latestDecision.confidence
                          ) || 0) * 100
                        )}
                        %
                      </strong>

                      <span>
                        confidence
                      </span>

                    </div>

                  </div>


                  <div className="decision-reason">

                    <div className="reason-icon">
                      <BrainCircuit size={15} />
                    </div>

                    <p>

                      RECAP classified this payment
                      as{" "}

                      {(
                        latestDecision.risk ||
                        "unknown"
                      ).replace(
                        /_/g,
                        " "
                      )}

                      {" "}and recommends{" "}

                      {(
                        latestDecision.action ||
                        "no action"
                      ).replace(
                        /_/g,
                        " "
                      )}

                      .

                    </p>

                  </div>


                  <div className="decision-footer">

                    <span>
                      <ShieldCheck size={14} />
                      Policy validated
                    </span>

                    <span>
                      <Zap size={14} />
                      AI proposal
                    </span>

                  </div>

                </>

              ) : (

                <div className="decision-reason">

                  <div className="reason-icon">
                    <AlertTriangle size={15} />
                  </div>

                  <p>
                    No AI decision is currently
                    available.
                  </p>

                </div>

              )}

            </div>

          </section>


          {/* =================================================
              AUDIT LOGS
          ================================================== */}

          <section
            className="panel audit-panel"
            id="audit"
          >

            <div className="panel-header">

              <div>

                <div className="panel-title">
                  Audit Logs
                </div>

                <div className="panel-subtitle">
                  Complete decision trail for
                  payment recovery actions
                </div>

              </div>


              <span className="status-badge">

                <span className="status-dot" />

                LIVE

              </span>

            </div>


            <div className="audit-list">

              {auditLogs.length === 0 ? (

                <div className="audit-empty">

                  <ShieldCheck size={18} />

                  <span>
                    No audit records available yet.
                  </span>

                </div>

              ) : (

                auditLogs.map((log) => (

                  <div
                    className="audit-row"
                    key={log.id}
                  >

                    <div className="audit-icon">

                      {log.policy_decision ===
                      "APPROVED" ? (

                        <CheckCircle2 size={16} />

                      ) : (

                        <XCircle size={16} />

                      )}

                    </div>


                    <div className="audit-main">

                      <div className="audit-top">

                        <strong>
                          {log.payment_id}
                        </strong>


                        <span
                          className={
                            log.policy_decision ===
                            "APPROVED"
                              ? "audit-approved"
                              : "audit-denied"
                          }
                        >
                          {log.policy_decision}
                        </span>

                      </div>


                      <div className="audit-meta">

                        <span>
                          {log.event_type}
                        </span>


                        <span>
                          {(
                            log.risk_category ||
                            "unknown"
                          ).replace(
                            /_/g,
                            " "
                          )}
                        </span>


                        <span>
                          {(
                            log.proposed_action ||
                            "N/A"
                          ).replace(
                            /_/g,
                            " "
                          )}
                        </span>


                        <span>

                          {log.created_at
                            ? new Date(
                                log.created_at
                              ).toLocaleString(
                                "en-IN"
                              )
                            : "Unknown time"}

                        </span>

                      </div>


                      <p className="audit-reason">

                        {log.reason ||
                          "No reason provided."}

                      </p>

                    </div>

                  </div>

                ))

              )}

            </div>

          </section>


          {/* =================================================
              RECENT DECISIONS
          ================================================== */}

          <section
            className="panel decisions-panel"
            id="payments"
          >

            <div className="panel-header">

              <div>

                <div className="panel-title">
                  Recent recovery decisions
                </div>

                <div className="panel-subtitle">
                  Latest recommendations generated
                  by RECAP
                </div>

              </div>


              <button className="panel-action">

                View all payments

                <ChevronRight size={14} />

              </button>

            </div>


            <div className="table-wrap">

              <table>

                <thead>

                  <tr>

                    <th>
                      PAYMENT
                    </th>

                    <th>
                      RISK
                    </th>

                    <th>
                      RECOMMENDATION
                    </th>

                    <th>
                      CONFIDENCE
                    </th>

                    <th>
                      AMOUNT
                    </th>

                    <th>
                      POLICY
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {decisions.length === 0 ? (

                    <tr>

                      <td
                        colSpan="6"
                        style={{
                          textAlign: "center",
                          padding: "30px",
                        }}
                      >
                        No recovery decisions
                        available yet.
                      </td>

                    </tr>

                  ) : (

                    decisions.map(
                      (decision) => (

                        <tr
                          key={
                            decision.payment_id
                          }
                        >

                          <td>

                            <div className="payment-cell">

                              <div className="payment-icon">
                                <CreditCard
                                  size={15}
                                />
                              </div>


                              <div>

                                <strong>
                                  {
                                    decision.payment_id
                                  }
                                </strong>

                                <span>
                                  {
                                    decision.customer_id
                                  }
                                </span>

                              </div>

                            </div>

                          </td>


                          <td>

                            <span className="risk-label">

                              {(
                                decision.risk ||
                                "unknown"
                              ).replace(
                                /_/g,
                                " "
                              )}

                            </span>

                          </td>


                          <td>

                            <span className="action-label">

                              {(
                                decision.action ||
                                "N/A"
                              ).replace(
                                /_/g,
                                " "
                              )}

                            </span>

                          </td>


                          <td>

                            <span className="confidence-label">

                              {Math.round(
                                (Number(
                                  decision.confidence
                                ) || 0) * 100
                              )}

                              %

                            </span>

                          </td>


                          <td>

                            <strong>

                              ₹
                              {(
                                Number(
                                  decision.amount
                                ) || 0
                              ).toLocaleString(
                                "en-IN"
                              )}

                            </strong>

                          </td>


                          <td>

                            <span className="table-approved">

                              <CheckCircle2
                                size={14}
                              />

                              {
                                decision.status
                              }

                            </span>

                          </td>

                        </tr>

                      )
                    )

                  )}

                </tbody>

              </table>

            </div>

          </section>


          {/* FOOTER */}

          <footer className="footer">

            <span>
              RECAP v0.1.0
            </span>

            <span>
              Revenue Intelligence &
              Recovery Agent
            </span>

            <span className="footer-status">

              <span className="online-pulse" />

              API Operational

            </span>

          </footer>

        </div>

      </main>

    </div>
  );
}


export default App;

