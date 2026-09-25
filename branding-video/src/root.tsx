import React from 'react';
import {Composition} from 'remotion';
import {BrandingCycle} from './scene';

export const Root: React.FC = () => (
  <Composition
    id="BrandingCycle"
    component={BrandingCycle}
    durationInFrames={810}
    fps={60}
    width={1628}
    height={1584}
  />
);
