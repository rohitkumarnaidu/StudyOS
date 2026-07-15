/**
 * Edge-safe Supabase env check (middleware). Do not import server-only modules here.
 */
export function isSupabaseEdgeConfigured(): boolean {
  const url = process.env["NEXT_PUBLIC_SUPABASE_URL"]?.trim();
  const key = process.env["NEXT_PUBLIC_SUPABASE_ANON_KEY"]?.trim();
  return Boolean(url && key);
}
