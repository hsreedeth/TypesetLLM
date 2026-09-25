import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill,
  continueRender,
  delayRender,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';

// Spacing contracts into rapid, blurred swaps, then expands before the final hold.
export const wordTimeline = [
  {at: 0, name: 'ChatGPT'},
  {at: 34, name: 'Claude'},
  {at: 64, name: 'Gemini'},
  {at: 91, name: 'Kimi.ai'},
  {at: 115, name: 'DeepSeek'},
  {at: 135, name: 'ChatGPT'},
  {at: 152, name: 'Claude'},
  {at: 166, name: 'Gemini'},
  {at: 178, name: 'Kimi.ai'},
  {at: 188, name: 'DeepSeek'},
  {at: 196, name: 'ChatGPT'},
  {at: 203, name: 'Claude'},
  {at: 209, name: 'Gemini'},
  {at: 215, name: 'Kimi.ai'},
  {at: 221, name: 'DeepSeek'},
  {at: 228, name: 'Claude'},
  {at: 236, name: 'Gemini'},
  {at: 246, name: 'Kimi.ai'},
  {at: 258, name: 'DeepSeek'},
  {at: 274, name: 'LLM'},
] as const;

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export const BrandingCycle: React.FC = () => {
  const frame = useCurrentFrame();
  const [fontHandle] = useState(() => delayRender('Loading Inter'));

  useEffect(() => {
    let active = true;
    const loadFont = async () => {
      const face = new FontFace('Inter Brand', `url(${staticFile('Inter-Variable.ttf')})`, {
        weight: '100 900',
      });
      await face.load();
      document.fonts.add(face);
      if (active) continueRender(fontHandle);
    };
    loadFont().catch((error) => {
      console.error(error);
      if (active) continueRender(fontHandle);
    });
    return () => { active = false; };
  }, [fontHandle]);

  const rushBlur = interpolate(frame, [125, 188, 208, 227, 274], [0, 2, 9, 7, 0], clamp);

  return (
    <AbsoluteFill style={{backgroundColor: '#fcf8f4', justifyContent: 'center', alignItems: 'center'}}>
      {wordTimeline.map(({at, name}, index) => {
        const nextAt = wordTimeline[index + 1]?.at ?? 330;
        const previousAt = wordTimeline[index - 1]?.at ?? 0;
        const entering = index === 0 ? 0 : Math.min(12, Math.max(3, (at - previousAt) * 0.45));
        const leaving = index === wordTimeline.length - 1 ? 0 : Math.min(12, Math.max(3, (nextAt - at) * 0.45));
        const inOpacity = index === 0 ? 1 : interpolate(frame, [at, at + entering], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
        const outOpacity = index === wordTimeline.length - 1 ? 1 : interpolate(frame, [nextAt - leaving, nextAt], [1, 0], {...clamp, easing: Easing.in(Easing.cubic)});
        const opacity = Math.min(inOpacity, outOpacity);
        if (opacity <= 0) return null;
        const enterY = index === 0 ? 0 : interpolate(frame, [at, at + entering], [-24, 0], clamp);
        const exitY = index === wordTimeline.length - 1 ? 0 : interpolate(frame, [nextAt - leaving, nextAt], [0, 24], clamp);
        return (
          <div
            key={`${at}-${name}`}
            style={{
              position: 'absolute',
              width: '100%',
              textAlign: 'center',
              fontFamily: 'Inter Brand, sans-serif',
              fontSize: 64,
              fontWeight: 400,
              letterSpacing: '-0.035em',
              whiteSpace: 'nowrap',
              color: '#0b0b0b',
              opacity,
              transform: `translateY(${enterY + exitY}px)`,
              filter: `blur(${rushBlur}px)`,
            }}
          >
            Typeset{name}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
