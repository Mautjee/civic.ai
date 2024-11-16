export const backendUrls = {
  postMessage: "feed-database",
};

export const API_URL =
  typeof import.meta.env.VITE_API_URL === "string"
    ? import.meta.env.VITE_API_URL
    : "";
