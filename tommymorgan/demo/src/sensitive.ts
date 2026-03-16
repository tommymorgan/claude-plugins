const SENSITIVE_PATTERNS = [
  /\/login/i,
  /\/auth/i,
  /\/signin/i,
  /\/sign-in/i,
  /\/admin/i,
  /\/account/i,
  /\/dashboard(?!.*public)/i,
  /\/settings/i,
  /\/profile/i,
  /\/oauth/i,
  /\/sso/i,
];

export function detectSensitiveUrls(urls: string[]): string[] {
  return urls.filter((url) =>
    SENSITIVE_PATTERNS.some((pattern) => pattern.test(url))
  );
}
