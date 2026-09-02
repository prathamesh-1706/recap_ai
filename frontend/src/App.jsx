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

const recoveryData = [
  { day: "Mon", recovered: 42, attempts: 58 },
  { day: "Tue", recovered: 51, attempts: 67 },
  { day: "Wed", recovered: 48, attempts: 63 },
  { day: "Thu", recovered: 71, attempts: 82 },
  { day: "Fri", recovered: 64, attempts: 78 },
  { day: "Sat", recovered: 82, attempts: 91 },
  { day: "Sun", recovered: 76, attempts: 88 },
];

const decisions = [
  {
    id: "pay_test_001",
    customer: "cust_test_001",
    risk: "Temporary failure",
    action: "WAIT_AND_RETRY",
    confidence: "95%",
    amount: "₹50,000",
    status: "Approved",
  },
  {
    id: "pay_nsf_014",
    customer: "cust_10482",
    risk: "Insufficient funds",
    action: "SEND_MESSAGE",
    confidence: "91%",
    amount: "₹12,500",
    status: "Approved",
  },
  {
    id: "pay_pm_029",
    customer: "cust_82711",
    risk: "Payment method",
    action: "UPDATE_METHOD",
    confidence: "88%",
    amount: "₹28,000",
    status: "Approved",
  },
  {
    id: "pay_risk_041",
    customer: "cust_21908",
    risk: "Suspected risk",
    action: "ESCALATE",
    confidence: "97%",
    amount: "₹85,000",
    status: "Approved",
  },
];

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

        <span className={positive ? "change positive" : "change negative"}>
          {positive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
          {change}
        </span>
      </div>

      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div> <div className="stat-description">{description}</div>
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
        <div className="risk-fill" style={{ width: `${value}%` }} />
      </div>

      <span className="risk-amount">{amount}</span>
    </div>
  );
}

