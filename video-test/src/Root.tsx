import React from "react";
import { Composition } from "remotion";
import { HelloWorld } from "./HelloWorld";
import { RedHoodScene } from "./RedHood";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="HelloWorld"
        component={HelloWorld}
        durationInFrames={150}
        fps={30}
        width={1280}
        height={720}
      />
      <Composition
        id="RedHoodScene"
        component={RedHoodScene}
        durationInFrames={300}
        fps={30}
        width={1280}
        height={720}
      />
    </>
  );
};
