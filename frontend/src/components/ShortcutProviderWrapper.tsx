"use client";

import { ShortcutProvider } from "./ShortcutProvider";

export function ShortcutProviderWrapper({ children }: { children: React.ReactNode }) {
  return <ShortcutProvider>{children}</ShortcutProvider>;
}
