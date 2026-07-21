import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  Building2,
  CheckCircle2,
  CircleAlert,
  ExternalLink,
  Globe2,
  KeyRound,
  RefreshCcw,
  Save,
  Search,
  ShieldCheck,
  Trash2,
  UserRound,
  UsersRound,
} from "lucide-react";
import {
  brandOpsUrl,
  isAssigned,
  statusText,
  staticRowsFromIndex,
  summaryFromRows,
} from "./brandDirectorRoster.js";
import {
  availableBooksSummary,
  loadDeliveryForBrand,
} from "./brandDirectorAvailability.js";

const FALLBACK_SUMMARY = {
  total: 0,
  assigned: 0,
  unassigned: 0,
  active: 0,
  inactive: 0,
  wizard_ready: 0,
  ops_ready: 0,
};

function withCanonicalOpsUrls(brands) {
  return (brands || []).map((row) => ({
    ...row,
    ops_url: brandOpsUrl(row.brand_id),
  }));
}

function MetricCard({ icon: Icon, label, value, tone = "neutral" }) {
  return (
    <section className={`director-metric director-metric--${tone}`}>
      <div className="director-metric__icon">
        <Icon size={18} aria-hidden="true" />
      </div>
      <div>
        <p>{label}</p>
        <strong>{Number(value || 0).toLocaleString()}</strong>
      </div>
    </section>
  );
}

function Pill({ tone = "neutral", children }) {
  return <span className={`director-pill director-pill--${tone}`}>{children}</span>;
}

function AccessLink({ href, label, available }) {
  return (
    <a
      className={`director-access ${available ? "director-access--on" : "director-access--off"}`}
      href={href}
      aria-disabled={!available}
      onClick={(event) => {
        if (!available) event.preventDefault();
      }}
    >
      <span>{label}</span>
      {available ? <ExternalLink size={14} aria-hidden="true" /> : <CircleAlert size={14} aria-hidden="true" />}
    </a>
  );
}

async function loadDashboard() {
  try {
    const response = await fetch("/api/onboarding/assignments", { cache: "no-store" });
    if (!response.ok) throw new Error(`assignments API ${response.status}`);
    const body = await response.json();
    if (!Array.isArray(body.brands)) throw new Error("assignments API missing brands");
    const brands = withCanonicalOpsUrls(body.brands);
    return {
      mode: "live",
      brands,
      summary: body.summary || summaryFromRows(brands),
      source: body.source || {},
      generatedAt: body.generated_at || "",
      error: "",
    };
  } catch (apiError) {
    const response = await fetch("/brand_admin_brands.json", { cache: "no-store" });
    if (!response.ok) throw apiError;
    const brands = staticRowsFromIndex(await response.json());
    return {
      mode: "static",
      brands,
      summary: summaryFromRows(brands),
      source: { static_brand_count: brands.length, r2_configured: false, r2_overlay_count: 0 },
      generatedAt: "",
      error: "",
    };
  }
}

