import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = 'http://localhost:8000/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [currentUser, setCurrentUser] = useState({ username: 'tester', role: 'tester', name: 'Priya Sharma (Test Officer)' });
  const [token, setToken] = useState('');
  
  // Dashboard & Reports State
  const [reports, setReports] = useState([]);
  const [stats, setStats] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [classFilter, setClassFilter] = useState('');
  const [selectedReport, setSelectedReport] = useState(null);
  const [qrModalReport, setQrModalReport] = useState(null);

  // Rulesets
  const [rulesets, setRulesets] = useState([]);
  const [activeRulesetId, setActiveRulesetId] = useState('oiml_r76_2006');
  const [rulesetDetails, setRulesetDetails] = useState(null);

  // Workbench Form State
  const [reportNumber, setReportNumber] = useState(`REP-${Date.now().toString().slice(-6)}`);
  const [instrument, setInstrument] = useState({
    manufacturer: 'Dibal S.A.',
    model: 'CS-6000',
    serial_number: 'SN-2026-6KG-01',
    accuracy_class: 'III',
    max_capacity: 6000,
    min_capacity: 40,
    verification_scale_interval_e: 2,
    actual_scale_interval_d: 2,
    unit: 'g',
    device_type: 'graduated_without_auxiliary',
    points_of_support: 4,
    is_multi_interval: false,
    is_grading_instrument: false,
  });

  const [plausibilityResult, setPlausibilityResult] = useState(null);

  // Weighing points
  const [weighingPoints, setWeighingPoints] = useState([
    { direction: 'increasing', load: 0, indicated: 0, delta_load: 0.8 },
    { direction: 'increasing', load: 40, indicated: 40, delta_load: 0.9 },
    { direction: 'increasing', load: 500, indicated: 500, delta_load: 1.0 },
    { direction: 'increasing', load: 1000, indicated: 1000, delta_load: 1.2 },
    { direction: 'increasing', load: 2000, indicated: 2000, delta_load: 0.6 },
    { direction: 'increasing', load: 4000, indicated: 4000, delta_load: 0.5 },
    { direction: 'increasing', load: 6000, indicated: 6000, delta_load: 0.4 },
    { direction: 'decreasing', load: 4000, indicated: 4000, delta_load: 0.5 },
    { direction: 'decreasing', load: 2000, indicated: 2000, delta_load: 0.7 },
    { direction: 'decreasing', load: 0, indicated: 0, delta_load: 0.8 },
  ]);
  const [weighingEval, setWeighingEval] = useState(null);

  // Eccentricity points
  const [eccentricityPositions, setEccentricityPositions] = useState([
    { position_id: 'center', description: 'Platform Center', load: 2000, indicated: 2000, delta_load: 0.8 },
    { position_id: 'pos_1', description: 'Front-Left Quadrant', load: 2000, indicated: 2000, delta_load: 0.5 },
    { position_id: 'pos_2', description: 'Back-Left Quadrant', load: 2000, indicated: 2000, delta_load: 1.1 },
    { position_id: 'pos_3', description: 'Back-Right Quadrant', load: 2000, indicated: 2000, delta_load: 0.7 },
    { position_id: 'pos_4', description: 'Front-Right Quadrant', load: 2000, indicated: 2000, delta_load: 0.9 },
  ]);
  const [eccentricityEval, setEccentricityEval] = useState(null);

  // Repeatability series
  const [repeatabilityRuns, setRepeatabilityRuns] = useState([
    { run_number: 1, load: 3000, indicated: 3000, delta_load: 0.8 },
    { run_number: 2, load: 3000, indicated: 3000, delta_load: 0.7 },
    { run_number: 3, load: 3000, indicated: 3000, delta_load: 0.9 },
    { run_number: 4, load: 3000, indicated: 3000, delta_load: 0.8 },
    { run_number: 5, load: 3000, indicated: 3000, delta_load: 1.0 },
    { run_number: 6, load: 3000, indicated: 3000, delta_load: 0.7 },
    { run_number: 7, load: 3000, indicated: 3000, delta_load: 1.1 },
    { run_number: 8, load: 3000, indicated: 3000, delta_load: 0.8 },
    { run_number: 9, load: 3000, indicated: 3000, delta_load: 1.2 },
    { run_number: 10, load: 3000, indicated: 3000, delta_load: 0.8 },
  ]);
  const [repeatabilityEval, setRepeatabilityEval] = useState(null);

  // Audit Logs
  const [auditLogs, setAuditLogs] = useState([]);

  // Verification Portal State
  const [verifyReportNum, setVerifyReportNum] = useState('');
  const [verifyHash, setVerifyHash] = useState('');
  const [verificationResult, setVerificationResult] = useState(null);

  // Reviewer Action Modal
  const [reviewModalReport, setReviewModalReport] = useState(null);
  const [reviewerComment, setReviewerComment] = useState('');

  // ─── LOGIN / ROLE SELECTION ───
  const selectRole = async (username, role, name) => {
    try {
      const resp = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password: `${username}123` })
      });
      if (resp.ok) {
        const data = await resp.json();
        setToken(data.access_token);
        setCurrentUser({ username, role, name });
      }
    } catch (err) {
      console.error("Login failed", err);
    }
  };

  useEffect(() => {
    // Initial login as tester
    selectRole('tester', 'tester', 'Priya Sharma (Test Officer)');
    fetchRulesets();
    fetchReports();
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/dashboard/stats`);
      if (res.ok) setStats(await res.json());
    } catch (e) { console.error(e); }
  };

  const fetchReports = async () => {
    try {
      let url = `${API_BASE}/reports?`;
      if (searchQuery) url += `search=${encodeURIComponent(searchQuery)}&`;
      if (statusFilter) url += `status=${encodeURIComponent(statusFilter)}&`;
      if (classFilter) url += `accuracy_class=${encodeURIComponent(classFilter)}&`;
      const res = await fetch(url);
      if (res.ok) setReports(await res.json());
    } catch (e) { console.error(e); }
  };

  const fetchRulesets = async () => {
    try {
      const res = await fetch(`${API_BASE}/rulesets`);
      if (res.ok) {
        const list = await res.json();
        setRulesets(list);
        if (list.length > 0) fetchRulesetDetails(list[0].ruleset_id);
      }
    } catch (e) { console.error(e); }
  };

  const fetchRulesetDetails = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/rulesets/${id}`);
      if (res.ok) {
        setRulesetDetails(await res.json());
        setActiveRulesetId(id);
      }
    } catch (e) { console.error(e); }
  };

  const fetchAuditLogs = async () => {
    try {
      const res = await fetch(`${API_BASE}/audit-logs?limit=40`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setAuditLogs(await res.json());
    } catch (e) { console.error(e); }
  };

  const triggerSeedSynthetic = async () => {
    try {
      const res = await fetch(`${API_BASE}/synthetic/seed`, { method: 'POST' });
      if (res.ok) {
        alert("Synthetic test datasets loaded into database successfully!");
        fetchReports();
        fetchStats();
      }
    } catch (e) { alert("Failed to seed synthetic data: " + e); }
  };

  // ─── LIVE METROLOGY EVALUATION TRIGGERS ───
  const runLiveEvaluation = async () => {
    try {
      // 1. Plausibility
      const plausRes = await fetch(`${API_BASE}/evaluate/plausibility`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instrument, ruleset_id: activeRulesetId })
      });
      if (plausRes.ok) setPlausibilityResult(await plausRes.json());

      // 2. Weighing Performance
      const wpRes = await fetch(`${API_BASE}/evaluate/weighing-performance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instrument,
          points: weighingPoints,
          ruleset_id: activeRulesetId,
          initial_zero_error_e0: 0.2
        })
      });
      if (wpRes.ok) setWeighingEval(await wpRes.json());

      // 3. Eccentricity
      const eccRes = await fetch(`${API_BASE}/evaluate/eccentricity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instrument,
          positions: eccentricityPositions,
          ruleset_id: activeRulesetId,
          initial_zero_error_e0: 0.2
        })
      });
      if (eccRes.ok) setEccentricityEval(await eccRes.json());

      // 4. Repeatability
      const repRes = await fetch(`${API_BASE}/evaluate/repeatability`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instrument,
          series: { "Series 1 (50% Max)": repeatabilityRuns },
          ruleset_id: activeRulesetId
        })
      });
      if (repRes.ok) setRepeatabilityEval(await repRes.json());

    } catch (e) {
      console.error("Evaluation error", e);
    }
  };

  // ─── PRESET LOADERS ───
  const loadPreset = (type) => {
    if (type === '6kg_class_iii') {
      setInstrument({
        manufacturer: 'Dibal S.A.',
        model: 'CS-6000',
        serial_number: `SN-${Date.now().toString().slice(-4)}`,
        accuracy_class: 'III',
        max_capacity: 6000,
        min_capacity: 40,
        verification_scale_interval_e: 2,
        actual_scale_interval_d: 2,
        unit: 'g',
        device_type: 'graduated_without_auxiliary',
        points_of_support: 4,
        is_multi_interval: false,
        is_grading_instrument: false,
      });
      setWeighingPoints([
        { direction: 'increasing', load: 0, indicated: 0, delta_load: 0.8 },
        { direction: 'increasing', load: 40, indicated: 40, delta_load: 0.9 },
        { direction: 'increasing', load: 1000, indicated: 1000, delta_load: 1.2 },
        { direction: 'increasing', load: 2000, indicated: 2000, delta_load: 0.6 },
        { direction: 'increasing', load: 4000, indicated: 4000, delta_load: 0.5 },
        { direction: 'increasing', load: 6000, indicated: 6000, delta_load: 0.4 },
        { direction: 'decreasing', load: 4000, indicated: 4000, delta_load: 0.5 },
        { direction: 'decreasing', load: 0, indicated: 0, delta_load: 0.8 },
      ]);
      setEccentricityPositions([
        { position_id: 'center', description: 'Platform Center', load: 2000, indicated: 2000, delta_load: 0.8 },
        { position_id: 'pos_1', description: 'Quadrant 1', load: 2000, indicated: 2000, delta_load: 0.5 },
        { position_id: 'pos_2', description: 'Quadrant 2', load: 2000, indicated: 2000, delta_load: 1.1 },
        { position_id: 'pos_3', description: 'Quadrant 3', load: 2000, indicated: 2000, delta_load: 0.7 },
        { position_id: 'pos_4', description: 'Quadrant 4', load: 2000, indicated: 2000, delta_load: 0.9 },
      ]);
    } else if (type === '600g_class_ii') {
      setInstrument({
        manufacturer: 'Mettler Toledo',
        model: 'ME204 Precision',
        serial_number: `SN-LAB-${Date.now().toString().slice(-4)}`,
        accuracy_class: 'II',
        max_capacity: 600,
        min_capacity: 2,
        verification_scale_interval_e: 0.1,
        actual_scale_interval_d: 0.01,
        unit: 'g',
        device_type: 'graduated_with_auxiliary',
        points_of_support: 1,
        is_multi_interval: false,
        is_grading_instrument: false,
      });
      setWeighingPoints([
        { direction: 'increasing', load: 0, indicated: 0, delta_load: null },
        { direction: 'increasing', load: 2, indicated: 2, delta_load: null },
        { direction: 'increasing', load: 200, indicated: 200.01, delta_load: null },
        { direction: 'increasing', load: 400, indicated: 400.02, delta_load: null },
        { direction: 'increasing', load: 600, indicated: 600.02, delta_load: null },
      ]);
      setEccentricityPositions([
        { position_id: 'center', description: 'Pan Center', load: 200, indicated: 200, delta_load: null },
        { position_id: 'pos_1', description: 'Corner 1', load: 200, indicated: 200.02, delta_load: null },
        { position_id: 'pos_2', description: 'Corner 2', load: 200, indicated: 200.01, delta_load: null },
      ]);
    } else if (type === '30t_class_iii') {
      setInstrument({
        manufacturer: 'Avery Weigh-Tronix',
        model: 'BridgeMaster 30T',
        serial_number: `SN-WB-${Date.now().toString().slice(-4)}`,
        accuracy_class: 'III',
        max_capacity: 30000,
        min_capacity: 200,
        verification_scale_interval_e: 10,
        actual_scale_interval_d: 10,
        unit: 'kg',
        device_type: 'graduated_without_auxiliary',
        points_of_support: 6,
        is_multi_interval: false,
        is_grading_instrument: false,
      });
      setWeighingPoints([
        { direction: 'increasing', load: 0, indicated: 0, delta_load: null },
        { direction: 'increasing', load: 200, indicated: 200, delta_load: null },
        { direction: 'increasing', load: 10000, indicated: 10000, delta_load: null },
        { direction: 'increasing', load: 20000, indicated: 20000, delta_load: null },
        { direction: 'increasing', load: 30000, indicated: 30000, delta_load: null },
      ]);
      setEccentricityPositions([
        { position_id: 'cell_1', description: 'Load cell 1', load: 6000, indicated: 6000, delta_load: null },
        { position_id: 'cell_2', description: 'Load cell 2', load: 6000, indicated: 6000, delta_load: null },
        { position_id: 'cell_3', description: 'Load cell 3', load: 6000, indicated: 6000, delta_load: null },
        { position_id: 'cell_4', description: 'Load cell 4', load: 6000, indicated: 6000, delta_load: null },
      ]);
    } else if (type === 'failing_scale') {
      setInstrument({
        manufacturer: 'Defective Scales Corp',
        model: 'ErrorProne 6000',
        serial_number: `SN-FAIL-${Date.now().toString().slice(-4)}`,
        accuracy_class: 'III',
        max_capacity: 6000,
        min_capacity: 40,
        verification_scale_interval_e: 2,
        actual_scale_interval_d: 2,
        unit: 'g',
        device_type: 'graduated_without_auxiliary',
        points_of_support: 4,
        is_multi_interval: false,
        is_grading_instrument: false,
      });
      setWeighingPoints([
        { direction: 'increasing', load: 0, indicated: 0, delta_load: 0.8 },
        { direction: 'increasing', load: 4000, indicated: 4004, delta_load: 0.6 }, // 4g error > MPE 2g -> FAIL!
      ]);
      setEccentricityPositions([
        { position_id: 'center', description: 'Center', load: 2000, indicated: 2000, delta_load: 0.8 },
        { position_id: 'pos_3', description: 'Corner 3 (Defective Bearing)', load: 2000, indicated: 2004, delta_load: 0.7 }, // FAIL!
      ]);
    }
  };

  // ─── REPORT SUBMISSION / CREATION ───
  const submitNewReport = async (submitForReview = false) => {
    try {
      const payload = {
        report_number: reportNumber,
        ruleset_id: activeRulesetId,
        instrument,
        weighing_points: weighingPoints,
        eccentricity_positions: eccentricityPositions,
        repeatability_series: { "Series 1 (50% Max)": repeatabilityRuns },
        notes: `Created by ${currentUser.name} via Workbench.`
      };
      const res = await fetch(`${API_BASE}/reports`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const err = await res.json();
        alert(`Error: ${err.detail || 'Failed to create report'}`);
        return;
      }
      const data = await res.json();
      if (submitForReview) {
        await fetch(`${API_BASE}/reports/${data.report_id}/submit`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        alert(`Report ${reportNumber} created and submitted for Reviewer sign-off!`);
      } else {
        alert(`Report ${reportNumber} saved as DRAFT.`);
      }
      fetchReports();
      fetchStats();
      setActiveTab('dashboard');
    } catch (e) {
      alert(`Error submitting report: ${e}`);
    }
  };

  // ─── REVIEWER SIGN / REJECT ───
  const signReportAction = async (reportId) => {
    if (currentUser.role !== 'reviewer' && currentUser.role !== 'admin') {
      alert("Permission Denied: Only users with Reviewer or Admin role can sign and lock reports.");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/reports/${reportId}/sign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ comments: reviewerComment || 'Approved for Legal Metrology Pattern Approval.' })
      });
      if (res.ok) {
        const data = await res.json();
        alert(`Report successfully signed, locked, and sealed!\nSHA-256: ${data.canonical_hash}`);
        setReviewModalReport(null);
        fetchReports();
        fetchStats();
      } else {
        const err = await res.json();
        alert(`Signing failed: ${err.detail}`);
      }
    } catch (e) { alert(e); }
  };

  const rejectReportAction = async (reportId) => {
    try {
      const res = await fetch(`${API_BASE}/reports/${reportId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ comments: reviewerComment || 'Rejected due to tolerance non-compliance.' })
      });
      if (res.ok) {
        alert("Report marked as REJECTED.");
        setReviewModalReport(null);
        fetchReports();
        fetchStats();
      }
    } catch (e) { alert(e); }
  };

  // ─── BRANCH VERSION ───
  const branchNewVersion = async (reportId) => {
    try {
      const res = await fetch(`${API_BASE}/reports/${reportId}/branch-version`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        alert(`New version ${data.new_report_number} created as DRAFT!`);
        fetchReports();
      }
    } catch (e) { alert(e); }
  };

  // ─── PUBLIC VERIFICATION ───
  const runPublicVerification = async () => {
    if (!verifyReportNum || !verifyHash) {
      alert("Please provide both Report Number and SHA-256 Hash.");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/reports/verify/${verifyReportNum}?hash=${verifyHash}`);
      if (res.ok) {
        setVerificationResult(await res.json());
      }
    } catch (e) { alert(e); }
  };

  return (
    <div>
      {/* ─── HEADER ─── */}
      <header className="header">
        <div className="header-brand">
          <div className="logo-icon">⚖️</div>
          <div>
            <div className="header-title">WeighProof Metrological Governance Engine</div>
            <div className="header-subtitle">OIML R 76 NAWI Type Evaluation & Tamper-Evident Report Generator (SIH 2026 PS26035)</div>
          </div>
        </div>
        <div className="header-controls">
          <button className="btn btn-secondary btn-sm" onClick={triggerSeedSynthetic}>
            📥 Seed Synthetic Test Instruments
          </button>
          <div className="role-badge">
            <span>Role:</span>
            <button className={`role-btn ${currentUser.role === 'tester' ? 'active' : ''}`} onClick={() => selectRole('tester', 'tester', 'Priya Sharma (Test Officer)')}>Tester</button>
            <button className={`role-btn ${currentUser.role === 'reviewer' ? 'active' : ''}`} onClick={() => selectRole('reviewer', 'reviewer', 'Dr. Rajesh Verma (Reviewer)')}>Reviewer</button>
            <button className={`role-btn ${currentUser.role === 'admin' ? 'active' : ''}`} onClick={() => selectRole('admin', 'admin', 'Amit Patel (Admin)')}>Admin</button>
          </div>
        </div>
      </header>

      {/* ─── NAVIGATION TABS ─── */}
      <nav className="nav-tabs">
        <button className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => { setActiveTab('dashboard'); fetchReports(); fetchStats(); }}>
          📊 Dashboard & Repository
        </button>
        <button className={`nav-tab ${activeTab === 'workbench' ? 'active' : ''}`} onClick={() => { setActiveTab('workbench'); runLiveEvaluation(); }}>
          🔬 Live Metrology Workbench
        </button>
        <button className={`nav-tab ${activeTab === 'verification' ? 'active' : ''}`} onClick={() => setActiveTab('verification')}>
          🛡️ Public QR & Hash Verification
        </button>
        <button className={`nav-tab ${activeTab === 'rulesets' ? 'active' : ''}`} onClick={() => setActiveTab('rulesets')}>
          📜 Versioned Rulesets
        </button>
        <button className={`nav-tab ${activeTab === 'audit' ? 'active' : ''}`} onClick={() => { setActiveTab('audit'); fetchAuditLogs(); }}>
          🔍 Audit Trail Log
        </button>
      </nav>

      <main className="main-content">
        {/* ══════════════════════════════════════════════════════════════
            TAB 1: DASHBOARD & REPOSITORY
        ══════════════════════════════════════════════════════════════ */}
        {activeTab === 'dashboard' && (
          <div>
            {stats && (
              <div className="stats-grid">
                <div className="stat-card">
                  <span className="stat-label">Total Type Reports</span>
                  <span className="stat-value">{stats.total_reports}</span>
                  <span className="stat-subtext">All active evaluations</span>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Cryptographically Sealed</span>
                  <span className="stat-value" style={{ color: 'var(--accent-blue)' }}>{stats.signed_reports}</span>
                  <span className="stat-subtext">Immutable SHA-256 locked</span>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Pending Review</span>
                  <span className="stat-value" style={{ color: 'var(--accent-amber)' }}>{stats.submitted_reports}</span>
                  <span className="stat-subtext">Awaiting sign-off</span>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Conforming Verdicts</span>
                  <span className="stat-value" style={{ color: 'var(--accent-green)' }}>{stats.pass_count} PASS</span>
                  <span className="stat-subtext">{stats.fail_count} Non-conforming</span>
                </div>
              </div>
            )}

            <div className="card">
              <div className="card-header">
                <div>
                  <div className="card-title">📁 Certified Type Evaluation Repository</div>
                  <div className="card-subtitle">Immutable registry of OIML R 76 examination reports with digital signatures & multi-format export</div>
                </div>
                <button className="btn btn-primary" onClick={() => { setActiveTab('workbench'); setReportNumber(`REP-${Date.now().toString().slice(-6)}`); }}>
                  ➕ New Type Evaluation
                </button>
              </div>

              {/* Filters */}
              <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                <input
                  type="text"
                  placeholder="Search report number, serial, model..."
                  className="form-input"
                  style={{ flex: 1 }}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyUp={(e) => e.key === 'Enter' && fetchReports()}
                />
                <select className="form-select" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); fetchReports(); }}>
                  <option value="">All Statuses</option>
                  <option value="DRAFT">DRAFT</option>
                  <option value="SUBMITTED">SUBMITTED</option>
                  <option value="SIGNED">SIGNED (Locked)</option>
                  <option value="REJECTED">REJECTED</option>
                </select>
                <select className="form-select" value={classFilter} onChange={(e) => { setClassFilter(e.target.value); fetchReports(); }}>
                  <option value="">All Classes</option>
                  <option value="I">Class I</option>
                  <option value="II">Class II</option>
                  <option value="III">Class III</option>
                  <option value="IIII">Class IIII</option>
                </select>
                <button className="btn btn-secondary" onClick={fetchReports}>Apply Filter</button>
              </div>

              {/* Reports Table */}
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Report No / Ver</th>
                      <th>Instrument Type</th>
                      <th>Class & Capacity</th>
                      <th>Standard</th>
                      <th>Verdict</th>
                      <th>Status</th>
                      <th>Integrity Seal</th>
                      <th>Exports & Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.length === 0 ? (
                      <tr><td colSpan="8" style={{ textAlign: 'center', padding: '24px' }}>No reports found. Click "Seed Synthetic Test Instruments" above to load benchmarks!</td></tr>
                    ) : (
                      reports.map((r) => (
                        <tr key={r.id}>
                          <td>
                            <strong>{r.report_number}</strong>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>v{r.version} • by {r.created_by}</div>
                          </td>
                          <td>
                            <strong>{r.manufacturer}</strong>
                            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>{r.model} (SN: {r.serial_number})</div>
                          </td>
                          <td>
                            <span className="badge" style={{ background: '#1e293b' }}>Class {r.accuracy_class}</span>
                            <div style={{ fontSize: '0.72rem', marginTop: '2px' }}>Max {r.max_capacity} {r.unit}</div>
                          </td>
                          <td>{r.ruleset_id} ({r.ruleset_edition})</td>
                          <td>
                            <span className={`badge ${r.overall_verdict === 'PASS' ? 'badge-pass' : 'badge-fail'}`}>
                              {r.overall_verdict}
                            </span>
                          </td>
                          <td>
                            <span className={`badge badge-${r.status.toLowerCase()}`}>
                              {r.status === 'SIGNED' ? '🔒 SIGNED' : r.status}
                            </span>
                          </td>
                          <td>
                            {r.canonical_hash ? (
                              <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => setQrModalReport(r)}
                                title="Inspect SHA-256 seal & verification QR code"
                              >
                                🛡️ SHA-256 & QR
                              </button>
                            ) : (
                              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Unsigned Draft</span>
                            )}
                          </td>
                          <td>
                            <div style={{ display: 'flex', gap: '6px' }}>
                              <a className="btn btn-secondary btn-sm" href={`${API_BASE}/reports/${r.id}/export/pdf`} target="_blank" rel="noreferrer">
                                📄 PDF
                              </a>
                              <a className="btn btn-secondary btn-sm" href={`${API_BASE}/reports/${r.id}/export/docx`} target="_blank" rel="noreferrer">
                                📝 DOCX
                              </a>
                              <a className="btn btn-secondary btn-sm" href={`${API_BASE}/reports/${r.id}/export/json`} target="_blank" rel="noreferrer">
                                ⚙️ JSON
                              </a>
                              {r.status === 'SUBMITTED' && (currentUser.role === 'reviewer' || currentUser.role === 'admin') && (
                                <button className="btn btn-primary btn-sm" onClick={() => setReviewModalReport(r)}>
                                  ✍️ Sign / Reject
                                </button>
                              )}
                              {(r.status === 'SIGNED' || r.status === 'REJECTED') && (
                                <button className="btn btn-secondary btn-sm" onClick={() => branchNewVersion(r.id)} title="Branch into new version">
                                  🌿 Branch v{r.version + 1}
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ══════════════════════════════════════════════════════════════
            TAB 2: LIVE METROLOGY WORKBENCH
        ══════════════════════════════════════════════════════════════ */}
        {activeTab === 'workbench' && (
          <div>
            {/* Presets Bar */}
            <div className="card" style={{ background: '#111827' }}>
              <div className="card-header" style={{ paddingBottom: '8px', marginBottom: '8px' }}>
                <span className="card-title">⚡ Synthetic Metrological Benchmarks</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Pre-populate standard instruments conforming to OIML R 76-1:</span>
              </div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <button className="btn btn-secondary btn-sm" onClick={() => { loadPreset('6kg_class_iii'); setTimeout(runLiveEvaluation, 100); }}>
                  🛒 6 kg / 2 g Class III Retail Scale (PASS)
                </button>
                <button className="btn btn-secondary btn-sm" onClick={() => { loadPreset('600g_class_ii'); setTimeout(runLiveEvaluation, 100); }}>
                  🔬 600 g / 0.01 g Class II Lab Balance (PASS)
                </button>
                <button className="btn btn-secondary btn-sm" onClick={() => { loadPreset('30t_class_iii'); setTimeout(runLiveEvaluation, 100); }}>
                  🚛 30 t / 10 kg Class III Weighbridge (PASS)
                </button>
                <button className="btn btn-danger btn-sm" onClick={() => { loadPreset('failing_scale'); setTimeout(runLiveEvaluation, 100); }}>
                  ❌ Deliberate Failing Scale (MPE & Eccentricity Violations)
                </button>
              </div>
            </div>

            {/* Master Data Section */}
            <div className="card">
              <div className="card-header">
                <div>
                  <div className="card-title">1. Instrument Master Data & Plausibility Evaluation</div>
                  <div className="card-subtitle">OIML R 76-1 Clause 3.2, 3.4 & Table 3/4 verification rules</div>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <select
                    className="form-select"
                    value={activeRulesetId}
                    onChange={(e) => { setActiveRulesetId(e.target.value); setTimeout(runLiveEvaluation, 100); }}
                  >
                    {rulesets.map((r) => (
                      <option key={r.ruleset_id} value={r.ruleset_id}>{r.ruleset_id} ({r.edition})</option>
                    ))}
                  </select>
                  <button className="btn btn-primary btn-sm" onClick={runLiveEvaluation}>🔄 Re-Evaluate</button>
                </div>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Report Number</label>
                  <input type="text" className="form-input" value={reportNumber} onChange={(e) => setReportNumber(e.target.value)} />
                </div>
                <div className="form-group">
                  <label className="form-label">Manufacturer</label>
                  <input type="text" className="form-input" value={instrument.manufacturer} onChange={(e) => setInstrument({ ...instrument, manufacturer: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Model</label>
                  <input type="text" className="form-input" value={instrument.model} onChange={(e) => setInstrument({ ...instrument, model: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Serial Number</label>
                  <input type="text" className="form-input" value={instrument.serial_number} onChange={(e) => setInstrument({ ...instrument, serial_number: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Accuracy Class</label>
                  <select className="form-select" value={instrument.accuracy_class} onChange={(e) => setInstrument({ ...instrument, accuracy_class: e.target.value })}>
                    <option value="I">Class I (Special)</option>
                    <option value="II">Class II (High)</option>
                    <option value="III">Class III (Medium)</option>
                    <option value="IIII">Class IIII (Ordinary)</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Max Capacity</label>
                  <input type="number" className="form-input" value={instrument.max_capacity} onChange={(e) => setInstrument({ ...instrument, max_capacity: parseFloat(e.target.value) })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Min Capacity</label>
                  <input type="number" className="form-input" value={instrument.min_capacity} onChange={(e) => setInstrument({ ...instrument, min_capacity: parseFloat(e.target.value) })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Verification Scale Interval (e)</label>
                  <input type="number" step="any" className="form-input" value={instrument.verification_scale_interval_e} onChange={(e) => setInstrument({ ...instrument, verification_scale_interval_e: parseFloat(e.target.value) })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Actual Scale Interval (d)</label>
                  <input type="number" step="any" className="form-input" value={instrument.actual_scale_interval_d} onChange={(e) => setInstrument({ ...instrument, actual_scale_interval_d: parseFloat(e.target.value) })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Mass Unit</label>
                  <select className="form-select" value={instrument.unit} onChange={(e) => setInstrument({ ...instrument, unit: e.target.value })}>
                    <option value="g">g (Grams)</option>
                    <option value="kg">kg (Kilograms)</option>
                    <option value="mg">mg (Milligrams)</option>
                    <option value="t">t (Tonnes)</option>
                  </select>
                </div>
              </div>

              {/* Plausibility Diagnostics */}
              {plausibilityResult && (
                <div style={{ marginTop: '16px', padding: '12px', background: '#111827', borderRadius: 'var(--radius)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <strong>Plausibility Checks (Calculated n = {plausibilityResult.calculated_n}):</strong>
                    <span className={`badge ${plausibilityResult.is_valid ? 'badge-pass' : 'badge-fail'}`}>
                      {plausibilityResult.summary_verdict}
                    </span>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '8px' }}>
                    {plausibilityResult.checks.map((chk, idx) => (
                      <div key={idx} style={{ padding: '6px 10px', background: '#1f2937', borderRadius: '4px', borderLeft: `3px solid ${chk.passed ? '#10b981' : '#ef4444'}` }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                          <span style={{ fontWeight: 600 }}>{chk.check_name}</span>
                          <span style={{ color: chk.passed ? '#34d399' : '#f87171' }}>{chk.passed ? 'PASS' : 'FAIL'}</span>
                        </div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{chk.message}</div>
                        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{chk.clause}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Weighing Performance Test Table */}
            <div className="card">
              <div className="card-header">
                <div>
                  <div className="card-title">2. Weighing Performance Test (OIML R 76-2 Form 1)</div>
                  <div className="card-subtitle">Changeover calculation P = I + 0.5e - ΔL, Error E = P - L, Corrected Ec = E - E0</div>
                </div>
                {weighingEval && (
                  <span className={`badge ${weighingEval.overall_verdict === 'PASS' ? 'badge-pass' : 'badge-fail'}`}>
                    Test Verdict: {weighingEval.overall_verdict}
                  </span>
                )}
              </div>

              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Direction</th>
                      <th>Load L ({instrument.unit})</th>
                      <th>Indication I ({instrument.unit})</th>
                      <th>Add. Load ΔL ({instrument.unit})</th>
                      <th>Turning P ({instrument.unit})</th>
                      <th>Error E ({instrument.unit})</th>
                      <th>Corrected Ec ({instrument.unit})</th>
                      <th>MPE ({instrument.unit})</th>
                      <th>Verdict</th>
                    </tr>
                  </thead>
                  <tbody>
                    {weighingEval ? (
                      weighingEval.points.map((pt, i) => (
                        <tr key={i}>
                          <td>{pt.direction}</td>
                          <td><strong>{pt.load}</strong></td>
                          <td>{pt.indicated}</td>
                          <td>{pt.delta_load !== null ? pt.delta_load : '-'}</td>
                          <td>{pt.turning_indication_p}</td>
                          <td>{pt.uncorrected_error_e}</td>
                          <td><strong>{pt.corrected_error_ec}</strong></td>
                          <td>±{pt.mpe}</td>
                          <td>
                            <span className={`badge ${pt.verdict === 'PASS' ? 'badge-pass' : 'badge-fail'}`}>{pt.verdict}</span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr><td colSpan="9">Click "Re-Evaluate" to compute results.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* Show explainable proof for the first 2 points */}
              {weighingEval && weighingEval.points.length > 0 && (
                <div style={{ marginTop: '12px' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Explainable Verdict Mathematical Proof (INNOVATION B):</div>
                  <div className="proof-box">{weighingEval.points[1]?.explanation || weighingEval.points[0]?.explanation}</div>
                </div>
              )}
            </div>

            {/* Eccentricity Test Table */}
            <div className="card">
              <div className="card-header">
                <div>
                  <div className="card-title">3. Eccentricity Test (OIML R 76-2 Form 3)</div>
                  <div className="card-subtitle">Recommended load: 1/3 Max for 4 supports (Clause 3.6.2 & A.4.7)</div>
                </div>
                {eccentricityEval && (
                  <span className={`badge ${eccentricityEval.overall_verdict === 'PASS' ? 'badge-pass' : 'badge-fail'}`}>
                    Test Verdict: {eccentricityEval.overall_verdict}
                  </span>
                )}
              </div>

              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Position ID</th>
                      <th>Description</th>
                      <th>Load L ({instrument.unit})</th>
                      <th>Indication I ({instrument.unit})</th>
                      <th>ΔL ({instrument.unit})</th>
                      <th>Error E</th>
                      <th>Corrected Ec</th>
                      <th>MPE</th>
                      <th>Verdict</th>
                    </tr>
                  </thead>
                  <tbody>
                    {eccentricityEval ? (
                      eccentricityEval.positions.map((p, i) => (
                        <tr key={i}>
                          <td><strong>{p.position_id}</strong></td>
                          <td>{p.description}</td>
                          <td>{p.load}</td>
                          <td>{p.indicated}</td>
                          <td>{p.delta_load !== null ? p.delta_load : '-'}</td>
                          <td>{p.uncorrected_error_e}</td>
                          <td><strong>{p.corrected_error_ec}</strong></td>
                          <td>±{p.mpe}</td>
                          <td>
                            <span className={`badge ${p.verdict === 'PASS' ? 'badge-pass' : 'badge-fail'}`}>{p.verdict}</span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr><td colSpan="9">No eccentricity data.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Repeatability Test Table */}
            <div className="card">
              <div className="card-header">
                <div>
                  <div className="card-title">4. Repeatability Test (OIML R 76-2 Form 5)</div>
                  <div className="card-subtitle">Range check: ΔE = Emax - Emin ≤ |mpe| (Clause 3.6.1 & A.4.10)</div>
                </div>
                {repeatabilityEval && (
                  <span className={`badge ${repeatabilityEval.overall_verdict === 'PASS' ? 'badge-pass' : 'badge-fail'}`}>
                    Test Verdict: {repeatabilityEval.overall_verdict}
                  </span>
                )}
              </div>

              {repeatabilityEval && repeatabilityEval.series_evaluations.map((s, idx) => (
                <div key={idx} style={{ marginBottom: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0' }}>
                    <strong>{s.series_name} (Load: {s.target_load} {instrument.unit}, MPE: ±{s.mpe} {instrument.unit})</strong>
                    <span>Spread ΔE = {s.spread_delta_e} {instrument.unit} ({s.spread_verdict})</span>
                  </div>
                  <div className="proof-box">{s.explanation}</div>
                </div>
              ))}
            </div>

            {/* Actions Bar */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button className="btn btn-secondary" onClick={() => submitNewReport(false)}>
                💾 Save as Draft
              </button>
              <button className="btn btn-primary" onClick={() => submitNewReport(true)}>
                🚀 Submit Report for Reviewer Sign-Off
              </button>
            </div>
          </div>
        )}

        {/* ══════════════════════════════════════════════════════════════
            TAB 3: PUBLIC VERIFICATION PORTAL (INNOVATION C)
        ══════════════════════════════════════════════════════════════ */}
        {activeTab === 'verification' && (
          <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <div className="card-header">
              <div>
                <div className="card-title">🛡️ Public Legal Metrology Verification Portal</div>
                <div className="card-subtitle">Verify report authenticity against tamper-evident canonical SHA-256 seal</div>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '20px' }}>
              <div className="form-group">
                <label className="form-label">Report Number</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. REP-2026-6KG-001"
                  value={verifyReportNum}
                  onChange={(e) => setVerifyReportNum(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Expected Canonical SHA-256 Checksum</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="64-character hexadecimal SHA-256 digest"
                  value={verifyHash}
                  onChange={(e) => setVerifyHash(e.target.value)}
                />
              </div>
              <button className="btn btn-primary" onClick={runPublicVerification}>
                🔍 Run Cryptographic Verification
              </button>
            </div>

            {verificationResult && (
              <div style={{
                padding: '20px',
                borderRadius: 'var(--radius)',
                background: verificationResult.valid ? '#064e3b' : '#7f1d1d',
                border: `1px solid ${verificationResult.valid ? '#059669' : '#b91c1c'}`
              }}>
                <h3 style={{ marginBottom: '8px', color: 'white' }}>
                  {verificationResult.valid ? '✅ CERTIFICATE GENUINE & TAMPER-FREE' : '⚠️ VERIFICATION FAILED: TAMPERING DETECTED'}
                </h3>
                <p style={{ fontSize: '0.85rem', color: '#e5e7eb' }}>
                  {verificationResult.valid
                    ? `Report ${verificationResult.report_number} (v${verificationResult.version}) is officially signed by ${verificationResult.reviewer} and locked. Cryptographic digest matches canonical payload exactly.`
                    : `The submitted payload or SHA-256 hash does not match the signed laboratory record! Either the data has been altered or the hash is invalid.`
                  }
                </p>
                {verificationResult.canonical_hash && (
                  <div style={{ marginTop: '10px' }}>
                    <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Canonical Hash on File:</span>
                    <div className="hash-string">{verificationResult.canonical_hash}</div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ══════════════════════════════════════════════════════════════
            TAB 4: VERSIONED RULESETS (INNOVATION A)
        ══════════════════════════════════════════════════════════════ */}
        {activeTab === 'rulesets' && (
          <div>
            <div className="card">
              <div className="card-header">
                <div>
                  <div className="card-title">📜 Schema-Validated Versioned Rulesets (INNOVATION A)</div>
                  <div className="card-subtitle">Zero-code ruleset additions: new editions & classes load dynamically without server redeployment</div>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {rulesets.map((r) => (
                    <button
                      key={r.ruleset_id}
                      className={`btn ${activeRulesetId === r.ruleset_id ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                      onClick={() => fetchRulesetDetails(r.ruleset_id)}
                    >
                      {r.ruleset_id}
                    </button>
                  ))}
                </div>
              </div>

              {rulesetDetails && (
                <div>
                  <div style={{ marginBottom: '16px' }}>
                    <h3>{rulesetDetails.title}</h3>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      Edition: <strong>{rulesetDetails.edition}</strong> | Rounding Mode: <strong>{rulesetDetails.rounding_mode}</strong> | Citation: <i>{rulesetDetails.citation}</i>
                    </div>
                  </div>

                  <h4>Accuracy Classes MPE Bands (Table 6)</h4>
                  <div className="form-grid" style={{ marginTop: '10px' }}>
                    {Object.entries(rulesetDetails.accuracy_classes).map(([cName, cDef]) => (
                      <div key={cName} style={{ background: '#111827', padding: '12px', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
                        <strong style={{ color: 'var(--accent-blue)' }}>Class {cName}: {cDef.name}</strong>
                        <div style={{ fontSize: '0.72rem', marginTop: '6px' }}>
                          <div><strong>Classification Intervals (Table 3):</strong></div>
                          {cDef.classification_intervals.map((ci, idx) => (
                            <div key={idx} style={{ color: 'var(--text-secondary)' }}>
                              • e: {ci.e_min_g}g - {ci.e_max_g ? `${ci.e_max_g}g` : 'inf'}, n in [{ci.n_min}, {ci.n_max || 'inf'}], Min = {ci.min_capacity_multiplier_e}e
                            </div>
                          ))}
                          <div style={{ marginTop: '6px' }}><strong>Initial MPE Bands (Table 6):</strong></div>
                          {cDef.mpe_bands_initial.map((b, idx) => (
                            <div key={idx} style={{ color: 'var(--text-secondary)' }}>
                              • {b.m_min_e}e &lt; m &le; {b.m_max_e ? `${b.m_max_e}e` : 'inf'} &rarr; ±{b.mpe_multiplier_e}e
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ══════════════════════════════════════════════════════════════
            TAB 5: AUDIT TRAIL LOG
        ══════════════════════════════════════════════════════════════ */}
        {activeTab === 'audit' && (
          <div className="card">
            <div className="card-header">
              <div>
                <div className="card-title">🔍 Immutable Audit Trail Log</div>
                <div className="card-subtitle">Traceable cryptographic event stream tracking all logins, evaluations, sign-offs, and ruleset operations</div>
              </div>
              <button className="btn btn-secondary btn-sm" onClick={fetchAuditLogs}>🔄 Refresh Logs</button>
            </div>

            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Timestamp (UTC)</th>
                    <th>User</th>
                    <th>Role</th>
                    <th>Action</th>
                    <th>Target Entity</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.length === 0 ? (
                    <tr><td colSpan="6" style={{ textAlign: 'center', padding: '20px' }}>No audit records found.</td></tr>
                  ) : (
                    auditLogs.map((l) => (
                      <tr key={l.id}>
                        <td style={{ fontFamily: 'monospace' }}>{l.timestamp ? l.timestamp.replace('T', ' ').slice(0, 19) : ''}</td>
                        <td><strong>{l.username}</strong></td>
                        <td><span className="badge" style={{ background: '#1e293b' }}>{l.role}</span></td>
                        <td><span className="badge badge-signed">{l.action}</span></td>
                        <td>{l.entity_type} {l.entity_id ? `(#${l.entity_id})` : ''}</td>
                        <td style={{ fontSize: '0.72rem', fontFamily: 'monospace', maxWidth: '300px', wordBreak: 'break-all' }}>
                          {l.details ? JSON.stringify(l.details) : '-'}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* ─── MODAL: QR CODE & DIGITAL SEAL ─── */}
      {qrModalReport && (
        <div className="modal-overlay" onClick={() => setQrModalReport(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="card-header">
              <span className="card-title">🛡️ Cryptographic Tamper-Evident Seal</span>
              <button className="btn btn-secondary btn-sm" onClick={() => setQrModalReport(null)}>✕ Close</button>
            </div>
            <div className="seal-container">
              <div className="seal-qr">
                {qrModalReport.qr_data_uri ? (
                  <img src={qrModalReport.qr_data_uri} alt="Verification QR Code" style={{ width: '100px', height: '100px' }} />
                ) : (
                  <span>No QR</span>
                )}
              </div>
              <div className="seal-details">
                <h4>{qrModalReport.report_number} (Version {qrModalReport.version})</h4>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  Status: <strong>{qrModalReport.status}</strong> | Verdict: <strong>{qrModalReport.overall_verdict}</strong>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>SHA-256 Canonical Fingerprint:</div>
                <div className="hash-string">{qrModalReport.canonical_hash}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
                  Verification URL: <code>https://weighproof.org/verify/{qrModalReport.report_number}?hash={qrModalReport.canonical_hash}</code>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ─── MODAL: REVIEWER SIGN-OFF ─── */}
      {reviewModalReport && (
        <div className="modal-overlay" onClick={() => setReviewModalReport(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
            <div className="card-header">
              <span className="card-title">✍️ Reviewer Pattern Approval Sign-Off</span>
              <button className="btn btn-secondary btn-sm" onClick={() => setReviewModalReport(null)}>✕ Close</button>
            </div>
            <div>
              <p style={{ fontSize: '0.85rem', marginBottom: '12px' }}>
                You are reviewing <strong>{reviewModalReport.report_number}</strong> for <strong>{reviewModalReport.manufacturer} {reviewModalReport.model}</strong>.
              </p>
              <div className="form-group" style={{ marginBottom: '16px' }}>
                <label className="form-label">Reviewer Notes / Certification Comments</label>
                <textarea
                  className="form-textarea"
                  rows="4"
                  placeholder="Enter endorsement rationale or deficiency notes..."
                  value={reviewerComment}
                  onChange={(e) => setReviewerComment(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button className="btn btn-danger" onClick={() => rejectReportAction(reviewModalReport.id)}>
                  ❌ Reject Report
                </button>
                <button className="btn btn-success" onClick={() => signReportAction(reviewModalReport.id)}>
                  🔒 Approve, Sign & Seal Report
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
