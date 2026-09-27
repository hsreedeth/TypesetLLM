import React from 'react';
import {Composition} from 'remotion';
import {McpDemo} from './scene';
export const Root: React.FC = () => <Composition id="McpDemo" component={McpDemo} durationInFrames={270} fps={30} width={1920} height={1080}/>;
