// Functions for handling PKCE (Proof Key for Code Exchange) for OAuth2 authorization code flow
export function generateRandomString(length: number) {
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    return result;
}

export function sha256(plain: string) {
    const encoder = new TextEncoder();
    const data = encoder.encode(plain);
    return crypto.subtle.digest('SHA-256', data);
}

export function base64UrlEncode(arrayBuffer: ArrayBuffer) {
    let base64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
    base64 = base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    return base64;
}

export async function generateCodeChallenge(verifier: string) {
    const hashed = await sha256(verifier);
    return base64UrlEncode(hashed);
}
