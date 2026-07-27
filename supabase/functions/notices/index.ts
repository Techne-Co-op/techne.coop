// notices · X-02 · Notices v1
// Transactional notices for the admission path: when a
// membership.applied event lands, the applicant receives an
// acknowledgment and the steward an intake notice.
//
// Rails (X-02 amendment, 2026-07-21): two sinks, one seam each.
// The steward intake notice rides Telegram; the applicant
// acknowledgment rides Resend email. Each sink activates only when
// its secrets are present, so the rail degrades by naming gaps
// rather than failing: an unconfigured email sink becomes a line in
// the steward notice, not a silent drop. Rationale: the techne.coop
// sending domain is DNS-managed outside the steward's reach, so the
// email sink awaits domain verification; the steward notice must not
// wait with it. Secrets live in Supabase function secrets
// (reference, not value):
//   TELEGRAM_BOT_TOKEN  steward-notice credential (@nou_guild_bot)
//   TELEGRAM_CHAT_ID    where intake notices land
//   RESEND_API_KEY      applicant-acknowledgment credential
//   NOTICES_FROM        e.g. "Techne <notices@techne.coop>" (domain
//                       verified in Resend first)
//   STEWARD_EMAIL       email fallback for the intake notice when
//                       Telegram is unconfigured (Bylaws §1.3.3)
//
// The applicant address is read from the event payload (email), then
// from the application row it references. If neither carries one, the
// steward notice still goes out, naming the gap.

import { createClient } from "npm:@supabase/supabase-js@2";

const TELEGRAM_BOT_TOKEN = Deno.env.get("TELEGRAM_BOT_TOKEN") ?? "";
const TELEGRAM_CHAT_ID = Deno.env.get("TELEGRAM_CHAT_ID") ?? "";
const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";
const NOTICES_FROM = Deno.env.get("NOTICES_FROM") ?? "";
const STEWARD_EMAIL = Deno.env.get("STEWARD_EMAIL") ?? "";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";

const emailConfigured = Boolean(RESEND_API_KEY && NOTICES_FROM);
const telegramConfigured = Boolean(TELEGRAM_BOT_TOKEN && TELEGRAM_CHAT_ID);

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

async function sendTelegram(text: string) {
  const r = await fetch(
    `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: TELEGRAM_CHAT_ID, text }),
    },
  );
  if (!r.ok) {
    throw new Error(`telegram ${r.status}: ${await r.text()}`);
  }
}

// X-12 · the member's rail, away-channel half. The in-app rail (0015 +
// the shell bell) is the authoritative delivery: it reads the log
// directly and works today. This routes the same events to the member's
// email so news reaches them when they are away, and it activates only
// when the email sink is configured (the X-02 amendment pattern); until
// the sending domain verifies, every branch below returns quietly and
// the in-app rail carries the whole load.
const MEMBER_KINDS: Record<string, (p: Record<string, unknown>) => [string, string]> = {
  "opportunity.responded": (p) => [
    `${p.responder ?? "A member"} responded to "${p.title ?? "your opportunity"}"`,
    "Read and reply on the opportunity board: https://techne.coop/commons/opportunities/",
  ],
  "registration.registered": (p) => [
    `${p.registrant ?? "A member"} registered for "${p.title ?? "your gathering"}"`,
    "The calendar holds the current count: https://techne.coop/commons/gatherings/",
  ],
  "registration.cancelled": (p) => [
    `${p.registrant ?? "A member"} cancelled their registration for "${p.title ?? "your gathering"}"`,
    "The calendar holds the current count: https://techne.coop/commons/gatherings/",
  ],
  "membership.admitted": () => [
    "You were admitted to membership in RegenHub, LCA",
    "Sign in and sign the membership agreement: https://techne.coop/commons/agreements/",
  ],
};

// The concerned member's address: the bound auth user first; failing
// that (admission precedes the first sign-in that binds), the address
// their membership.applied event carries.
async function memberEmail(sb: ReturnType<typeof createClient>, agentId: string): Promise<string | null> {
  const { data: agent } = await sb.from("agents")
    .select("auth_user_id").eq("id", agentId).single();
  if (agent?.auth_user_id) {
    const { data } = await sb.auth.admin.getUserById(agent.auth_user_id);
    if (data?.user?.email) return data.user.email;
  }
  const { data: applied } = await sb.from("events")
    .select("payload").eq("kind", "membership.applied")
    .eq("agent_id", agentId).order("occurred_at", { ascending: false }).limit(1);
  const addr = applied?.[0]?.payload?.email;
  return typeof addr === "string" && addr.includes("@") ? addr : null;
}

Deno.serve(async (req) => {
  try {
    const { event } = await req.json();

    if (event && event.kind in MEMBER_KINDS) {
      if (!emailConfigured) {
        return new Response(
          JSON.stringify({ ok: true, sink: "in-app only; email sink not configured" }),
          { headers: { "Content-Type": "application/json" } },
        );
      }
      const sb = createClient(SUPABASE_URL, SERVICE_KEY);
      const to = event.agent_id ? await memberEmail(sb, event.agent_id) : null;
      if (!to) {
        return new Response(
          JSON.stringify({ ok: true, sink: "no address on record; in-app rail carries it" }),
          { headers: { "Content-Type": "application/json" } },
        );
      }
      const [subject, hint] = MEMBER_KINDS[event.kind](event.payload ?? {});
      await send(to, subject, [
        subject + ".",
        "",
        hint,
        "",
        "RegenHub, LCA · Boulder, Colorado",
        "techne.coop",
      ].join("\n"));
      return new Response(JSON.stringify({ ok: true, sent: { member: to } }), {
        headers: { "Content-Type": "application/json" },
      });
    }

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

    if (email && emailConfigured) {
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
    } else if (email) {
      results.applicant =
        "address on file; email sink not configured -- steward notified of the gap";
    } else {
      results.applicant = "no address found; steward notified of the gap";
    }

    const stewardText = [
      `New membership application: ${displayName}`,
      "",
      `event: ${event.id}`,
      `agent: ${event.agent_id ?? "unknown"}`,
      `applicant address: ${email ?? "NOT FOUND -- check the application record"}`,
      `applicant acknowledged: ${
        results.applicant === email ? "yes, by email" : "NO -- " + results.applicant
      }`,
      "",
      "Intake per Bylaws 1.3.3; admission is the Board's decision.",
    ].join("\n");

    if (telegramConfigured) {
      await sendTelegram(stewardText);
      results.steward = "telegram";
    } else if (STEWARD_EMAIL && emailConfigured) {
      await send(
        STEWARD_EMAIL,
        `New membership application: ${displayName}`,
        stewardText,
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
