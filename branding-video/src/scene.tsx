import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill,
  continueRender,
  delayRender,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

// Each timestamp is when the next name reaches the fixed title position.
// The intervals shrink gradually, then grow again; the motion never resets
// between names, so velocity stays continuous even at the fastest point.
export const wordTimeline = [
  {at: 0, name: 'ChatGPT'},
  {at: 0.43, name: 'Claude'},
  {at: 0.83, name: 'Gemini'},
  {at: 1.23, name: 'Kimi.ai'},
  {at: 1.63, name: 'DeepSeek'},
  {at: 1.90, name: 'ChatGPT'},
  {at: 2.05, name: 'Claude'},
  {at: 2.17, name: 'Gemini'},
  {at: 2.27, name: 'Kimi.ai'},
  {at: 2.37, name: 'DeepSeek'},
  {at: 2.52, name: 'ChatGPT'},
  {at: 2.73, name: 'Claude'},
  {at: 3.02, name: 'LLM'},
] as const;

function slopeAt(index: number): number {
  if (index === 0 || index === wordTimeline.length - 1) return 0;
  const previousGap = wordTimeline[index].at - wordTimeline[index - 1].at;
  const nextGap = wordTimeline[index + 1].at - wordTimeline[index].at;
  const previousSpeed = 1 / previousGap;
  const nextSpeed = 1 / nextGap;
  const weightPrevious = 2 * nextGap + previousGap;
  const weightNext = nextGap + 2 * previousGap;
  return (weightPrevious + weightNext) / (weightPrevious / previousSpeed + weightNext / nextSpeed);
}

export function reelPositionAt(seconds: number): number {
  const last = wordTimeline.length - 1;
  if (seconds <= 0) return 0;
  if (seconds >= wordTimeline[last].at) return last;

  const index = wordTimeline.findIndex((item, next) => next < last && seconds < wordTimeline[next + 1].at);
  const start = wordTimeline[index].at;
  const duration = wordTimeline[index + 1].at - start;
  const t = (seconds - start) / duration;
  const t2 = t * t;
  const t3 = t2 * t;
  const startTangent = duration * slopeAt(index);
  const endTangent = duration * slopeAt(index + 1);
  return (2 * t3 - 3 * t2 + 1) * index
    + (t3 - 2 * t2 + t) * startTangent
    + (-2 * t3 + 3 * t2) * (index + 1)
    + (t3 - t2) * endTangent;
}

export const BrandingCycle: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
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

  const position = reelPositionAt(frame / fps);

  return (
    <AbsoluteFill style={{backgroundColor: '#fcf8f4', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{position: 'absolute', left: '25%', top: '46%', height: 180, fontFamily: 'Inter Brand, sans-serif', fontSize: 128, fontWeight: 400, letterSpacing: '-0.035em', whiteSpace: 'nowrap', color: '#0b0b0b'}}>
        <div style={{position: 'absolute', left: 0, top: 0}}>Typeset</div>
        <div style={{position: 'absolute', left: 405, top: -70, width: 850, height: 300, overflow: 'hidden', maskImage: 'linear-gradient(to bottom, transparent, black 15%, black 85%, transparent)'}}>
          {wordTimeline.map(({name}, index) => {
            const distance = position - index;
            if (Math.abs(distance) >= 1) return null;
            return (
              <div
                key={index}
                style={{
                  position: 'absolute',
                  left: 0,
                  top: 70,
                  transform: `translateY(${distance * 170}px)`,
                }}
              >
                {name}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
