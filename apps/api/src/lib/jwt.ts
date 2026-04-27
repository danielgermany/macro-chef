import { SignJWT, jwtVerify } from 'jose';
import type { Env } from './env.js';

export function getJwtSecretKey(env: Env): Uint8Array {
  return new TextEncoder().encode(env.JWT_SECRET);
}

export async function signAccessToken(userId: string, env: Env): Promise<string> {
  return await new SignJWT({})
    .setProtectedHeader({ alg: 'HS256' })
    .setSubject(userId)
    .setIssuedAt()
    .setExpirationTime('24h')
    .sign(getJwtSecretKey(env));
}

export async function verifyAccessToken(token: string, env: Env): Promise<string> {
  const { payload } = await jwtVerify(token, getJwtSecretKey(env));
  const sub = payload.sub;
  if (!sub || typeof sub !== 'string') {
    throw new Error('Invalid token subject');
  }
  return sub;
}
