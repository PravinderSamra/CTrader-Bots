import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

// ── Timing (frames @ 30 fps) ──────────────────────────────────────────────────
// Scene 1:  0–115   girl walks up path (back view)
// Scene 2: 115–165  two knocks on door
// Scene 3: 175–215  cross-dissolve → front-view close-up
// Scene 4: 225–295  door swings open, warm light floods her face
// Total  : 300 frames = 10 s

const T = {
  FADE_IN:    [0,  25] as const,
  WALK:       [20, 115] as const,
  KNOCK1:     [122, 138] as const,
  KNOCK2:     [148, 164] as const,
  TRANSITION: [175, 215] as const,
  DOOR_OPEN:  [225, 292] as const,
};

const ci = (
  frame: number,
  range: readonly [number, number],
  from = 0,
  to   = 1,
) =>
  interpolate(frame, [...range], [from, to], {
    extrapolateLeft:  "clamp",
    extrapolateRight: "clamp",
  });

// ── Stars ─────────────────────────────────────────────────────────────────────
const STARS = Array.from({ length: 55 }, (_, i) => ({
  cx: ((i * 197 + 31) % 1200) + 40,
  cy: ((i * 83)       % 370)  + 10,
  r:  (i % 4) * 0.55 + 0.8,
  op: 0.25 + (i % 6) * 0.12,
}));

const Stars: React.FC<{ t: number }> = ({ t }) => (
  <>
    {STARS.map((s, i) => (
      <circle
        key={i} cx={s.cx} cy={s.cy}
        r={s.r * (1 + (i % 5 === 0 ? Math.sin(t + i * 0.7) * 0.35 : 0))}
        fill="white" opacity={s.op}
      />
    ))}
  </>
);

// ── Tree silhouettes ──────────────────────────────────────────────────────────
const TREES: [number, number, number][] = [
  [55,  445, 0.72], [195, 435, 0.82],
  [1085, 440, 0.76], [1200, 430, 0.64],
];

const Trees: React.FC = () => (
  <>
    {TREES.map(([x, y, s], i) => (
      <g key={i} transform={`translate(${x},${y}) scale(${s})`}>
        <rect x={-9} y={0} width={18} height={45} fill="#070F1A" />
        <polygon points="0,-120 -44,0 44,0"    fill="#070F1A" />
        <polygon points="0,-172 -32,-55 32,-55" fill="#070F1A" />
        <polygon points="0,-214 -22,-110 22,-110" fill="#070F1A" />
      </g>
    ))}
  </>
);

// ── Garden path ───────────────────────────────────────────────────────────────
// Perspective trapezoid from bottom of screen to house door
const Path: React.FC = () => (
  <>
    <polygon points="405,720 875,720 682,465 598,465" fill="#4E342E" opacity={0.75} />
    {[0.12, 0.32, 0.52, 0.72, 0.90].map((p, i) => {
      const cy = 720 - p * (720 - 465);
      const rx = 88 - p * 58;
      return (
        <ellipse key={i} cx={640} cy={cy}
          rx={rx} ry={rx * 0.38} fill="#5D4037" opacity={0.5}
        />
      );
    })}
  </>
);

