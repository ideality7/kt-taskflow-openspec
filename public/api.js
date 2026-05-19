export function getToken() {
    return localStorage.getItem('tf_token');
}

export function setAuth(token, user) {
    localStorage.setItem('tf_token', token);
    localStorage.setItem('tf_user', JSON.stringify(user));
}

export function clearAuth() {
    ['tf_token', 'tf_user', 'tf_team'].forEach(k => localStorage.removeItem(k));
}

export function getUser() {
    const u = localStorage.getItem('tf_user');
    return u ? JSON.parse(u) : null;
}

export function getTeam() {
    const t = localStorage.getItem('tf_team');
    return t ? JSON.parse(t) : null;
}

export function setTeam(team) {
    localStorage.setItem('tf_team', JSON.stringify(team));
}

export function requireAuth() {
    if (!getToken()) { location.href = '/index.html'; return false; }
    return true;
}

export function requireTeam() {
    if (!getTeam()) { location.href = '/teams.html'; return false; }
    return true;
}

export async function api(method, path, body) {
    const token = getToken();
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (token) opts.headers['Authorization'] = `Bearer ${token}`;
    if (body !== undefined) opts.body = JSON.stringify(body);

    const res = await fetch(path, opts);

    if (res.status === 401) {
        clearAuth();
        location.href = '/index.html';
        return null;
    }

    const data = await res.json();
    if (!res.ok) {
        const err = (data && data.detail) || data || {};
        const e = new Error(err.msg || '오류가 발생했습니다');
        e.code = err.code;
        e.status = res.status;
        throw e;
    }
    return data;
}
