export type RelationshipListType =
  | "following"
  | "followers"
  | "non_followers"
  | "not_following_back";

export const LETTER_BUCKETS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
export const DIGITS_BUCKET = "0-9";
export const SPECIAL_BUCKET = "SPECIAL";
export const ALL_BUCKETS = [...LETTER_BUCKETS, DIGITS_BUCKET, SPECIAL_BUCKET] as const;

export interface Profile {
  pk: string;
  username: string;
  full_name: string;
  bucket: string;
  profile_pic_url: string | null;
  is_following: boolean;
  is_follower: boolean;
  is_verified: boolean;
}

export interface ListProfilesResponse {
  profiles: Profile[];
  bucket_counts: Record<string, number>;
  total_in_list: number;
}

export interface SyncResponse {
  total_profiles: number;
  following_count: intOrNumber;
  followers_count: number;
  non_followers_count: number;
  gateway_mode: string;
}

type intOrNumber = number;

export interface UnfollowResponse {
  pk: string;
  username: string;
  full_name: string;
  unfollowed: boolean;
  follower_removed?: boolean;
}

export interface RemoveFollowerResponse {
  pk: string;
  username: string;
  full_name: string;
  removed: boolean;
}

export interface HealthResponse {
  status: string;
  gateway_mode: string;
}

export interface AuthStatus {
  authenticated: boolean;
  gateway_mode: string;
  username: string | null;
  full_name: string | null;
  profile_pic_url: string | null;
}

export interface LoginPayload {
  username?: string;
  password?: string;
  verification_code?: string;
  challenge_code?: string;
  session_id?: string;
}
