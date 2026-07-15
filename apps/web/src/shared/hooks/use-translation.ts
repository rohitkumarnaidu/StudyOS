"use client";

import { useState, useCallback } from "react";
import type { Locale } from "@/shared/config/i18n";
import type { TranslationKey } from "@/shared/config/translations";
import { DEFAULT_LOCALE } from "@/shared/config/i18n";
import { t as translate } from "@/shared/config/translations";

export function useTranslation(initialLocale: Locale = DEFAULT_LOCALE) {
  const [locale, setLocale] = useState<Locale>(initialLocale);

  const t = useCallback(
    (key: TranslationKey) => translate(locale, key),
    [locale],
  );

  return { t, locale, setLocale };
}
