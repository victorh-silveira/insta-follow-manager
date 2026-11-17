import {
  HealthResponse,
  ListProfilesResponse,
  RelationshipListType,
  SyncResponse,
  UnfollowResponse,
} from "@/types/relationship";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let detail = `Erro HTTP ${response.status}`;
    try {
      const data = (await response.json()) as { detail?: string };
      if (data.detail) detail = data.detail;
    } catch {
      // Ignore JSON parse errors on non-JSON responses
    }
    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export const relationshipApi = {
  getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>("/api/health");
  },

  sync(): Promise<SyncResponse> {
    return request<SyncResponse>("/api/relationships/sync", {
      method: "POST",
    });
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
    return request<UnfollowResponse>(`/api/relationships/${encodeURIComponent(pk)}/unfollow`, {
      method: "POST",
    });
  },
};