// ── Gingerbread House ─────────────────────────────────────────────────────────
// House is translated so wall-bottom (y=200 rel) sits on ground (y=490 abs)
// → translate(640, 290)
const House: React.FC<{ doorOpen: number }> = ({ doorOpen }) => {
  // Door panel narrows as it swings inward (2-D perspective approximation)
  const doorW = interpolate(doorOpen, [0, 1], [58, 2], {
    extrapolateRight: "clamp",
  });

  return (
    <g transform="translate(640,290)">
      {/* Ground shadow */}
      <ellipse cx={0} cy={200} rx={130} ry={18} fill="#000" opacity={0.22} />

      {/* Walls */}
      <rect x={-115} y={0} width={230} height={200} fill="#8B5E3C" />
      {/* Wall shading */}
      <rect x={-115} y={0} width={230} height={200} fill="#3E1500" opacity={0.18} />

      {/* Roof */}
      <polygon points="-142,-97 0,-215 142,-97" fill="#5C2F0E" />
      {/* Icing drips */}
      {Array.from({ length: 15 }, (_, i) => {
        const rx = -135 + i * 19;
        const dh = 8 + (i % 3) * 6;
        return (
          <g key={i}>
            <circle cx={rx} cy={-92} r={7} fill="white" />
            <rect x={rx - 4} y={-92} width={8} height={dh} fill="white" rx={3} />
          </g>
        );
      })}

      {/* Chimney */}
      <rect x={55} y={-200} width={28} height={68} fill="#5C2F0E" />
      <rect x={53} y={-205} width={32} height={12} fill="#4A2308" />

      {/* Windows */}
      {([-82, 33] as number[]).map((wx, i) => (
        <g key={i}>
          <rect x={wx} y={25} width={56} height={55} fill="#FFF9C4" rx={3} />
          <rect x={wx} y={25} width={56} height={55} fill="#FFD54F" rx={3} opacity={0.55} />
          {/* panes */}
          <line x1={wx + 28} y1={25} x2={wx + 28} y2={80} stroke="#8B5E3C" strokeWidth={3} />
          <line x1={wx}      y1={52} x2={wx + 56} y2={52} stroke="#8B5E3C" strokeWidth={3} />
        </g>
      ))}

      {/* Door surround / frame */}
      <rect x={-30} y={92} width={60} height={108} fill="#3E1F00" rx="5 5 0 0" />

      {/* Interior warm light revealed as door opens */}
      <rect x={-30} y={92} width={60} height={108}
        fill="#FF8F00" opacity={doorOpen * 0.92} rx="5 5 0 0" />

      {/* Door panel */}
      <rect x={-30} y={92} width={doorW} height={108} fill="#7B3F00" rx="5 5 0 0" />
      {doorW > 18 && (
        <circle cx={-30 + doorW - 14} cy={150} r={5} fill="#FFD700" />
      )}

      {/* Ground glow spilling from open door */}
      <ellipse cx={0} cy={200}
        rx={doorOpen * 150} ry={doorOpen * 48}
        fill="#FFD54F" opacity={doorOpen * 0.48}
      />

      {/* Candy canes */}
      {([-127, 117] as number[]).map((cxPos, i) => (
        <g key={i}>
          <rect x={cxPos - 4} y={145} width={8} height={58}
            fill="white" rx={4} />
          <rect x={cxPos - 4} y={145} width={8} height={58}
            fill="none" stroke="#E53935" strokeWidth={3}
            strokeDasharray="7 7" rx={4} />
          <path
            d={i === 0
              ? `M${cxPos},145 Q${cxPos},126 ${cxPos + 17},124`
              : `M${cxPos},145 Q${cxPos},126 ${cxPos - 17},124`}
            fill="none" stroke="white"   strokeWidth={8} strokeLinecap="round" />
          <path
            d={i === 0
              ? `M${cxPos},145 Q${cxPos},126 ${cxPos + 17},124`
              : `M${cxPos},145 Q${cxPos},126 ${cxPos - 17},124`}
            fill="none" stroke="#E53935" strokeWidth={4} strokeLinecap="round" />
        </g>
      ))}
    </g>
  );
};

// ── Girl — back view ──────────────────────────────────────────────────────────
// Camera faces her back; she walks away up the path toward the house.
// Feet anchor to ground: translate_y = 490 − 82 × scale
const GirlBack: React.FC<{
  walkP:      number;
  frame:      number;
  knockPhase: number;
}> = ({ walkP, frame, knockPhase }) => {
  const scale = interpolate(walkP, [0, 1], [1.20, 0.38]);
  const ty    = 490 - 82 * scale;          // feet stay on ground

  // Leg swing while walking, stops when she reaches the door
  const swing = walkP < 0.97 ? Math.sin(frame * 0.36) * 14 * (1 - walkP * 0.4) : 0;

  // Knocking arm: sinusoidal extend-and-retract
  const armAng = Math.sin(knockPhase * Math.PI) * 38;

  return (
    <g transform={`translate(640,${ty}) scale(${scale})`}>
      {/* Ground shadow */}
      <ellipse cx={0} cy={82} rx={36} ry={9} fill="#000" opacity={0.28} />

      {/* Cloak body */}
      <path
        d="M-44,-52 Q-58,5 -50,62 Q0,76 50,62 Q58,5 44,-52 Q0,-68 -44,-52"
        fill="#C62828"
      />
      {/* Shadow fold on cloak */}
      <path
        d="M-29,-50 Q-40,10 -34,58"
        stroke="#9B0000" strokeWidth={7} fill="none"
        strokeLinecap="round" opacity={0.45}
      />
      {/* Hood back */}
      <ellipse cx={0} cy={-56} rx={29} ry={29} fill="#B71C1C" />
      <ellipse cx={0} cy={-40} rx={33} ry={18} fill="#C62828" />

      {/* Left leg */}
      <g transform={`rotate(${swing}, -11, 58)`}>
        <rect x={-18} y={54} width={13} height={34} fill="#1A1A2E" rx={5} />
        <ellipse cx={-12} cy={88} rx={10} ry={6} fill="#1A1A2E" />
      </g>
      {/* Right leg */}
      <g transform={`rotate(${-swing}, 11, 58)`}>
        <rect x={5}   y={54} width={13} height={34} fill="#1A1A2E" rx={5} />
        <ellipse cx={12} cy={88} rx={10} ry={6} fill="#1A1A2E" />
      </g>

      {/* Knocking arm (only visible during knocks) */}
      {knockPhase > 0 && (
        <g transform={`translate(40,4) rotate(${-28 + armAng})`}>
          <rect x={0} y={-4} width={9} height={40} fill="#C62828" rx={4} />
          <circle cx={4.5} cy={41} r={10} fill="#FFCCBC" />
        </g>
      )}
    </g>
  );
};

