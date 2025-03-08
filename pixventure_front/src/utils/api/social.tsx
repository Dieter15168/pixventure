// src/utils/api/social.ts
'use client';

import { useCallback } from 'react';
import useAxios from '../useAxios';

interface ToggleLikeResponse {
  success?: string;
  error?: string;
  likes_counter?: number;
  has_liked?: boolean;
}

export function useSocialAPI() {
  const axios = useAxios();

  /**
   * Toggle like/unlike on a particular target.
   * "action" can be "like" or "unlike".
   * "target_type" can be "post", "media", "album", "user_profile", etc.
   * "target_id" is the entity's ID.
   */
  const toggleLike = useCallback(async (entity_type: string, targetId: number, action: 'like' | 'unlike') => {
    const res = await axios.post('/social/like/', {
      target_type: entity_type,
      target_id: targetId,
      action, // "like" or "unlike"
    });
    return res.data as ToggleLikeResponse;
  }, [axios]);

  return { toggleLike };
}