function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Zap size={19} fill="currentColor" />
          </div>

          <div>
            <div className="brand-name">RECAP</div>
            <div className="brand-subtitle">Revenue Intelligence</div>
          </div>
        </div>

        <div className="workspace">
          <span className="workspace-dot" />
          <span>Production</span>
          <ChevronRight size={14} />
        </div>

        <nav className="nav">
          <div className="nav-section">COMMAND CENTER</div>

          <a className="nav-item active" href="#overview">
            <LayoutDashboard size={18} />
            Overview
          </a>

          <a className="nav-item" href="#payments">
            <CreditCard size={18} />
            Payments
            <span className="nav-count">126</span>
          </a>

          <a className="nav-item" href="#recovery">
            <RefreshCw size={18} />
            Recovery
          </a>

          <a className="nav-item" href="#ai">
            <BrainCircuit size={18} />
            AI Decisions
            <span className="ai-dot" />
          </a>

          <a className="nav-item" href="#risk">
            <AlertTriangle size={18} />
            Risk
          </a>

          <div className="nav-section second">SYSTEM</div>

          <a className="nav-item" href="#audit">
            <ShieldCheck size={18} />
            Audit Logs
          </a>

          <a className="nav-item" href="#simulator">
            <Activity size={18} />
            Simulator
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-card">
            <div className="system-card-header">
              <span className="online-pulse" />
              <span>All systems operational</span>
            </div>

            <div className="system-meta">
              API <span>Healthy</span>
            </div>

            <div className="system-meta">
              AI <span>Ollama</span>
            </div>
          </div>

          <div className="profile">
            <div className="avatar">P</div>
            <div className="profile-info">
              <strong>Prathamesh</strong>
              <span>Administrator</span>
            </div>
            <MoreHorizontal size={18} />
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="mobile-menu">
            <Menu size={20} />
          </div>

          <div className="breadcrumbs">
            <span>Command Center</span>
            <ChevronRight size={14} />
            <strong>Overview</strong>
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

        <div className="content" id="overview">
          <section className="hero">
            <div>
              <div className="eyebrow">
                <Sparkles size={14} />
                AI-POWERED RECOVERY
              </div>

              <h1>Good evening, Prathamesh.</h1>

              <p>
                Here's what RECAP recovered and prevented today.
              </p>
            </div>

            <button className="date-button">
              <Activity size={16} />
              Last 7 days
              <ChevronRight size={15} />
            </button>
          </section>

          <section className="stats-grid">
            <StatCard
              icon={CircleDollarSign}
              label="Recovery value"
              value="₹4.82L"
              change="18.4%"
              description="Estimated recoverable revenue"
            />

            <StatCard
              icon={TrendingUp}
              label="Recovery rate"
              value="87.4%"
              change="6.8%"
              description="Across failed payments"
            />

            <StatCard
              icon={CreditCard}
              label="Payment events"
              value="126"
              change="12.2%"
              description="Processed by RECAP"
            />

            <StatCard
              icon={CheckCircle2}
              label="Recovered"
              value="₹2.14L"
              change="24.6%"
              description="Revenue successfully recovered"
            />
          </section>

          <section className="main-grid">
            <div className="panel recovery-panel" id="recovery">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Recovery performance</div>
                  <div className="panel-subtitle">
                    Recovery attempts vs successful recovery
                  </div>
                </div>

                <button className="panel-action">
                  View report
                  <ChevronRight size={14} />
                </button>
              </div>

              <div className="chart-legend">
                <span>
                  <i className="legend-dot recovery" />
                  Recovered
                </span>
                <span>
                  <i className="legend-dot attempts" />
                  Attempts
                </span>
              </div>

              <div className="chart">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={recoveryData}>
                    <defs>
                      <linearGradient id="recoveryGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopOpacity={0.24} />
                        <stop offset="100%" stopOpacity={0} />
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
                      tick={{ fill: "#737b8c", fontSize: 12 }}
                      dy={10}
                    />

                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: "#737b8c", fontSize: 12 }}
                      width={32}
                    />

                    <Tooltip
                      contentStyle={{
                        background: "#151922",
                        border: "1px solid rgba(255,255,255,0.1)",
                        borderRadius: "10px",
                        color: "#fff",
                      }}
                    />

                    <Area
                      type="monotone"
                      dataKey="attempts"
                      stroke="#5c6678"
                      strokeWidth={2}
                      fill="none"
                    />

                    <Area
                      type="monotone"
                      dataKey="recovered"
                      stroke="#a3ff5c"
                      strokeWidth={2.5}
                      fill="url(#recoveryGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="panel ai-panel" id="ai">
              <div className="panel-header">
                <div>
                  <div className="panel-title">AI decision engine</div>
                  <div className="panel-subtitle">
                    Current intelligence layer
                  </div>
                </div>

                <span className="status-badge">
                  <span className="status-dot" />
                  ONLINE
                </span>
              </div>

              <div className="ai-model">
                <div className="ai-orb">
                  <BrainCircuit size={25} />
                </div>

                <div>
                  <strong>gemma3:4b</strong>
                  <span>Ollama Local Agent</span>
                </div>

                <div className="model-check">
                  <CheckCircle2 size={17} />
                </div>
              </div>

              <div className="ai-metrics">
                <div>
                  <span>Decisions</span>
                  <strong>126</strong>
                </div>

                <div>
                  <span>AI handled</span>
                  <strong>104</strong>
                </div>

                <div>
                  <span>Fallback</span>
                  <strong>22</strong>
                </div>

                <div>
                  <span>Avg. confidence</span>
                  <strong>91.8%</strong>
                </div>
              </div>

              <div className="ai-message">
                <Sparkles size={16} />
                <div>
                  <strong>AI intelligence active</strong>
                  <span>
                    Every recommendation is validated by the Policy Engine.
                  </span>
                </div>
              </div>
            </div>
          </section>

          <section className="lower-grid" id="risk">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Risk distribution</div>
                  <div className="panel-subtitle">
                    Payment failure classification
                  </div>
                </div>

                <button className="icon-only">
                  <MoreHorizontal size={18} />
                </button>
              </div>

              <div className="risk-list">
                <RiskBar
                  label="Temporary failure"
                  value={42}
                  amount="53 events"
                />

                <RiskBar
                  label="Insufficient funds"
                  value={28}
                  amount="35 events"
                />

                <RiskBar
                  label="Payment method"
                  value={18}
                  amount="23 events"
                />

                <RiskBar
                  label="Suspected risk"
                  value={8}
                  amount="10 events"
                />

                <RiskBar
                  label="Unknown"
                  value={4}
                  amount="5 events"
                />
              </div>
            </div>

            <div className="panel decision-highlight">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Latest AI decision</div>
                  <div className="panel-subtitle">
                    pay_test_001
                  </div>
                </div>

                <span className="approved-badge">
                  <CheckCircle2 size={14} />
                  APPROVED
                </span>
              </div>

              <div className="decision-action">
                <div className="action-icon">
                  <RefreshCw size={23} />
                </div>

                <div>
                  <span>Recommended action</span>
                  <strong>WAIT_AND_RETRY</strong>
                </div>

                <div className="confidence">
                  <strong>95%</strong>
                  <span>confidence</span>
                </div>
              </div>

              <div className="decision-reason">
                <div className="reason-icon">
                  <BrainCircuit size={15} />
                </div>

                <p>
                  Customer has high payment reliability and the gateway
                  failure appears temporary. RECAP recommends waiting before
                  attempting recovery.
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
            </div>
          </section>

          <section className="panel decisions-panel" id="payments">
            <div className="panel-header">
              <div>
                <div className="panel-title">Recent recovery decisions</div>
                <div className="panel-subtitle">
                  Latest recommendations generated by RECAP
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
                    <th>PAYMENT</th>
                    <th>RISK</th>
                    <th>RECOMMENDATION</th>
                    <th>CONFIDENCE</th>
                    <th>AMOUNT</th>
                    <th>POLICY</th>
                  </tr>
                </thead>

                <tbody>
                  {decisions.map((decision) => (
                    <tr key={decision.id}>
                      <td>
                        <div className="payment-cell">
                          <div className="payment-icon">
                            <CreditCard size={15} />
                          </div>
                          <div>
                            <strong>{decision.id}</strong>
                            <span>{decision.customer}</span>
                          </div>
                        </div>
                      </td>

                      <td>
                        <span className="risk-label">{decision.risk}</span>
                      </td>

                      <td>
                        <span className="action-label">
                          {decision.action}
                        </span>
                      </td>

                      <td>
                        <span className="confidence-label">
                          {decision.confidence}
                        </span>
                      </td>

                      <td>
                    <strong>{decision.amount}</strong>
                      </td>

                      <td>
                        <span className="table-approved">
                          <CheckCircle2 size={14} />
                          {decision.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <footer className="footer">
            <span>RECAP v0.1.0</span>
            <span>Revenue Intelligence & Recovery Agent</span>
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
