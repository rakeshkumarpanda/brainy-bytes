// Settings that change between machines (a laptop, CI, staging) live here and nowhere else
export const env = {
  baseURL: process.env.BASE_URL ?? 'http://localhost:4173',
};
