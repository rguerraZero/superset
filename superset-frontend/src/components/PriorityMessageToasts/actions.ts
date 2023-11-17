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

export interface PriorityMessageToastMeta {
  message: string;
  toastType: PriorityMessageToastType;
  duration: number;
}

export type PriorityMessageToastType = 'info' | 'loading';

export const SET_PRIORITY_TOAST = 'SET_PRIORITY_TOAST';
export function setPriorityToast({
  message,
  duration = 0,
}: PriorityMessageToastMeta) {
  return {
    type: SET_PRIORITY_TOAST,
    toastType: 'info',
    duration,
    message,
  };
}

export function setPriorityLoadingToast({ message }: PriorityMessageToastMeta) {
  return {
    type: SET_PRIORITY_TOAST,
    toastType: 'loading',
    duration: 0,
    message,
  };
}

export const REMOVE_PRIORITY_TOAST = 'REMOVE_PRIORITY_TOAST';
export function removePriorityToast() {
  return {
    type: REMOVE_PRIORITY_TOAST,
  };
}

export const priorityMessageToastOptions = {
  setPriorityToast,
};
