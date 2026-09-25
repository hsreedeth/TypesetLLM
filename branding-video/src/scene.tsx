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

// The model names accelerate from slow changes to four-frame flips, then decelerate.
export const wordTimeline = [
  {at: 0, name: 'ChatGPT'},
  {at: 36, name: 'Claude'},
  {at: 66, name: 'Gemini'},
  {at: 91, name: 'Kimi.ai'},
  {at: 112, name: 'DeepSeek'},
  {at: 130, name: 'ChatGPT'},
  {at: 145, name: 'Claude'},
  {at: 157, name: 'Gemini'},
  {at: 167, name: 'Kimi.ai'},
  {at: 175, name: 'DeepSeek'},
  {at: 181, name: 'ChatGPT'},
  {at: 186, name: 'Claude'},
  {at: 190, name: 'Gemini'},
  {at: 194, name: 'Kimi.ai'},
  {at: 198, name: 'DeepSeek'},
  {at: 202, name: 'ChatGPT'},
  {at: 207, name: 'Claude'},
  {at: 213, name: 'Gemini'},
  {at: 221, name: 'Kimi.ai'},
  {at: 232, name: 'DeepSeek'},
  {at: 246, name: 'ChatGPT'},
  {at: 264, name: 'Claude'},
  {at: 286, name: 'LLM'},
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

  const tryOpacity = interpolate(frame, [303, 326], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const tryY = interpolate(frame, [303, 326], [-30, 0], {...clamp, easing: Easing.out(Easing.cubic)});

  return (
    <AbsoluteFill style={{backgroundColor: '#fcf8f4', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{position: 'absolute', left: '25%', top: '46%', height: 180, fontFamily: 'Inter Brand, sans-serif', fontSize: 128, fontWeight: 400, letterSpacing: '-0.035em', whiteSpace: 'nowrap', color: '#0b0b0b'}}>
        <div style={{position: 'absolute', left: 0, top: 0}}>Typeset</div>
        {wordTimeline.map(({at, name}, index) => {
        const nextAt = wordTimeline[index + 1]?.at ?? 390;
        const previousAt = wordTimeline[index - 1]?.at ?? 0;
        const entering = index === 0 ? 0 : Math.min(12, Math.max(2, (at - previousAt) * 0.45));
        const leaving = index === wordTimeline.length - 1 ? 0 : Math.min(12, Math.max(2, (nextAt - at) * 0.45));
        const inOpacity = index === 0 ? 1 : interpolate(frame, [at, at + entering], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
        const outOpacity = index === wordTimeline.length - 1 ? 1 : interpolate(frame, [nextAt - leaving, nextAt], [1, 0], {...clamp, easing: Easing.in(Easing.cubic)});
        const opacity = Math.min(inOpacity, outOpacity);
        if (opacity <= 0) return null;
        const enterY = index === 0 ? 0 : interpolate(frame, [at, at + entering], [-46, 0], clamp);
        const exitY = index === wordTimeline.length - 1 ? 0 : interpolate(frame, [nextAt - leaving, nextAt], [0, 46], clamp);
        const enterFlip = index === 0 ? 0 : interpolate(frame, [at, at + entering], [65, 0], clamp);
        const exitFlip = index === wordTimeline.length - 1 ? 0 : interpolate(frame, [nextAt - leaving, nextAt], [0, -65], clamp);
        return (
          <div
            key={`${at}-${name}`}
            style={{
              position: 'absolute',
              left: 405,
              top: 0,
              opacity,
              transform: `perspective(700px) translateY(${enterY + exitY}px) rotateX(${enterFlip + exitFlip}deg)`,
              transformOrigin: 'center center',
              backfaceVisibility: 'hidden',
            }}
          >
            {name}
          </div>
        );
        })}
        <div style={{position: 'absolute', left: 0, top: -190, width: 760, textAlign: 'center', fontSize: 76, opacity: tryOpacity, transform: `translateY(${tryY}px)`}}>Try</div>
      </div>
    </AbsoluteFill>
  );
};
