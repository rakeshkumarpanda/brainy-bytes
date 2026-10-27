// Test accounts. Real projects read passwords from CI secrets, never from the repository.
export const users = {
  asha: { email: 'asha@shop.example', password: process.env.ASHA_PASSWORD || 's3cret', name: 'Asha' },
  ravi: { email: 'ravi@shop.example', password: process.env.RAVI_PASSWORD || 'admin123', name: 'Ravi' },
};
