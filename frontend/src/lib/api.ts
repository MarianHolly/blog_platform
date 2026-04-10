const API_URL = import.meta.env.PUBLIC_API_URL ?? 'http://localhost:8000';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Author {
	id: number;
	username: string;
	full_name: string;
	avatar_url: string | null;
}

export interface BulletinSummary {
	id: number;
	slug: string;
	title: string;
	description: string;
	owner: Profile;
	subscribers_count: number;
	articles_count: number;
	created: string;
	updated: string;
}

export interface BulletinDetail extends BulletinSummary {
	recent_articles: ArticleSummary[];
}

export interface ArticleSummary {
	id: number;
	slug: string;
	title: string;
	subtitle: string;
	description: string;
	bulletin_title: string;
	author: Author;
	status: 'draft' | 'published';
	visibility: 'public' | 'private';
	likes_count: number;
	comments_count: number;
	created: string;
	published: string | null;
}

export interface ArticleDetail extends ArticleSummary {
	content: string;
	evaluation: string;
	updated: string;
	is_liked: boolean;
	is_bookmarked: boolean;
	can_edit: boolean;
}

export interface Comment {
	id: number;
	author: Profile;
	author_name: string;
	article: number;
	content: string;
	created: string;
	updated: string;
	can_edit: boolean;
}

export interface Profile {
	id: number;
	user: {
		id: number;
		username: string;
		email: string;
		first_name: string;
		last_name: string;
	};
	role: 'reader' | 'writer' | 'admin';
	biography: string;
	avatar: string | null;
	avatar_url: string | null;
	full_name: string;
	articles_count: number;
}

export interface PaginatedResponse<T> {
	count: number;
	next: string | null;
	previous: string | null;
	results: T[];
}

export interface TokenPair {
	access: string;
	refresh: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

async function apiFetch<T>(
	path: string,
	options: RequestInit = {},
	token?: string,
): Promise<T> {
	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...(options.headers as Record<string, string>),
	};
	if (token) headers['Authorization'] = `Bearer ${token}`;

	const res = await fetch(`${API_URL}/api/v1${path}`, {
		...options,
		headers,
	});

	if (!res.ok) {
		const text = await res.text().catch(() => res.statusText);
		throw new Error(`API ${res.status}: ${text}`);
	}

	return res.json() as Promise<T>;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export async function login(username: string, password: string): Promise<TokenPair> {
	return apiFetch<TokenPair>('/auth/token/', {
		method: 'POST',
		body: JSON.stringify({ username, password }),
	});
}

export async function refreshToken(refresh: string): Promise<{ access: string }> {
	return apiFetch<{ access: string }>('/auth/token/refresh/', {
		method: 'POST',
		body: JSON.stringify({ refresh }),
	});
}

// ─── Articles ─────────────────────────────────────────────────────────────────

export async function getArticles(params?: {
	page?: number;
	page_size?: number;
	search?: string;
	bulletin?: string;
	ordering?: string;
}, token?: string): Promise<PaginatedResponse<ArticleSummary>> {
	const qs = new URLSearchParams();
	if (params?.page) qs.set('page', String(params.page));
	if (params?.page_size) qs.set('page_size', String(params.page_size));
	if (params?.search) qs.set('search', params.search);
	if (params?.bulletin) qs.set('bulletin', params.bulletin);
	if (params?.ordering) qs.set('ordering', params.ordering);
	const query = qs.toString() ? `?${qs}` : '';
	return apiFetch<PaginatedResponse<ArticleSummary>>(`/articles/${query}`, {}, token);
}

export async function getArticle(slug: string, token?: string): Promise<ArticleDetail> {
	return apiFetch<ArticleDetail>(`/articles/${slug}/`, {}, token);
}

export async function likeArticle(slug: string, token: string): Promise<void> {
	await apiFetch(`/articles/${slug}/like/`, { method: 'POST' }, token);
}

export async function bookmarkArticle(slug: string, token: string): Promise<void> {
	await apiFetch(`/articles/${slug}/bookmark/`, { method: 'POST' }, token);
}

// ─── Bulletins ────────────────────────────────────────────────────────────────

export async function getBulletins(params?: {
	page?: number;
	search?: string;
}, token?: string): Promise<PaginatedResponse<BulletinSummary>> {
	const qs = new URLSearchParams();
	if (params?.page) qs.set('page', String(params.page));
	if (params?.search) qs.set('search', params.search);
	const query = qs.toString() ? `?${qs}` : '';
	return apiFetch<PaginatedResponse<BulletinSummary>>(`/bulletins/${query}`, {}, token);
}

export async function getBulletin(slug: string, token?: string): Promise<BulletinDetail> {
	return apiFetch<BulletinDetail>(`/bulletins/${slug}/`, {}, token);
}

export async function subscribeToBulletin(slug: string, token: string): Promise<void> {
	await apiFetch(`/bulletins/${slug}/subscribe/`, { method: 'POST' }, token);
}

// ─── Comments ─────────────────────────────────────────────────────────────────

export async function getComments(articleId: number, token?: string): Promise<PaginatedResponse<Comment>> {
	return apiFetch<PaginatedResponse<Comment>>(`/comments/?article=${articleId}`, {}, token);
}

export async function createComment(articleId: number, content: string, token: string): Promise<Comment> {
	return apiFetch<Comment>('/comments/', {
		method: 'POST',
		body: JSON.stringify({ article: articleId, content }),
	}, token);
}

export async function deleteComment(id: number, token: string): Promise<void> {
	await apiFetch(`/comments/${id}/`, { method: 'DELETE' }, token);
}
