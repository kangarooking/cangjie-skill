export function onRequest() {
  return new Response("ab151a3261fe600b79627b0ff1efd721", {
    headers: {
      "Cache-Control": "public, max-age=300",
      "Content-Type": "text/html; charset=UTF-8",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
