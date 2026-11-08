import React from "react";
import { Composition } from "remotion";
import { Reel } from "./Reel";
import { PLAN_VACIO, Plan } from "./plan";

// 1080x1920 a 30 fps. La duración sale del plan (props.plan.frames) que escribe preparar.py.
export const Root: React.FC = () => (
  <Composition
    id="Presentador"
    component={Reel as unknown as React.FC<Record<string, unknown>>}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={PLAN_VACIO.frames}
    defaultProps={{ plan: PLAN_VACIO } as Record<string, unknown>}
    calculateMetadata={({ props }) => ({ durationInFrames: Math.max(30, ((props as { plan: Plan }).plan || PLAN_VACIO).frames) })}
  />
);
