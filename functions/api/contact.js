// Cloudflare Pages Function: POST /api/contact -> sends the lead by email through Resend.
// Required environment variables (Cloudflare Pages > Settings > Environment variables):
//   RESEND_API_KEY  - your Resend API key
//   LEAD_TO_EMAIL   - inbox that receives leads (comma-separate for several)
//   LEAD_FROM_EMAIL - verified sender, e.g. "Laurel Dry Pros <leads@waterdamagerestorationlaurelmd.com>"
const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

const clean = (v, max = 2000) => String(v || "").replace(/[\u0000-\u001f\u007f]/g, " ").trim().slice(0, max);
const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export async function onRequestPost({ request, env }) {
  let form;
  try { form = await request.formData(); } catch { return json({ error: "Invalid form data." }, 400); }
  if (clean(form.get("company"))) return json({ ok: true }); // honeypot: silently accept bots
  const name = clean(form.get("name"), 120);
  const phone = clean(form.get("phone"), 40);
  const zip = clean(form.get("zip"), 10);
  const service = clean(form.get("service"), 120);
  const message = clean(form.get("message"), 3000);
  const consent = clean(form.get("consent"), 10);
  if (!name || !phone) return json({ error: "Please add your name and phone number." }, 400);
  if (!/^[0-9+().\-\s]{7,20}$/.test(phone)) return json({ error: "Please check the phone number." }, 400);
  if (zip && !/^\d{5}$/.test(zip)) return json({ error: "Please use a 5-digit ZIP code." }, 400);
  if (consent !== "yes") return json({ error: "Please tick the consent box so we can contact you." }, 400);
  if (!env.RESEND_API_KEY || !env.LEAD_TO_EMAIL || !env.LEAD_FROM_EMAIL) return json({ error: "The form is not set up yet. Please call us." }, 503);

  const page = clean(request.headers.get("referer"), 300);
  const html = `<h2>New website request: Laurel Dry Pros</h2>
<p><b>Name:</b> ${esc(name)}<br><b>Phone:</b> ${esc(phone)}<br><b>ZIP:</b> ${esc(zip || "-")}<br><b>Service:</b> ${esc(service || "-")}</p>
<p><b>Message:</b><br>${esc(message || "-").replace(/\n/g, "<br>")}</p>
<p style="color:#666;font-size:12px">Page: ${esc(page || "-")} · Consent to contact: yes · ${new Date().toISOString()}</p>`;

  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: env.LEAD_FROM_EMAIL,
      to: env.LEAD_TO_EMAIL.split(",").map((s) => s.trim()).filter(Boolean),
      subject: `Lead: ${service || "Water damage"} - ${name} (${zip || "no ZIP"})`,
      html,
    }),
  });
  if (!r.ok) return json({ error: "Sorry, that did not send. Please call us instead." }, 502);
  return json({ ok: true });
}

export const onRequestGet = () => json({ error: "Method not allowed." }, 405);
