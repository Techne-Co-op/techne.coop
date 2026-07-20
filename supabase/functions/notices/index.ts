// notices · X-02 · Notices v1
// Transactional email for the admission path: when a
// membership.applied event lands, the applicant receives an
// acknowledgment and the steward an intake notice.
//
// Rail (X-02 decision, 2026-07-20): Resend free tier, one seam. To
// change senders, change send() and nothing else. Secrets live in
// Supabase function secrets (reference, not value):
//   RESEND_API_KEY   the sender credential
//   NOTICES_FROM     e.g. "Techne <notices@techne.coop>" (domain
//                    verified in Resend first)
//   STEWARD_EMAIL    intake notices per Bylaws §1.3.3
//
// The applicant address is read from the event payload (email), then
// from the application row it references. If neither carries one, the
// steward notice still goes out, naming the gap.

import { createClient } from "npm:@supabase/supabase-js@2";

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";
const NOTICES_FROM = Deno.env.get("NOTICES_FROM") ?? "";
const STEWARD_EMAIL = Deno.env.get("STEWARD_EMAIL") ?? "";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

async function send(to: string, subject: string, text: string) {
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ from: NOTICES_FROM, to: [to], subject, text }),
  });
  if (!r.ok) {
    throw new Error(`resend ${r.status}: ${await r.text()}`);
  }
}

Deno.serve(async (req) => {
  try {
    const { event } = await req.json();
    if (!event || event.kind !== "membership.applied") {
      return new Response(JSON.stringify({ ok: true, skipped: true }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    const sb = createClient(SUPABASE_URL, SERVICE_KEY);
    const payload = event.payload ?? {};

    // who applied, for the notice text
    let displayName = "an applicant";
    if (event.agent_id) {
      const { data: agent } = await sb.from("agents")
        .select("display_name").eq("id", event.agent_id).single();
      if (agent?.display_name) displayName = agent.display_name;
    }

    // where to reach them: payload first, application row second
    let email: string | null =
      typeof payload.email === "string" && payload.email.includes("@")
        ? payload.email
        : null;
    if (!email && payload.application_id) {
      const { data: app } = await sb.from("applications")
        .select("note").eq("id", payload.application_id).single();
      const m = app?.note?.match(/[^\s]+@[^\s]+\.[^\s]+/);
      if (m) email = m[0];
    }

    const results: Record<string, string> = {};

    if (email) {
      await send(
        email,
        "Your application to RegenHub was received",
        [
          `Hello ${displayName},`,
          "",
          "Your membership application was received and recorded.",
          "A steward will be in touch at this address. Admission is",
          "decided by the Board; you will hear the outcome the same way.",
          "",
          "RegenHub, LCA · Boulder, Colorado",
          "techne.coop",
        ].join("\n"),
      );
      results.applicant = email;
    } else {
      results.applicant = "no address found; steward notified of the gap";
    }

    if (STEWARD_EMAIL) {
      await send(
        STEWARD_EMAIL,
        `New membership application: ${displayName}`,
        [
          `${displayName} applied for membership.`,
          "",
          `event: ${event.id}`,
          `agent: ${event.agent_id ?? "unknown"}`,
          `applicant address: ${email ?? "NOT FOUND -- check the application record"}`,
          "",
          "Intake per Bylaws 1.3.3; admission is the Board's decision.",
        ].join("\n"),
      );
      results.steward = STEWARD_EMAIL;
    }

    return new Response(JSON.stringify({ ok: true, sent: results }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    // the boundary rule: log the detail, return a quiet failure
    console.error("[techne:notices]", err);
    return new Response(JSON.stringify({ ok: false }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
});
