import { useEffect, useState } from "react";
import { ClipboardList, Loader2, RefreshCw, ShieldCheck } from "lucide-react";

export default function TeacherOperatorQueue() {
  const [state, setState] = useState({ status: "loading", data: null, error: null });

  const load = async () => {
    setState({ status: "loading", data: null, error: null });
    try {
      const response = await fetch("/api/teacher-onboarding/queue");
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        setState({ status: "error", data: null, error: body.detail || `HTTP ${response.status}` });
        return;
      }
      setState({ status: "ok", data: body, error: null });
    } catch (err) {
      setState({ status: "error", data: null, error: err.message });
    }
  };

  useEffect(() => {
    load();
  }, []);

  const drafts = state.data?.drafts || [];
  const submissions = state.data?.submissions || [];

  return (
    <main className="min-h-screen bg-[#0e0a06] text-stone-100">
      <div className="mx-auto max-w-5xl px-4 py-8">
        <header className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-[10px] uppercase tracking-[0.2em] text-amber-500">Pearl Prime · Operator</div>
            <h1 className="mt-2 text-3xl">Teacher portal queue</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-stone-400">
              Read-only pending drafts and submissions. Production atoms are never created here
              (<code className="text-amber-500/90">production_atoms_created: false</code>).
            </p>
          </div>
          <button
            type="button"
            onClick={load}
            className="inline-flex items-center gap-2 rounded-md border border-amber-800/40 px-4 py-2 text-sm text-amber-400 hover:border-amber-500"
          >
            {state.status === "loading" ? <Loader2 className="animate-spin" size={16} /> : <RefreshCw size={16} />}
            Refresh
          </button>
        </header>

        <div className="mb-6 rounded-md border border-amber-900/30 bg-[#1c1009]/70 p-4 text-sm text-stone-300">
          <div className="flex items-center gap-2 text-amber-500">
            <ShieldCheck size={16} />
            Intake-queue only · operator review required
          </div>
          {state.data?.counts ? (
            <div className="mt-2 text-stone-400">
              {state.data.counts.drafts} drafts · {state.data.counts.submissions} submissions
              {state.data.mock ? " · local mock store" : ""}
            </div>
          ) : null}
        </div>

        {state.status === "error" ? (
          <div className="rounded-md border border-red-900/50 bg-red-950/30 p-4 text-sm text-red-200">
            {state.error}
          </div>
        ) : null}

        <section className="mb-10">
          <h2 className="mb-3 flex items-center gap-2 text-xl">
            <ClipboardList size={18} className="text-amber-500" />
            Drafts
          </h2>
          <div className="overflow-hidden rounded-lg border border-amber-900/25">
            <table className="w-full text-left text-sm">
              <thead className="bg-black/30 text-[11px] uppercase tracking-[0.14em] text-stone-500">
                <tr>
                  <th className="px-3 py-2">Teacher</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Updated</th>
                  <th className="px-3 py-2">Draft id</th>
                </tr>
              </thead>
              <tbody>
                {drafts.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-3 py-4 text-stone-500">
                      No drafts in queue.
                    </td>
                  </tr>
                ) : (
                  drafts.map((row) => (
                    <tr key={row.draft_id} className="border-t border-amber-900/20">
                      <td className="px-3 py-3">{row.teacher_name || "—"}</td>
                      <td className="px-3 py-3 text-amber-400">{row.status}</td>
                      <td className="px-3 py-3 text-stone-400">{row.updated_at || "—"}</td>
                      <td className="px-3 py-3 font-mono text-xs text-stone-500">{row.draft_id}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section>
          <h2 className="mb-3 text-xl">Submissions</h2>
          <div className="overflow-hidden rounded-lg border border-amber-900/25">
            <table className="w-full text-left text-sm">
              <thead className="bg-black/30 text-[11px] uppercase tracking-[0.14em] text-stone-500">
                <tr>
                  <th className="px-3 py-2">Teacher</th>
                  <th className="px-3 py-2">Received</th>
                  <th className="px-3 py-2">Score</th>
                  <th className="px-3 py-2">Atoms</th>
                  <th className="px-3 py-2">Key</th>
                </tr>
              </thead>
              <tbody>
                {submissions.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-3 py-4 text-stone-500">
                      No submissions yet.
                    </td>
                  </tr>
                ) : (
                  submissions.map((row) => (
                    <tr key={row.key} className="border-t border-amber-900/20">
                      <td className="px-3 py-3">{row.teacher_name || "—"}</td>
                      <td className="px-3 py-3 text-stone-400">{row.received_at || "—"}</td>
                      <td className="px-3 py-3">{row.readiness_score ?? "—"}</td>
                      <td className="px-3 py-3 text-stone-400">
                        {row.server_policy?.production_atoms_created ? "CREATED" : "false"}
                      </td>
                      <td className="px-3 py-3 font-mono text-xs text-stone-500">{row.key}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}
