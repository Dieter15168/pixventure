"use client";

import React from "react";
import {
  TransformWrapper,
  TransformComponent
} from "react-zoom-pan-pinch";
import styles from "./ZoomableImage.module.scss";

interface ZoomableImageProps {
  src: string;
  alt?: string;
}

const ZoomableImage: React.FC<ZoomableImageProps> = ({ src, alt = "" }) => {
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
          <img src={src} alt={alt} className={styles.image} draggable={false} />
        </TransformComponent>
      </TransformWrapper>
    </div>
  );
};

export default ZoomableImage;