// ── Girl — front view (close-up) ──────────────────────────────────────────────
// Camera has swung around; warm door-light illuminates her face.
const GirlFront: React.FC<{ lightI: number }> = ({ lightI }) => {
  const glow = lightI * 0.48;

  return (
    <g transform="translate(640,415)">
      {/* Hood outer shadow */}
      <path
        d="M-80,-95 Q-86,-15 -68,84 Q0,114 68,84 Q86,-15 80,-95 Q0,-160 -80,-95"
        fill="#8B0000"
      />
      {/* Hood */}
      <path
        d="M-70,-80 Q-75,-8 -58,74 Q0,100 58,74 Q75,-8 70,-80 Q0,-140 -70,-80"
        fill="#C62828"
      />
      {/* Hood highlight */}
      <path
        d="M-54,-72 Q-58,-2 -44,66"
        stroke="#E53935" strokeWidth={6} fill="none"
        strokeLinecap="round" opacity={0.35}
      />

      {/* Neck */}
      <rect x={-12} y={58} width={24} height={22} fill="#FFCCBC" rx={6} />

      {/* Face */}
      <ellipse cx={0} cy={0} rx={50} ry={57} fill="#FFCCBC" />

      {/* Warm door-light wash on face (increases with doorOpen) */}
      <ellipse cx={16} cy={8} rx={52} ry={58}
        fill={`rgba(255,140,30,${glow})`} />

      {/* Whites of eyes */}
      <ellipse cx={-17} cy={-9} rx={10} ry={11} fill="white" />
      <ellipse cx={ 17} cy={-9} rx={10} ry={11} fill="white" />
      {/* Irises */}
      <ellipse cx={-16} cy={-8} rx={7} ry={8} fill="#3E2723" />
      <ellipse cx={ 18} cy={-8} rx={7} ry={8} fill="#3E2723" />
      {/* Pupils */}
      <circle cx={-15} cy={-7} r={3.5} fill="#111" />
      <circle cx={ 19} cy={-7} r={3.5} fill="#111" />
      {/* Catchlights grow with door light */}
      <circle cx={-11} cy={-11} r={1.5 + lightI * 2.2} fill="white" opacity={0.9} />
      <circle cx={ 23} cy={-11} r={1.5 + lightI * 2.2} fill="white" opacity={0.9} />

      {/* Eyebrows */}
      <path d="M-27,-23 Q-17,-30 -7,-23"
        fill="none" stroke="#5D4037" strokeWidth={2.5} strokeLinecap="round" />
      <path d="M 7,-23 Q 17,-30 27,-23"
        fill="none" stroke="#5D4037" strokeWidth={2.5} strokeLinecap="round" />

      {/* Eyelashes */}
      {[-22, -16, -10].map((lx, i) => (
        <line key={i} x1={lx} y1={-19} x2={lx - 1} y2={-24}
          stroke="#1A1A1A" strokeWidth={1.5} />
      ))}
      {[10, 16, 23].map((lx, i) => (
        <line key={i} x1={lx} y1={-19} x2={lx + 1} y2={-24}
          stroke="#1A1A1A" strokeWidth={1.5} />
      ))}

      {/* Nose */}
      <path d="M-4,9 Q0,20 4,9"
        fill="none" stroke="#E8A090" strokeWidth={2} strokeLinecap="round" />

      {/* Mouth — open in wonder */}
      <path d="M-15,30 Q0,46 15,30" fill="#C2185B" opacity={0.85} />
      <path d="M-13,31 Q0,44 13,31"
        fill="none" stroke="#880E4F" strokeWidth={2.5} strokeLinecap="round" />

      {/* Rosy cheeks (brighten with light) */}
      <ellipse cx={-35} cy={14} rx={14} ry={9}
        fill="#FF7043" opacity={0.20 + lightI * 0.28} />
      <ellipse cx={ 35} cy={14} rx={14} ry={9}
        fill="#FF7043" opacity={0.20 + lightI * 0.28} />

      {/* Freckles */}
      {([ [-10, 22], [10, 22], [-24, 8], [24, 8] ] as [number,number][])
        .map(([fx, fy], i) => (
          <circle key={i} cx={fx} cy={fy} r={1.8} fill="#C4805A" opacity={0.55} />
        ))}
    </g>
  );
};

