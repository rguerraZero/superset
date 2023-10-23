/* eslint-disable */
/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import React from 'react';
import { styled } from '@superset-ui/core';
import cls from 'classnames';
import Loader from 'src/assets/images/loading.gif';

export type PositionOption =
  | 'floating'
  | 'inline'
  | 'inline-centered'
  | 'normal'
  | 'absolute';
export interface Props {
  position?: PositionOption;
  className?: string;
  image?: string;
  extraClass?: string;
}

const LoaderImg = styled.img`
  z-index: 99;
  width: 50px;
  height: unset;
  position: relative;
  margin: 10px;
  &.inline {
    margin: 0px;
    width: 30px;
  }
  &.inline-centered {
    margin: 0 auto;
    width: 30px;
    display: block;
  }
  &.floating {
    padding: 0;
    margin: 0;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
  }
  &.download-pdf {
    top: 0px;
    right: 0px;
    bottom: 0px;
    background: #f7f7f7;
    padding: 48vh 48vw;
    width: 100vw;
    visibility: hidden;
    height: 100vh;
    position: absolute;
    margin: 0px;
  }
`;

export default function Loading({
  position = 'floating',
  image,
  className,
  extraClass,
}: Props) {
  return (
    <LoaderImg
      className={cls('loading', position, className, extraClass)}
      alt="Loading..."
      src={image || Loader}
      role="status"
      aria-live="polite"
      aria-label="Loading"
      data-test="loading-indicator"
    />
  );
}
