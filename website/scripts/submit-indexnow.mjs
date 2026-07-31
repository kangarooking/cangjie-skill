const host = "www.cangjie-skill.com";
const key = "bffc3923d11c98b9f97a83ffb46ba39e";
const keyLocation = `https://${host}/${key}.txt`;
const sitemapUrl = `https://${host}/sitemap.xml`;

const sitemapResponse = await fetch(sitemapUrl);
if (!sitemapResponse.ok) {
  throw new Error(`Unable to fetch live sitemap: ${sitemapResponse.status}`);
}

const sitemap = await sitemapResponse.text();
const urlList = [...sitemap.matchAll(/<loc>(.*?)<\/loc>/g)].map((match) =>
  match[1]
    .replaceAll("&amp;", "&")
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">")
    .replaceAll("&quot;", '"')
    .replaceAll("&apos;", "'"),
);

if (!urlList.length) {
  throw new Error("No URLs found in the live sitemap.");
}

const response = await fetch("https://api.indexnow.org/indexnow", {
  method: "POST",
  headers: { "Content-Type": "application/json; charset=utf-8" },
  body: JSON.stringify({ host, key, keyLocation, urlList }),
});

if (![200, 202].includes(response.status)) {
  throw new Error(`IndexNow submission failed: ${response.status} ${await response.text()}`);
}

console.log(`IndexNow accepted ${urlList.length} URLs with status ${response.status}.`);
