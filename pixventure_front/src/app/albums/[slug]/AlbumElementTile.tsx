'use client';

interface AlbumElement {
  id: number;
  element_type: number;
  post_data: null | {
    id: number;
    slug: string;
    name: string;
    thumbnail_url: string;
    has_liked: boolean;
  };
  media_data: null | {
    id: number;
    media_type: string;
    thumbnail_url: string;
    has_liked: boolean;
  };
}

export default function AlbumElementTile({ element }: { element: AlbumElement }) {
  if (element.element_type === 1 && element.post_data) {
    // post_data
    return (
      <div style={{ border: '1px solid #ccc', padding: '10px' }}>
        <img src={element.post_data.thumbnail_url} alt={element.post_data.name} width={100} />
        <h4>Post: {element.post_data.name}</h4>
        <p>{element.post_data.has_liked ? 'Liked' : 'Not Liked'}</p>
      </div>
    );
  } else if (element.element_type === 2 && element.media_data) {
    // media_data
    return (
      <div style={{ border: '1px solid #ccc', padding: '10px' }}>
        <img src={element.media_data.thumbnail_url} alt={`Media ${element.media_data.id}`} width={100} />
        <h4>Media Item {element.media_data.id}</h4>
        <p>{element.media_data.has_liked ? 'Liked' : 'Not Liked'}</p>
      </div>
    );
  } else {
    return <div>Unknown album element</div>;
  }
}
