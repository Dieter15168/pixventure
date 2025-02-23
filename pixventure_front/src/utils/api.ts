// src/utils/api.ts

export const fetchPosts = async () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    const response = await fetch(`${apiUrl}/posts/`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch posts');
    }
  
    const data = await response.json();
    return data.results;
  };
  