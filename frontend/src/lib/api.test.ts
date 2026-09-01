import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { afterEach, describe, expect, it, vi } from "vitest";

import { getApiBaseUrl } from "@/lib/api";

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..");

describe("getApiBaseUrl", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("defaults to the local FastAPI host when NEXT_PUBLIC_API_URL is unset", () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "");
    expect(getApiBaseUrl()).toBe("http://127.0.0.1:8000");
  });

  it("strips trailing slashes from configured API URLs", () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000/");
    expect(getApiBaseUrl()).toBe("http://127.0.0.1:8000");
  });
});

describe("frontend dev script", () => {
  it("uses localhost:3001 for local development", () => {
    const packageJson = JSON.parse(
      readFileSync(join(frontendRoot, "package.json"), "utf8"),
    ) as { scripts: { dev: string } };
    expect(packageJson.scripts.dev).toContain("localhost");
    expect(packageJson.scripts.dev).toContain("3001");
  });
});
