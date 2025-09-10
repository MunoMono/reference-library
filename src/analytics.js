// src/analytics.js
export const byYear = (entries) =>
  entries.reduce((m, e) => {
    const y = e.year || "Unknown";
    m[y] = (m[y] || 0) + 1;
    return m;
  }, {});

export const byAuthor = (entries) =>
  entries.reduce((m, e) => {
    for (const a of e.authors || []) m[a] = (m[a] || 0) + 1;
    return m;
  }, {});

export const toSeries = (obj) =>
  Object.entries(obj).map(([label, value]) => ({ label, key: label, value }));