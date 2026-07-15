export const SUPPORTED_LOCALES = ["en", "hi", "ta"] as const;

export type Locale = (typeof SUPPORTED_LOCALES)[number];

export const DEFAULT_LOCALE: Locale = "en";

export const LOCALE_NAMES: Record<Locale, string> = {
  en: "English",
  hi: "हिन्दी",
  ta: "தமிழ்",
};

export function getLocaleFromHeader(header: string | null): Locale {
  if (!header) return DEFAULT_LOCALE;
  const primary = header.split(",")[0]?.split("-")[0] ?? "";
  if (SUPPORTED_LOCALES.includes(primary as Locale)) {
    return primary as Locale;
  }
  return DEFAULT_LOCALE;
}

export function isLocaleSupported(locale: string): locale is Locale {
  return SUPPORTED_LOCALES.includes(locale as Locale);
}
