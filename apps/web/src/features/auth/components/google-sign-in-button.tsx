"use client";

import { useState } from "react";

import { Button } from "@/shared/components/ui/button";
import { ROUTES } from "@/shared/config/routes";
import { notifyError, notifyFromUnknown } from "@/shared/lib";
import { createSupabaseBrowserClient } from "@/shared/lib/supabase/browser-client";

type GoogleSignInButtonProps = {
  /** Post-login path (already sanitized by caller). */
  nextPath: string;
};

export function GoogleSignInButton({ nextPath }: GoogleSignInButtonProps) {
  const [busy, setBusy] = useState(false);
  const supabase = createSupabaseBrowserClient();

  if (!supabase) {
    return null;
  }

  const client = supabase;

  async function onGoogle() {
    setBusy(true);
    try {
      const callback = new URL(ROUTES.authCallback, window.location.origin);
      callback.searchParams.set("next", nextPath);

      const { data, error } = await client.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: callback.toString(),
          queryParams: { prompt: "select_account" },
        },
      });

      if (error) {
        notifyError(error.message);
        return;
      }

      if (data.url) {
        window.location.assign(data.url);
      }
    } catch (e) {
      notifyFromUnknown(e, "Could not start Google sign-in");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Button
      type="button"
      variant="secondary"
      className="w-full"
      disabled={busy}
      onClick={() => void onGoogle()}
    >
      {busy ? "Redirecting…" : "Continue with Google"}
    </Button>
  );
}
