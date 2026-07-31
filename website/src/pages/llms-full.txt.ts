import { filterCatalog, getCatalogStats, loadCatalog } from "@/lib/catalog";
import { buildLlmsFullText } from "@/lib/geo";

export async function GET() {
  const entries = filterCatalog(await loadCatalog(), {});
  return new Response(buildLlmsFullText(entries, getCatalogStats(entries)), {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
