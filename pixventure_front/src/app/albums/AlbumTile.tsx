// app/albums/AlbumTile.tsx
interface Album {
    id: number;
    name: string;
    slug: string;
    status: number;
    likes_counter: number;
    posts_count: number;
    images_count: number;
    videos_count: number;
    owner_username: string;
    show_creator_to_others: boolean;
    created: string;
    updated: string;
  }
  
  export default function AlbumTile({ album }: { album: Album }) {
    return (
      <div style={{ border: '1px solid #ddd', padding: 10 }}>
        <h2>{album.name}</h2>
        <p>Owner: {album.owner_username}</p>
        <p>Likes: {album.likes_counter}</p>
        <p>Posts: {album.posts_count}</p>
        <p>Images: {album.images_count}, Videos: {album.videos_count}</p>
        <p>Created: {new Date(album.created).toLocaleString()}</p>
      </div>
    );
  }
  