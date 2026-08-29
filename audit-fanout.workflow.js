// Gated Multi-Agent Audit Fan-out — 1:1 zum claude-seo-Orchestrator.
// args = { url, credentials? }
const url = args.url;
const creds = args.credentials || {};

phase("Branche erkennen");
const probe = await agent(
  `Ermittle die Branche der Website ${url}. Antworte NUR mit dem JSON-Feld.`,
  { label: "industry-probe", phase: "Branche erkennen",
    schema: { type: "object", properties: { industry: { type: "string", enum: ["saas", "local-service", "ecommerce", "publisher", "agency", "other"] } }, required: ["industry"] } }
);
const industry = (probe && probe.industry) || "other";
log("Branche: " + industry);

const ALWAYS = ["technical", "content", "schema", "page", "sxo", "geo"];
const BY_INDUSTRY = { "saas": ["cluster", "programmatic"], "local-service": ["local", "maps"],
  "ecommerce": ["ecommerce"], "publisher": ["cluster", "images"], "agency": ["competitor-pages"], "other": [] };
const CREDENTIAL = [["google", "google"], ["backlinks", "backlinks"], ["dataforseo", "dataforseo"], ["firecrawl", "firecrawl"]];

let cats = [...ALWAYS, ...(BY_INDUSTRY[industry] || [])];
for (const [key, cat] of CREDENTIAL) { if (creds[key]) cats.push(cat); }
cats = [...new Set(cats)];
log("Gated Agents: " + cats.join(", "));

const schema = {
  type: "object",
  properties: {
    category: { type: "string" }, severity: { type: "string", enum: ["critical", "high", "medium", "low"] },
    summary: { type: "string" }, findings: { type: "array", items: { type: "string" } },
    recommendations: { type: "array", items: { type: "object", properties: {
      title: { type: "string" }, observation: { type: "string" }, dependency: { type: "string" },
      failure_signal: { type: "string" }, early_indicator: { type: "string" } },
      required: ["title", "observation", "dependency", "failure_signal", "early_indicator"] } }
  },
  required: ["category", "severity", "summary", "findings"]
};

phase("Parallele Analyse");
const results = await parallel(cats.map((cat) => () =>
  agent(
    `Du bist der Spezialist "seo-${cat}" im SEO-Audit von ${url} (Branche: ${industry}).\n` +
    `Arbeite NUR deine Kategorie ab.\n` +
    `1. Lade skills/seo-${cat}/SKILL.md.\n` +
    `2. Führe Messungen aus: cd "seo-toolkit" && ./seo <passender Befehl> ${url}\n` +
    `3. Formuliere jede Empfehlung mit 4 Feldern: Beobachtung → Abhängigkeit → Misserfolgssignal → Frühindikator.\n` +
    `Antworte mit den geforderten JSON-Feldern.`,
    { label: cat, phase: "Parallele Analyse", schema }
  )
));

phase("Synthese");
return { url, industry, categoriesRun: cats, results: results.filter(Boolean) };
