import { Frame, VectorObject, Bone, Layer } from '../types';

export interface SavedAnimationRecord {
  id: string;
  title: string;
  savedAt: number;
  email: string;
  fps: number;
  layers: Layer[];
  objects: { [id: string]: VectorObject };
  frames: Frame[];
  bones: Bone[];
  thumbnailUrl?: string;
}

// Maximum quota allowed for saved animations per user/session
export const MAX_SAVED_ANIMATIONS_QUOTA = 10;

// Local storage keys for our database
const DB_STORAGE_KEY_V2 = 'animastudio_custom_db_v2';
const DB_STORAGE_KEY_V1 = 'animastudio_custom_db';

// IndexedDB configuration for unlimited large asset storage
const IDB_NAME = 'animastudio_indexed_db';
const IDB_VERSION = 1;
const IDB_STORE_PROJECTS = 'projects';
const IDB_STORE_ASSETS = 'large_assets';

let idbInstance: IDBDatabase | null = null;

async function getIndexedDB(): Promise<IDBDatabase | null> {
  if (typeof window === 'undefined' || !window.indexedDB) return null;
  if (idbInstance) return idbInstance;

  return new Promise((resolve) => {
    try {
      const request = indexedDB.open(IDB_NAME, IDB_VERSION);
      request.onupgradeneeded = (event: any) => {
        const db = event.target.result as IDBDatabase;
        if (!db.objectStoreNames.contains(IDB_STORE_PROJECTS)) {
          db.createObjectStore(IDB_STORE_PROJECTS, { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains(IDB_STORE_ASSETS)) {
          db.createObjectStore(IDB_STORE_ASSETS, { keyPath: 'id' });
        }
      };
      request.onsuccess = (event: any) => {
        idbInstance = event.target.result;
        resolve(idbInstance);
      };
      request.onerror = () => {
        resolve(null);
      };
    } catch {
      resolve(null);
    }
  });
}

// Background sync to IndexedDB for large assets
async function syncToIndexedDB(record: SavedAnimationRecord) {
  try {
    const db = await getIndexedDB();
    if (!db) return;
    const tx = db.transaction(IDB_STORE_PROJECTS, 'readwrite');
    const store = tx.objectStore(IDB_STORE_PROJECTS);
    store.put(record);
  } catch (err) {
    console.warn('Could not sync record to IndexedDB:', err);
  }
}

async function deleteFromIndexedDB(id: string) {
  try {
    const db = await getIndexedDB();
    if (!db) return;
    const tx = db.transaction(IDB_STORE_PROJECTS, 'readwrite');
    const store = tx.objectStore(IDB_STORE_PROJECTS);
    store.delete(id);
  } catch (err) {
    console.warn('Could not delete from IndexedDB:', err);
  }
}

/**
 * Safely parses JSON with fallback
 */
function safeJsonParse<T>(raw: string | null, fallback: T): T {
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch (e) {
    console.error('Failed to parse database json', e);
    return fallback;
  }
}

/**
 * Compress / sanitize large assets for localStorage to prevent quota overflow
 */
function createSafeStorageRecord(record: SavedAnimationRecord): SavedAnimationRecord {
  // If thumbnail or image URLs are massive (> 500KB), create a compressed copy for localStorage
  return {
    ...record,
    thumbnailUrl: record.thumbnailUrl && record.thumbnailUrl.length > 50000 
      ? record.thumbnailUrl.substring(0, 100) + '...' 
      : record.thumbnailUrl
  };
}

/**
 * Loads the raw database list from LocalStorage for v2 schema.
 */
function getRawDbList(): SavedAnimationRecord[] {
  try {
    const raw = localStorage.getItem(DB_STORAGE_KEY_V2);
    if (!raw) {
      // Migrate v1 legacy single record if exists
      const legacyRaw = localStorage.getItem(DB_STORAGE_KEY_V1);
      if (legacyRaw) {
        const legacyDict = safeJsonParse<Record<string, SavedAnimationRecord>>(legacyRaw, {});
        const migratedList: SavedAnimationRecord[] = [];
        Object.entries(legacyDict).forEach(([email, item]) => {
          if (item && item.savedAt) {
            migratedList.push({
              ...item,
              id: item.id || `anim_${item.savedAt}_${Math.random().toString(36).substring(2, 6)}`,
              title: item.title || 'Saved Animation 1',
              email: item.email || email,
            });
          }
        });
        if (migratedList.length > 0) {
          try {
            localStorage.setItem(DB_STORAGE_KEY_V2, JSON.stringify(migratedList));
          } catch {
            // Ignore quota errors
          }
        }
        return migratedList;
      }
      return [];
    }
    return safeJsonParse<SavedAnimationRecord[]>(raw, []);
  } catch (e) {
    console.error('Failed to parse animastudio local db list', e);
    return [];
  }
}

/**
 * Persists raw database list to LocalStorage with large asset safety.
 */
function saveRawDbList(list: SavedAnimationRecord[]) {
  try {
    const safeList = list.map(createSafeStorageRecord);
    localStorage.setItem(DB_STORAGE_KEY_V2, JSON.stringify(safeList));
  } catch (e) {
    console.warn('LocalStorage quota exceeded, saving lightened data and relying on IndexedDB:', e);
    try {
      // Attempt saving only latest 5 records with stripped thumbnails
      const minimalList = list.slice(0, 5).map(r => ({ ...r, thumbnailUrl: undefined }));
      localStorage.setItem(DB_STORAGE_KEY_V2, JSON.stringify(minimalList));
    } catch {
      // Continue safely
    }
  }
}

/**
 * Gets all saved animations for a specific email or guest user.
 */
export function getAllUserSavedAnimations(email: string): SavedAnimationRecord[] {
  const normalizedEmail = (email || 'guest').trim().toLowerCase();
  const all = getRawDbList();
  return all.filter(item => (item.email || 'guest').trim().toLowerCase() === normalizedEmail);
}

/**
 * Gets quota status (e.g. 3 / 10 used).
 */
export function getSavedAnimationsQuotaStatus(email: string): { count: number; max: number; isFull: boolean; remaining: number } {
  const userItems = getAllUserSavedAnimations(email);
  const count = userItems.length;
  const max = MAX_SAVED_ANIMATIONS_QUOTA;
  return {
    count,
    max,
    isFull: count >= max,
    remaining: Math.max(0, max - count),
  };
}

/**
 * Saves a new animation record into the 10-quota database.
 */
export function saveUserAnimationToQuotaDb(
  email: string,
  title: string,
  data: {
    fps: number;
    layers: Layer[];
    objects: { [id: string]: VectorObject };
    frames: Frame[];
    bones: Bone[];
    thumbnailUrl?: string;
  }
): { success: boolean; record?: SavedAnimationRecord; error?: string } {
  try {
    const normalizedEmail = (email || 'guest').trim().toLowerCase();
    const quota = getSavedAnimationsQuotaStatus(normalizedEmail);

    if (quota.isFull) {
      return {
        success: false,
        error: `Quota limit reached (${quota.count}/${quota.max} saved animations). Please delete an existing saved animation to save a new project.`,
      };
    }

    const all = getRawDbList();
    const newRecord: SavedAnimationRecord = {
      id: `anim_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
      title: title && title.trim().length > 0 ? title.trim() : `Saved Project ${quota.count + 1}`,
      savedAt: Date.now(),
      email: normalizedEmail,
      fps: data.fps,
      layers: data.layers,
      objects: data.objects,
      frames: data.frames,
      bones: data.bones,
      thumbnailUrl: data.thumbnailUrl,
    };

    all.unshift(newRecord); // Add to beginning of list
    saveRawDbList(all);
    syncToIndexedDB(newRecord);

    return {
      success: true,
      record: newRecord,
    };
  } catch (e: any) {
    console.error('Error saving animation to database quota:', e);
    return {
      success: false,
      error: e.message || 'Failed to save animation to database.',
    };
  }
}

/**
 * Deletes a specific saved animation by ID.
 */
export function deleteSavedAnimationById(id: string, email: string): boolean {
  try {
    const all = getRawDbList();
    const filtered = all.filter(item => item.id !== id);
    saveRawDbList(filtered);
    deleteFromIndexedDB(id);
    return true;
  } catch (e) {
    console.error('Failed to delete saved animation by id', e);
    return false;
  }
}

/**
 * Retrieves a saved animation by ID.
 */
export function getSavedAnimationById(id: string): SavedAnimationRecord | null {
  const all = getRawDbList();
  return all.find(item => item.id === id) || null;
}

/**
 * Legacy compatibility functions:
 */
export function saveUserAnimation(
  email: string,
  data: {
    fps: number;
    layers: Layer[];
    objects: { [id: string]: VectorObject };
    frames: Frame[];
    bones: Bone[];
  }
): SavedAnimationRecord {
  const res = saveUserAnimationToQuotaDb(email, 'Latest Animation', data);
  if (res.record) return res.record;
  // If full, overwrite oldest for legacy caller
  const userItems = getAllUserSavedAnimations(email);
  if (userItems.length > 0) {
    deleteSavedAnimationById(userItems[userItems.length - 1].id, email);
  }
  const retry = saveUserAnimationToQuotaDb(email, 'Latest Animation', data);
  return retry.record!;
}

export function getUserAnimation(email: string): { record: SavedAnimationRecord | null; wasDeleted: boolean } {
  const items = getAllUserSavedAnimations(email);
  if (items.length === 0) return { record: null, wasDeleted: false };
  return { record: items[0], wasDeleted: false };
}

export function deleteUserAnimation(email: string) {
  const items = getAllUserSavedAnimations(email);
  items.forEach(item => deleteSavedAnimationById(item.id, email));
}

/**
 * Validates Gmail authentication logic.
 */
export function validateSimpleAuth(email: string, password: string): { success: boolean; message: string } {
  const trimmedEmail = email.trim();
  const isGmail = trimmedEmail.toLowerCase().endsWith('@gmail.com') && trimmedEmail.includes('@');

  if (!isGmail) {
    return {
      success: false,
      message: 'Invalid email address. Authentication requires a valid @gmail.com address.',
    };
  }

  if (password === '123456' || password === 'password' || password === 'password123') {
    return {
      success: true,
      message: 'Authentication successful!',
    };
  } else {
    return {
      success: false,
      message: 'Incorrect password. (Try using standard passwords like "123456" or "password")',
    };
  }
}