// ── Main Composition ──────────────────────────────────────────────────────────
export const RedHoodScene: React.FC = () => {
  const frame = useCurrentFrame();

  const fadeIn     = ci(frame, T.FADE_IN);
  const walkP      = ci(frame, T.WALK);
  const knock1     = ci(frame, T.KNOCK1);
  const knock2     = ci(frame, T.KNOCK2);
  const transP     = ci(frame, T.TRANSITION);
  const doorOpen   = ci(frame, T.DOOR_OPEN);

  // knockPhase is the active knock value (0 when neither knock is in progress)
  const knockPhase =
    knock1 > 0 && knock1 < 1 ? knock1 :
    knock2 > 0 && knock2 < 1 ? knock2 : 0;

  const showBack  = transP < 1;
  const showFront = transP > 0;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0D1B2A", opacity: fadeIn }}>
      <svg width="1280" height="720" viewBox="0 0 1280 720">
        <defs>
          <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#060E1A" />
            <stop offset="65%"  stopColor="#0D1B2A" />
            <stop offset="100%" stopColor="#1A2744" />
          </linearGradient>
          <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#1B4D20" />
            <stop offset="100%" stopColor="#0A1E0B" />
          </linearGradient>
          <radialGradient id="moonGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%"   stopColor="#FFF9C4" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#FFF9C4" stopOpacity="0"    />
          </radialGradient>
        </defs>

        {/* ── SKY ── */}
        <rect width="1280" height="720" fill="url(#sky)" />
        <Stars t={frame * 0.07} />

        {/* Moon + soft halo */}
        <circle cx={175} cy={108} r={90}  fill="url(#moonGlow)" />
        <circle cx={175} cy={108} r={60}  fill="#FFFDE7" opacity={0.85} />
        {/* Subtle crater hints */}
        <circle cx={158} cy={94}  r={10}  fill="#F0EAB0" opacity={0.20} />
        <circle cx={185} cy={120} r={6}   fill="#F0EAB0" opacity={0.15} />

        {/* ── BACKGROUND TREES ── */}
        <Trees />

        {/* ── GROUND ── */}
        <rect x={0} y={490} width={1280} height={230} fill="url(#ground)" />

        {/* ── PATH ── */}
        <Path />

        {/* ── HOUSE ── */}
        <House doorOpen={doorOpen} />

        {/* ═══════════════════════════════════════════════════════════════
            BACK VIEW  — girl walking up path, then knocking
            ═══════════════════════════════════════════════════════════════ */}
        {showBack && (
          <g opacity={1 - transP}>
            <GirlBack walkP={walkP} frame={frame} knockPhase={knockPhase} />
          </g>
        )}

        {/* ═══════════════════════════════════════════════════════════════
            FRONT VIEW — camera has circled round; door opens on her face
            ═══════════════════════════════════════════════════════════════ */}
        {showFront && (
          <g opacity={transP}>
            {/* Dark vignette so her face reads against the night */}
            <rect width="1280" height="720" fill="#040B14" opacity={0.58} />

            {/* Warm glow of open doorway behind her */}
            <ellipse cx={640} cy={370}
              rx={doorOpen * 210} ry={doorOpen * 125}
              fill="#FF8F00" opacity={doorOpen * 0.38}
            />
            {/* Bright door-frame highlight */}
            <ellipse cx={640} cy={370}
              rx={doorOpen * 90}  ry={doorOpen * 55}
              fill="#FFE082" opacity={doorOpen * 0.55}
            />

            <GirlFront lightI={doorOpen} />
          </g>
        )}
      </svg>
    </AbsoluteFill>
  );
};
