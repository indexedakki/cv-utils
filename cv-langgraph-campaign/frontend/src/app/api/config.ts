export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export const API_ENDPOINTS = {
  CAMPAIGN: '/campaign',
  CANDIDATES: '/candidates',
  EMAIL_DRAFT: '/email_draft',
} as const;