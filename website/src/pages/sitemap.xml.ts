import { filterCatalog, loadCatalog } from "@/lib/catalog";
import { buildSitemap } from "@/lib/seo";

export async function GET() {
  const entries = filterCatalog(await loadCatalog(), {});
  const paths = [
    "/",
    "/about",
    "/faq",
    "/learn",
    "/skills",
    ...entries.map((entry) => `/skills/${entry.slug}`),
    "/submit",
  ];

  return new Response(buildSitemap(paths), {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
}