export default function BrandDirectorDashboard() {
  const [data, setData] = useState({
    mode: "loading",
    brands: [],
    summary: FALLBACK_SUMMARY,
    source: {},
    generatedAt: "",
    error: "",
  });
  const [query, setQuery] = useState("");
  const [lane, setLane] = useState("all");
  const [lifecycle, setLifecycle] = useState("all");
  const [assignment, setAssignment] = useState("all");
  const [refreshing, setRefreshing] = useState(false);
  const [selectedBrandId, setSelectedBrandId] = useState("");
  const [adminToken, setAdminToken] = useState(() => {
    try {
      return sessionStorage.getItem("phoenix_brand_director_admin_token") || "";
    } catch (_) {
      return "";
    }
  });
  const [adminName, setAdminName] = useState("");
  const [adminDirectorId, setAdminDirectorId] = useState("");
  const [adminBusy, setAdminBusy] = useState(false);
  const [adminNotice, setAdminNotice] = useState("");
  const [availableBooks, setAvailableBooks] = useState({
    count: 0,
    assets: [],
    empty: true,
    empty_label: "No titles available yet",
    loading: false,
  });

  const refresh = async () => {
    setRefreshing(true);
    try {
      setData(await loadDashboard());
    } catch (error) {
      setData((current) => ({
        ...current,
        mode: "error",
        error: error.message || "dashboard unavailable",
      }));
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  useEffect(() => {
    try {
      if (adminToken) sessionStorage.setItem("phoenix_brand_director_admin_token", adminToken);
      else sessionStorage.removeItem("phoenix_brand_director_admin_token");
    } catch (_) {}
  }, [adminToken]);

  const lanes = useMemo(
    () => Array.from(new Set(data.brands.map((row) => row.lane).filter(Boolean))).sort(),
    [data.brands],
  );

  const visibleRows = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return data.brands.filter((row) => {
      const haystack = [
        row.brand_id,
        row.base_brand,
        row.display_brand,
        row.lane,
        row.teacher,
        row.brand_director_name,
        row.brand_director_id,
      ]
        .join(" ")
        .toLowerCase();
      if (needle && !haystack.includes(needle)) return false;
      if (lane !== "all" && row.lane !== lane) return false;
      if (lifecycle !== "all" && String(row.lifecycle).toLowerCase() !== lifecycle) return false;
      if (assignment === "assigned" && !isAssigned(row)) return false;
      if (assignment === "unassigned" && isAssigned(row)) return false;
      return true;
    });
  }, [assignment, data.brands, lane, lifecycle, query]);

  const selectedRow = useMemo(
    () => data.brands.find((row) => row.brand_id === selectedBrandId) || visibleRows[0] || null,
    [data.brands, selectedBrandId, visibleRows],
  );

  useEffect(() => {
    if (!selectedRow) {
      setAdminName("");
      setAdminDirectorId("");
      return;
    }
    setAdminName(selectedRow.brand_director_name || "");
    setAdminDirectorId(selectedRow.brand_director_id || "");
  }, [selectedRow?.brand_id]);

  useEffect(() => {
    let cancelled = false;
    if (!selectedRow?.brand_id) {
      setAvailableBooks({
        count: 0,
        assets: [],
        empty: true,
        empty_label: "No titles available yet",
        loading: false,
      });
      return undefined;
    }
    setAvailableBooks((current) => ({ ...current, loading: true }));
    loadDeliveryForBrand(selectedRow.brand_id).then((delivery) => {
      if (cancelled) return;
      const summary = availableBooksSummary(delivery);
      setAvailableBooks({ ...summary, loading: false });
    });
    return () => {
      cancelled = true;
    };
  }, [selectedRow?.brand_id]);

  const attentionRows = useMemo(
    () => data.brands.filter((row) => row.active && !isAssigned(row)).slice(0, 8),
    [data.brands],
  );
  const recentRows = useMemo(
    () =>
      data.brands
        .filter((row) => isAssigned(row))
        .sort((a, b) => String(b.assigned_at || "").localeCompare(String(a.assigned_at || "")))
        .slice(0, 6),
    [data.brands],
  );
  const adminConfigured = Boolean(data.source.admin_actions_configured);
  const adminUnlocked = adminConfigured && Boolean(adminToken.trim());
  const selectedIsPromoted = selectedRow?.assignment_source === "brand_admin_brands";

  const runAdminAction = async (action) => {
    if (!selectedRow || !adminUnlocked) return;
    setAdminBusy(true);
    setAdminNotice("");
    try {
      const payload = { action, brand_id: selectedRow.brand_id };
      if (action === "assign" || action === "reassign") {
        payload.brand_director_name = adminName.trim();
        payload.brand_director_id = adminDirectorId.trim();
      }
      const response = await fetch("/api/onboarding/assignments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Admin-Token": adminToken.trim(),
        },
        body: JSON.stringify(payload),
      });
      let body = {};
      try {
        body = await response.json();
      } catch (_) {}
      if (!response.ok) {
        throw new Error(body.detail || body.error || `admin action failed (${response.status})`);
      }
      setAdminNotice(`${statusText(action)} complete for ${selectedRow.brand_id}.`);
      await refresh();
    } catch (error) {
      setAdminNotice(error.message || "Admin action failed.");
    } finally {
      setAdminBusy(false);
    }
  };

  return (
    <main className="director-dashboard">
      <header className="director-hero">
        <div>
          <p className="director-kicker">Pearl Prime Operations</p>
          <h1>Brand Director Command</h1>
          <p className="director-subtitle">
            {data.summary.total.toLocaleString()} brand lanes across global channels.
          </p>
        </div>
        <div className="director-hero__status">
          <Pill tone={data.mode === "live" ? "good" : data.mode === "static" ? "warn" : "neutral"}>
            {data.mode === "live" ? "Live overlay" : data.mode === "static" ? "Static fallback" : "Loading"}
          </Pill>
          <button className="director-refresh" type="button" onClick={refresh} disabled={refreshing}>
            <RefreshCcw size={16} aria-hidden="true" />
            <span>{refreshing ? "Refreshing" : "Refresh"}</span>
          </button>
        </div>
      </header>

      <section className="director-metrics" aria-label="Brand director summary">
        <MetricCard icon={Building2} label="Total brands" value={data.summary.total} />
        <MetricCard icon={UsersRound} label="Assigned" value={data.summary.assigned} tone="good" />
        <MetricCard icon={CircleAlert} label="Needs director" value={data.summary.unassigned} tone="warn" />
        <MetricCard icon={Activity} label="Active lanes" value={data.summary.active} />
        <MetricCard icon={ShieldCheck} label="Wizard ready" value={data.summary.wizard_ready} tone="good" />
        <MetricCard icon={Globe2} label="Ops ready" value={data.summary.ops_ready} tone="good" />
      </section>

      <section className="director-toolbar" aria-label="Filters">
        <label className="director-search">
          <Search size={17} aria-hidden="true" />
          <input
            type="search"
            placeholder="Search brand, director, lane"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
        <select value={lane} onChange={(event) => setLane(event.target.value)} aria-label="Lane filter">
          <option value="all">All lanes</option>
          {lanes.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        <select value={lifecycle} onChange={(event) => setLifecycle(event.target.value)} aria-label="Lifecycle filter">
          <option value="all">All lifecycle</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <select value={assignment} onChange={(event) => setAssignment(event.target.value)} aria-label="Assignment filter">
          <option value="all">All assignments</option>
          <option value="assigned">Assigned</option>
          <option value="unassigned">Unassigned</option>
        </select>
      </section>

      {data.error ? <p className="director-notice">{data.error}</p> : null}

      <div className="director-layout">
        <section className="director-table-panel">
          <div className="director-table-head">
            <div>
              <h2>Global Brand Roster</h2>
              <p>{visibleRows.length.toLocaleString()} visible rows</p>
            </div>
            <Pill>{data.source.r2_overlay_count || 0} live overlays</Pill>
          </div>
          <div className="director-table-wrap">
            <table className="director-table">
              <thead>
                <tr>
                  <th>Brand</th>
                  <th>Market</th>
                  <th>Director</th>
                  <th>Lifecycle</th>
                  <th>Wizard</th>
                  <th>Ops</th>
                  <th>Source</th>
                  <th>Admin</th>
                </tr>
              </thead>
              <tbody>
                {visibleRows.map((row) => (
                  <tr key={row.brand_id} className={selectedRow?.brand_id === row.brand_id ? "director-row--selected" : ""}>
                    <td>
                      <div className="director-brand-cell">
                        <strong>{row.display_brand}</strong>
                        <span>{row.brand_id}</span>
                      </div>
                    </td>
                    <td>
                      <div className="director-market-cell">
                        <Pill>{row.lane || "n/a"}</Pill>
                        <span>{row.is_teacher ? row.teacher || "Teacher lane" : row.base_brand}</span>
                      </div>
                    </td>
                    <td>
                      {isAssigned(row) ? (
                        <div className="director-person">
                          <UserRound size={16} aria-hidden="true" />
                          <div>
                            <strong>{row.brand_director_name}</strong>
                            <span>{row.brand_director_id || "director"}</span>
                          </div>
                        </div>
                      ) : (
                        <Pill tone="warn">Unassigned</Pill>
                      )}
                    </td>
                    <td>
                      <Pill tone={row.active ? "good" : "neutral"}>{statusText(row.lifecycle)}</Pill>
                    </td>
                    <td>
                      <AccessLink href={row.wizard_url} label="Wizard" available={row.wizard_access === "available"} />
                    </td>
                    <td>
                      <AccessLink href={row.ops_url} label="Ops" available={row.ops_access === "available"} />
                    </td>
                    <td>
                      <span className="director-source">{statusText(row.assignment_source)}</span>
                    </td>
                    <td>
                      <button
                        className="director-mini-button"
                        type="button"
                        onClick={() => setSelectedBrandId(row.brand_id)}
                      >
                        Select
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="director-side">
          <section className="director-side-card">
            <div className="director-side-card__title">
              <KeyRound size={17} aria-hidden="true" />
              <h2>Admin Actions</h2>
            </div>
            <div className="director-admin-form">
              <label>
                <span>Token</span>
                <input
                  type="password"
                  value={adminToken}
                  onChange={(event) => setAdminToken(event.target.value)}
                  placeholder={adminConfigured ? "Paste admin token" : "Admin token not configured"}
                  disabled={!adminConfigured}
                />
              </label>
              <div className="director-selected-brand" data-testid="selected-brand">
                <strong>{selectedRow?.display_brand || "No brand selected"}</strong>
                <span>{selectedRow ? `${selectedRow.brand_id} · ${selectedRow.lane || "n/a"}` : "Select a row"}</span>
              </div>
              <div
                className="director-selected-brand"
                data-testid="available-books"
                data-available-count={availableBooks.count}
                data-available-empty={availableBooks.empty ? "true" : "false"}
              >
                <strong>Downloadable titles</strong>
                <span>
                  {availableBooks.loading
                    ? "Checking real assets…"
                    : availableBooks.empty
                      ? availableBooks.empty_label
                      : `${availableBooks.count} real downloadable asset${availableBooks.count === 1 ? "" : "s"}`}
                </span>
                {selectedRow?.ops_url ? (
                  <AccessLink href={selectedRow.ops_url} label="Open ops" available />
                ) : null}
              </div>
              <label>
                <span>Director name</span>
                <input
                  type="text"
                  value={adminName}
                  onChange={(event) => setAdminName(event.target.value)}
                  placeholder="Name for live assignment"
                  disabled={!adminUnlocked || selectedIsPromoted}
                />
              </label>
              <label>
                <span>Director ID</span>
                <input
                  type="text"
                  value={adminDirectorId}
                  onChange={(event) => setAdminDirectorId(event.target.value)}
                  placeholder="auto from name"
                  disabled={!adminUnlocked || selectedIsPromoted}
                />
              </label>
              <div className="director-admin-actions">
                <button
                  className="director-admin-button"
                  type="button"
                  disabled={!adminUnlocked || !selectedRow || selectedIsPromoted || !adminName.trim() || adminBusy}
                  onClick={() => runAdminAction(isAssigned(selectedRow) ? "reassign" : "assign")}
                >
                  <Save size={15} aria-hidden="true" />
                  <span>{isAssigned(selectedRow) ? "Reassign" : "Assign"}</span>
                </button>
                <button
                  className="director-admin-button director-admin-button--danger"
                  type="button"
                  disabled={!adminUnlocked || !selectedRow || selectedIsPromoted || !isAssigned(selectedRow) || adminBusy}
                  onClick={() => runAdminAction("release")}
                >
                  <Trash2 size={15} aria-hidden="true" />
                  <span>Release</span>
                </button>
              </div>
              {selectedIsPromoted ? (
                <p className="director-admin-note">Promoted assignments are source-controlled. Change them in the repo.</p>
              ) : null}
              {adminNotice ? <p className="director-admin-note">{adminNotice}</p> : null}
            </div>
          </section>

          <section className="director-side-card">
            <div className="director-side-card__title">
              <CircleAlert size={17} aria-hidden="true" />
              <h2>Attention</h2>
            </div>
            {attentionRows.length ? (
              <ul className="director-mini-list">
                {attentionRows.map((row) => (
                  <li key={row.brand_id}>
                    <strong>{row.display_brand}</strong>
                    <span>{row.lane} · {row.brand_id}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="director-empty">All active lanes have directors.</p>
            )}
          </section>

          <section className="director-side-card">
            <div className="director-side-card__title">
              <CheckCircle2 size={17} aria-hidden="true" />
              <h2>Assigned</h2>
            </div>
            {recentRows.length ? (
              <ul className="director-mini-list">
                {recentRows.map((row) => (
                  <li key={row.brand_id}>
                    <strong>{row.brand_director_name}</strong>
                    <span>{row.display_brand} · {row.lane}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="director-empty">No directors assigned yet.</p>
            )}
          </section>

          <section className="director-side-card director-side-card--compact">
            <div className="director-side-card__title">
              <ArrowUpRight size={17} aria-hidden="true" />
              <h2>Surface</h2>
            </div>
            <p className="director-source-line">Static: {data.source.static_brand_count || data.brands.length}</p>
            <p className="director-source-line">R2 overlay: {data.source.r2_configured ? "configured" : "not configured"}</p>
            {data.generatedAt ? <p className="director-source-line">Updated: {new Date(data.generatedAt).toLocaleString()}</p> : null}
          </section>
        </aside>
      </div>
    </main>
  );
}
