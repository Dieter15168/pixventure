// /components/ZoomableImage/ZoomableImage.tsx
"use client";

import React, { useCallback } from "react";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import styles from "./ZoomableImage.module.scss";

interface ZoomableImageProps {
  src: string;
  alt?: string;
  imageWidth?: number;
  imageHeight?: number;
  onLoadComplete?: () => void; // <--- add this
}

const ZoomableImage: React.FC<ZoomableImageProps> = ({
  src,
  alt = "",
  imageWidth,
  imageHeight,
  onLoadComplete,
}) => {
  // optional: if you have width/height, you can pass them to contentStyle

  const handleImageLoad = useCallback(() => {
    // Let parent know image is loaded
    if (onLoadComplete) {
      onLoadComplete();
    }
  }, [onLoadComplete]);

  return (
    <div className={styles.outerContainer}>
      <TransformWrapper
        limitToBounds={false}
        minScale={0.1}
        maxScale={5}
        initialScale={1}
        centerOnInit={true}
      >
        <TransformComponent
          contentStyle={{
            width: "100vw",
            height: "100vh",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <img
            src={src}
            alt={alt}
            className={styles.image}
            draggable={false}
            onLoad={handleImageLoad}
          />
        </TransformComponent>
      </TransformWrapper>
    </div>
  );
};

export default ZoomableImage;
