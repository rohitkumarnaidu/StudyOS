/** Legacy demo cookie (middleware still accepts for older flows). */
export const STUDYOS_SESSION_COOKIE = "studyos_session";

/** HttpOnly access JWT (BFF + middleware; must match API signing secret). */
export const STUDYOS_ACCESS_COOKIE = "studyos_access";

/** HttpOnly rotating refresh token (opaque). */
export const STUDYOS_REFRESH_COOKIE = "studyos_refresh";
