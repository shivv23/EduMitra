"use client";

import { getStoredToken, getStoredUser, type AuthUser } from "@/lib/auth";

export function createSupabaseBrowserClient(): {
  auth: {
    getSession: () => Promise<{ data: { session: { access_token: string; user: { email?: string; user_metadata: Record<string, unknown> } } | null } }>;
    getUser: () => Promise<{ data: { user: { email?: string; user_metadata: Record<string, unknown> } | null } }>;
  };
} {
  return {
    auth: {
      getSession: async () => {
        const token = getStoredToken();
        const user = getStoredUser();
        if (!token || !user) return { data: { session: null } };
        return {
          data: {
            session: {
              access_token: token,
              user: {
                email: user.email,
                user_metadata: { name: user.name, role: user.role },
              },
            },
          },
        };
      },
      getUser: async () => {
        const user = getStoredUser();
        if (!user) return { data: { user: null } };
        return {
          data: {
            user: {
              email: user.email,
              user_metadata: { name: user.name, role: user.role },
            },
          },
        };
      },
    },
  };
}

export async function getSession() {
  return createSupabaseBrowserClient().auth.getSession();
}

export async function getCurrentUser() {
  return createSupabaseBrowserClient().auth.getUser();
}
