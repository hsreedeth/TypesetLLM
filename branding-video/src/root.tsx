import React from 'react';
import {Composition} from 'remotion';
import {BrandingCycle} from './scene';

export const Root: React.FC = () => (
  <Composition
    id="BrandingCycle"
    component={BrandingCycle}
    durationInFrames={330}
    fps={30}
    width={814}
    height={792}
  />
);
