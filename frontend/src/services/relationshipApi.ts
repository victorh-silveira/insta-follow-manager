import {
  AuthStatus,
  HealthResponse,
  ListProfilesResponse,
  LoginPayload,
  RelationshipAnalytics,
  RelationshipListType,
  RemoveFollowerResponse,
  SyncResponse,
  UnfollowResponse,
} from "@/types/relationship";

function resolveApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL;
  if (typeof window !== "undefined") {
    const { protocol, hostname } = window.location;
    if (
      hostname &&
      hostname !== "localhost" &&
      hostname !== "127.0.0.1" &&
      (!configured || configured === "http://localhost:8000")
    ) {
      return `${protocol}//${hostname}:8000`;
    }
  }
  return configured ?? "http://localhost:8000";
}

export class ApiError extends Error {
  requires2fa: boolean;
  requiresChallenge: boolean;

  constructor(
    message: string,
    opts?: { requires2fa?: boolean; requiresChallenge?: boolean }
  ) {
    super(message);
    this.requires2fa = Boolean(opts?.requires2fa);
    this.requiresChallenge = Boolean(opts?.requiresChallenge);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${resolveApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let detail = `Erro HTTP ${response.status}`;
    let requires2fa = false;
    let requiresChallenge = false;
    try {
      const data = (await response.json()) as {
        detail?: string;
        requires_2fa?: boolean;
        requires_challenge?: boolean;
      };
      if (data.detail) detail = data.detail;
      requires2fa = Boolean(data.requires_2fa);
      requiresChallenge = Boolean(data.requires_challenge);
    } catch {
      // Ignore JSON parse errors on non-JSON responses
    }
    throw new ApiError(detail, { requires2fa, requiresChallenge });
  }

  return (await response.json()) as T;
}

export const relationshipApi = {
  getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>("/api/health");
  },

  getAuthStatus(): Promise<AuthStatus> {
    return request<AuthStatus>("/api/auth/status");
  },

  login(payload: LoginPayload): Promise<AuthStatus> {
    return request<AuthStatus>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  logout(): Promise<AuthStatus> {
    return request<AuthStatus>("/api/auth/logout", {
      method: "POST",
    });
  },

  sync(): Promise<SyncResponse> {
    return request<SyncResponse>("/api/relationships/sync", {
      method: "POST",
    });
  },

  getAnalytics(): Promise<RelationshipAnalytics> {
    return request<RelationshipAnalytics>("/api/relationships/analytics");
  },

  list(params: {
    listType: RelationshipListType;
    bucket?: string | null;
    search?: string;
  }): Promise<ListProfilesResponse> {
    const query = new URLSearchParams({ list_type: params.listType });
    if (params.bucket && params.bucket !== "ALL") {
      query.set("bucket", params.bucket);
    }
    if (params.search && params.search.trim()) {
      query.set("q", params.search.trim());
    }
    return request<ListProfilesResponse>(`/api/relationships?${query.toString()}`);
  },

  unfollow(pk: string): Promise<UnfollowResponse> {
    return request<UnfollowResponse>(
      `/api/relationships/${encodeURIComponent(pk)}/unfollow`,
      {
        method: "POST",
      }
    );
  },

  removeFollower(pk: string): Promise<RemoveFollowerResponse> {
    return request<RemoveFollowerResponse>(
      `/api/relationships/${encodeURIComponent(pk)}/remove-follower`,
      {
        method: "POST",
      }
    );
  },
};
