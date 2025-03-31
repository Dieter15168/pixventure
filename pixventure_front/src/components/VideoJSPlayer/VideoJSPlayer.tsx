// src/components/VideoJSPlayer/VideoJSPlayer.tsx
import React, { useEffect, useRef } from "react";
import videojs from "video.js";
import "video.js/dist/video-js.css";
import { useModal } from "../../contexts/ModalContext"; // Modal context hook

type Player = ReturnType<typeof videojs>;
type PlayerOptions = Parameters<typeof videojs>[1];

interface VideoPlayerProps {
  options: PlayerOptions;
  onReady?: (player: Player) => void;
  /**
   * If true, the player will trigger a membership prompt modal
   * when the video finishes playing.
   */
  showMembershipPrompt?: boolean;
}

/**
 * VideoJSPlayer
 * -------------
 * Wraps the Video.js player and adds custom behavior.
 *
 * When "showMembershipPrompt" is true, an event listener is added
 * to trigger a modal when the video ends.
 */
const VideoJSPlayer: React.FC<VideoPlayerProps> = ({
  options,
  onReady,
  showMembershipPrompt,
}) => {
  const videoRef = useRef<HTMLDivElement>(null);
  const playerRef = useRef<Player | null>(null);
  const { showModal } = useModal(); // Get modal context

  useEffect(() => {
    if (!videoRef.current) return;

    // Create a video element and initialize video.js
    const videoElement = document.createElement("video-js");
    videoRef.current.appendChild(videoElement);

    const player = (playerRef.current = videojs(videoElement, options, () => {
      if (onReady) {
        onReady(player);
      }
    }));

    // If membership prompt is enabled, attach the "ended" event listener.
    let handleEnded: (() => void) | null = null;
    if (showMembershipPrompt) {
      handleEnded = () => {
        // Trigger the modal when video playback finishes.
        showModal("Unlock more features with a membership!");
      };
      player.on("ended", handleEnded);
    }

    // Cleanup: remove event listener and dispose of the player instance.
    return () => {
      if (handleEnded) {
        player.off("ended", handleEnded);
      }
      if (playerRef.current) {
        playerRef.current.dispose();
        playerRef.current = null;
      }
    };
  }, [options, onReady, showMembershipPrompt, showModal]);

  return <div data-vjs-player ref={videoRef} />;
};

export default VideoJSPlayer;
