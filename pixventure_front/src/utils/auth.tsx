// utils/auth.ts

export function saveAuthToken(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
  }
  
  export function getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }
  
  export function removeAuthToken() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  }
  