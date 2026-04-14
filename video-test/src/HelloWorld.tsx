import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const HelloWorld: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    config: { damping: 10 },
    durationInFrames: 30,
  });

  const opacity = Math.min(1, frame / 15);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0b84f3",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          color: "white",
          fontSize: 80,
          fontWeight: "bold",
          transform: `scale(${scale})`,
          opacity,
          fontFamily: "sans-serif",
          textAlign: "center",
          textShadow: "0 4px 20px rgba(0,0,0,0.3)",
        }}
      >
        Hello World!
      </div>
      <div
        style={{
          color: "rgba(255,255,255,0.7)",
          fontSize: 28,
          marginTop: 20,
          opacity,
          fontFamily: "sans-serif",
        }}
      >
        Local Remotion Render Pipeline ✓
      </div>
    </AbsoluteFill>
  );
};
