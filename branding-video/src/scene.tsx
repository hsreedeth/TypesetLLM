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
  {at: 1.25, name: 'Claude'},
  {at: 2.35, name: 'Gemini'},
  {at: 3.30, name: 'Kimi.ai'},
  {at: 4.15, name: 'DeepSeek'},
  {at: 4.90, name: 'ChatGPT'},
  {at: 5.55, name: 'Claude'},
  {at: 6.10, name: 'Gemini'},
  {at: 6.55, name: 'Kimi.ai'},
  {at: 6.91, name: 'DeepSeek'},
  {at: 7.19, name: 'ChatGPT'},
  {at: 7.42, name: 'Claude'},
  {at: 7.61, name: 'Gemini'},
  {at: 7.78, name: 'Kimi.ai'},
  {at: 7.94, name: 'DeepSeek'},
  {at: 8.10, name: 'ChatGPT'},
  {at: 8.27, name: 'Claude'},
  {at: 8.46, name: 'Gemini'},
  {at: 8.69, name: 'Kimi.ai'},
  {at: 8.97, name: 'DeepSeek'},
  {at: 9.33, name: 'ChatGPT'},
  {at: 9.79, name: 'Claude'},
  {at: 10.37, name: 'Gemini'},
  {at: 11.10, name: 'DeepSeek'},
  {at: 11.90, name: 'LLM'},
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
        <div style={{position: 'absolute', left: 405, top: -22, width: 850, height: 205, overflow: 'hidden', perspective: 900}}>
          {wordTimeline.map(({name}, index) => {
            const distance = position - index;
            if (Math.abs(distance) >= 1) return null;
            return (
              <div
                key={index}
                style={{
                  position: 'absolute',
                  left: 0,
                  top: 22,
                  opacity: Math.pow(1 - Math.abs(distance), 0.6),
                  transform: `translateY(${distance * 150}px) rotateX(${-distance * 36}deg)`,
                  transformOrigin: 'center center',
                  backfaceVisibility: 'hidden',
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
