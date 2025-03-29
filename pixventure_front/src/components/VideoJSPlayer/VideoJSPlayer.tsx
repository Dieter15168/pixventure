// src/components/VideoJSPlayer/VideoJSPlayer.tsx
import React, { useEffect, useRef } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';

type Player = ReturnType<typeof videojs>;
type PlayerOptions = Parameters<typeof videojs>[1];

interface VideoPlayerProps {
  options: PlayerOptions;
  onReady?: (player: Player) => void;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ options, onReady }) => {
  const videoRef = useRef<HTMLDivElement>(null);
  const playerRef = useRef<Player | null>(null);

  useEffect(() => {
    if (!videoRef.current) return;

    const videoElement = document.createElement('video-js');
    videoRef.current.appendChild(videoElement);

    const player = (playerRef.current = videojs(videoElement, options, () => {
      if (onReady) {
        onReady(player);
      }
    }));

    return () => {
      if (playerRef.current) {
        playerRef.current.dispose();
        playerRef.current = null;
      }
    };
  }, [options, onReady]);

  return <div data-vjs-player ref={videoRef} />;
};

export default VideoPlayer;
