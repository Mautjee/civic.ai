export const backendUrls = {
  postMessage: "/feed-database",
};

export const API_URL =
  typeof import.meta.env.VITE_API_URL === "string"
    ? import.meta.env.VITE_API_URL
    : "";

export const Nouns_API = "https://noun-api.com/beta/pfp";
