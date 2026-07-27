import { mkdir, writeFile } from "node:fs/promises";

const worker = `export default {
  async fetch(request, env) {
    const response = await env.ASSETS.fetch(request);
    if (response.status !== 404 || request.method !== "GET") return response;

    const url = new URL(request.url);
    if (url.pathname.endsWith("/")) {
      url.pathname += "index.html";
    } else if (!url.pathname.split("/").at(-1)?.includes(".")) {
      url.pathname += "/index.html";
    } else {
      return response;
    }

    return env.ASSETS.fetch(new Request(url, request));
  },
};
`;

await mkdir(new URL("../dist/server/", import.meta.url), { recursive: true });
await writeFile(new URL("../dist/server/index.js", import.meta.url), worker);
