import Cookies from 'js-cookie';

/**
 * Saves the authentication token in both cookie and localStorage for redundancy
 * @param token The JWT token to save
 * @returns boolean indicating success or failure
 */
export const saveToken = (token: string): boolean => {
  try {
    // Basic cookie with just expiration
    Cookies.set('lingogi_token', token, { expires: 7 });
    
    // Also store in localStorage as backup
    localStorage.setItem('lingogi_token', token);
    
    console.log('Token saved successfully');
    return true;
  } catch (err) {
    console.error('Error saving token:', err);
    return false;
  }
};

/**
 * Gets the authentication token from either cookie or localStorage
 * @returns The token if found, null otherwise
 */
export const getToken = (): string | null => {
  // Try cookie first, then localStorage
  let token: string | null | undefined = Cookies.get('lingogi_token');
  
  // If not in cookie, try localStorage
  if (!token) {
    // localStorage.getItem returns string | null
    const localToken = localStorage.getItem('lingogi_token');
    
    // If found in localStorage but not in cookie, restore the cookie
    if (localToken) {
      console.log('Token found in localStorage but not in cookie, restoring cookie');
      Cookies.set('lingogi_token', localToken, { expires: 7 });
      token = localToken;
    }
  }
  
  return token || null;
};

/**
 * Removes the authentication token from both cookie and localStorage
 * @returns boolean indicating success or failure
 */
export const removeToken = (): boolean => {
  try {
    Cookies.remove('lingogi_token');
    localStorage.removeItem('lingogi_token');
    return true;
  } catch (err) {
    console.error('Error removing token:', err);
    return false;
  }
};
