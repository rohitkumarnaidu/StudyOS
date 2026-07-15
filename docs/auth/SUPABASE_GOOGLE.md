# Google sign-in (Supabase Auth + Next.js)

StudyOS uses **Supabase Auth** for Google OAuth and the route **`/auth/callback`** to complete the PKCE exchange (see `apps/web/src/app/auth/callback/route.ts`).

## 1. Google Cloud Console

1. Create a project (or pick an existing one): [Google Cloud Console](https://console.cloud.google.com/).
2. **APIs & Services → Credentials → Create credentials → OAuth client ID**.
3. Application type: **Web application**.
4. **Authorized JavaScript origins**: your app origins, e.g. `http://localhost:3000`, `https://your-domain.com`.
5. **Authorized redirect URIs**: add Supabase’s callback (not your Next app directly):
   - `https://<YOUR_PROJECT_REF>.supabase.co/auth/v1/callback`  
   Copy the exact value from **Supabase Dashboard → Authentication → Providers → Google** (“Callback URL”).

Save the **Client ID** and **Client secret**.

## 2. Supabase Dashboard

1. **Authentication → Providers → Google**: enable, paste Client ID and Client secret.
2. **Authentication → URL configuration**:
   - **Site URL**: e.g. `http://localhost:3000` or production site root.
   - **Redirect URLs**: allow your app callback, e.g.  
     `http://localhost:3000/auth/callback`  
     `https://your-domain.com/auth/callback`  
     (Must match what `Continue with Google` sends as `redirectTo`.)

## 3. App environment

In `apps/web/.env.local` (see `.env.example`):

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

Restart `pnpm dev` after changes.

## 4. `public.profiles` row for new Google users

OAuth creates `auth.users`. A DB migration **`20260213120001_on_auth_user_create_profile.sql`** installs **`public.handle_new_user`**: after insert on `auth.users`, a matching **`public.profiles`** row is inserted (`ON CONFLICT DO NOTHING`). The trigger is only created when **`auth.users`** exists (Supabase).

If you applied migrations before this file was added, run **`supabase db push`** / **`supabase db reset`** or apply the SQL manually in the Supabase SQL editor.

If you customize `profiles` columns, adjust the trigger function accordingly.

## 5. Troubleshooting

- **`redirect_mismatch`**: Google redirect URI must be Supabase `…/auth/v1/callback`, not `/auth/callback` on your domain.
- **Loop or “oauth” error on `/login`**: check Supabase **Redirect URLs** include full callback URL with origin; check `NEXT_PUBLIC_*` values and restart Next.
- **Session ok but no DB row**: add trigger or upsert `profiles` as in section 4.
