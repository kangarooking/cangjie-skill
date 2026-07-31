export function onRequest() {
  return new Response("2653ffe9de5227d7be23e331551bec0d", {
    headers: {
      "Cache-Control": "public, max-age=300",
      "Content-Type": "text/html; charset=UTF-8",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
