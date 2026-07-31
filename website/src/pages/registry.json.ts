import { filterCatalog, getCatalogStats, loadCatalog } from "@/lib/catalog";
import { buildRegistryPayload } from "@/lib/geo";

export async function GET() {
  const entries = filterCatalog(await loadCatalog(), {});
  const payload = buildRegistryPayload(entries, getCatalogStats(entries));

  return new Response(`${JSON.stringify(payload, null, 2)}\n`, {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
      "Access-Control-Allow-Origin": "*",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
