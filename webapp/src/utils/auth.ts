// webapp/src/utils/auth.ts
export function decodeToken(token: string | null): string {
    if (!token) return "";
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.sub || "";
    } catch (e) {
      return "";
    }
  }
  