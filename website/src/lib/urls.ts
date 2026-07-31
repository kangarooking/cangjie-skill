export function withBase(path = "/"): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  const raw = path.startsWith("/") ? path : `/${path}`;
  const [pathname, suffix = ""] = raw.split(/([?#].*)/, 2);
  const isFile = /\/[^/]+\.[^/]+$/.test(pathname);
  const normalized = pathname !== "/" && !pathname.endsWith("/") && !isFile
    ? `${pathname}/${suffix}`
    : `${pathname}${suffix}`;
  return `${base}${normalized}` || "/";
}
