import { jwtVerify } from "jose";

const encoder = new TextEncoder();

/** Verify StudyOS access JWT (HS256, iss, typ=access). Returns null if invalid or secret unset. */
export async function verifyStudyosAccessJwt(token: string): Promise<Record<string, unknown> | null> {
  const secret = process.env.STUDYOS_JWT_SECRET;
  if (!secret) return null;
  try {
    const { payload } = await jwtVerify(token, encoder.encode(secret), {
      issuer: process.env.STUDYOS_JWT_ISSUER ?? "studyos-api",
      algorithms: ["HS256"],
    });
    if (payload.typ !== "access") return null;
    return { ...payload };
  } catch {
    return null;
  }
}
