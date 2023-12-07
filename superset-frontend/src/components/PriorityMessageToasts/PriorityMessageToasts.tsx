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
import React, { useEffect, useState } from 'react';
import { styled } from '@superset-ui/core';
import { Interweave } from 'interweave';
import cx from 'classnames';
import Loader from 'src/assets/images/loading.gif';
import { PriorityMessageToastType } from './actions';

export interface VisualProps {
  position: 'bottom' | 'top';
}

const StyledPriorityToastPresenter = styled.div<VisualProps>`
  max-width: 600px;
  position: fixed;
  ${({ position }) => (position === 'bottom' ? 'bottom' : 'top')}: 0px;
  right: 0px;
  margin-right: 50px;
  margin-bottom: 50px;
  z-index: ${({ theme }) => theme.zIndex.max};
  word-break: break-word;

  .toast {
    background: ${({ theme }) => theme.colors.grayscale.dark1};
    border-radius: ${({ theme }) => theme.borderRadius};
    box-shadow: 0 2px 4px 0
      fade(
        ${({ theme }) => theme.colors.grayscale.dark2},
        ${({ theme }) => theme.opacity.mediumLight}
      );
    color: ${({ theme }) => theme.colors.grayscale.light5};
    opacity: 0;
    position: relative;
    transform: translateY(-100%);
    white-space: pre-line;
    will-change: transform, opacity;
    transition: transform ${({ theme }) => theme.transitionTiming}s,
      opacity ${({ theme }) => theme.transitionTiming}s;

    &:after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 6px;
      height: 100%;
    }
  }

  .toast > button {
    color: ${({ theme }) => theme.colors.grayscale.light5};
    opacity: 1;
  }

  .toast--visible {
    opacity: 1;
    transform: translateY(0);
  }
`;

const LoaderImg = styled.img`
  z-index: 99;
  width: 25px;
  height: unset;
  position: relative;
  margin: 3px;
`;

const ToastContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;

  span {
    padding: 0 11px;
  }
`;

type PriorityToastPresenterProps = Partial<VisualProps> & {
  message: string;
  toastType: PriorityMessageToastType;
  duration: number;
  removePriorityToast: () => any;
};

export default function PriorityToastPresenter({
  message,
  duration,
  toastType,
  position = 'bottom',
  removePriorityToast,
}: PriorityToastPresenterProps) {
  const [visible, setVisible] = useState(false);
  const showToast = () => {
    setVisible(true);
  };

  useEffect(() => {
    setTimeout(showToast);
    if (duration > 0) {
      setTimeout(removePriorityToast, duration);
    }
  }, [duration, removePriorityToast]);

  return (
    <>
      {message && (
        <StyledPriorityToastPresenter
          id="priority-toast-presenter"
          position={position}
        >
          <ToastContainer
            className={cx('alert', 'toast', visible && 'toast--visible')}
          >
            <Interweave content={message} />
            {toastType === 'loading' && (
              <LoaderImg
                className={cx('loading', position)}
                alt="Loading..."
                src={Loader}
                role="status"
              />
            )}
          </ToastContainer>
        </StyledPriorityToastPresenter>
      )}
    </>
  );
}
