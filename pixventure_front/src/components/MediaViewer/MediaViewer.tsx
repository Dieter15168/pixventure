// src/components/MediaViewer/MediaViewer.tsx
"use client";

import React, { useCallback, useState } from "react";
import ZoomableImage from "@/components/ZoomableImage/ZoomableImage";
import VideoJSPlayer from "@/components/VideoJSPlayer/VideoJSPlayer";
import styles from "./MediaViewer.module.scss";

export type MediaType = "video" | "image";

interface MediaViewerProps {
  src: string;
  alt?: string;
  imageWidth?: number;
  imageHeight?: number;
  onLoadComplete?: () => void;
  fallbackMediaType?: MediaType;
  posterUrl?: string;
  higherResolutionAvailable?: boolean;
}

/**
 * MediaViewer
 * -----------
 * Renders either a ZoomableImage for images or
 * a VideoJSPlayer for videos.
 *
 * If "higherResolutionAvailable" is true:
 *  - The video will not loop.
 *  - When playback finishes, a modal is automatically shown.
 *
 * If false:
 *  - The video will auto-loop.
 */
const MediaViewer: React.FC<MediaViewerProps> = ({
  src,
  alt = "",
  imageWidth,
  imageHeight,
  onLoadComplete,
  fallbackMediaType,
  posterUrl,
  higherResolutionAvailable,
}) => {
  const isVideo = determineIfVideo(src, fallbackMediaType);
  const [videoLoading, setVideoLoading] = useState(true);

  const handleImageLoaded = useCallback(() => {
    onLoadComplete?.();
  }, [onLoadComplete]);

  const handleVideoReady = useCallback(() => {
    setVideoLoading(false);
    onLoadComplete?.();
  }, [onLoadComplete]);

  if (!isVideo) {
    // Render the ZoomableImage for images
    return (
      <ZoomableImage
        src={src}
        alt={alt}
        imageWidth={imageWidth}
        imageHeight={imageHeight}
        onLoadComplete={handleImageLoaded}
      />
    );
  }

  // Build the options object for VideoJSPlayer.
  // If higherResolutionAvailable is false, we auto-loop the video.
  const videoOptions = {
    controls: true,
    autoplay: false,
    preload: "auto",
    poster: posterUrl,
    sources: [{ src, type: "video/mp4" }],
    loop: !higherResolutionAvailable,
  };

  return (
    <div className={styles.videoContainer}>
      <VideoJSPlayer
        options={videoOptions}
        onReady={handleVideoReady}
        higherResolutionAvailable={higherResolutionAvailable}
      />
      {videoLoading && (
        <div className={styles.videoSpinnerOverlay}>
          <div className={styles.spinner} />
        </div>
      )}
    </div>
  );
};

function determineIfVideo(src: string, fallback?: MediaType): boolean {
  if (fallback) return fallback === "video";
  const lower = src.toLowerCase();
  return lower.endsWith(".mp4") || lower.endsWith(".mov") || lower.endsWith(".m4v");
}

export default MediaViewer;
