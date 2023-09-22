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
import { SyntheticEvent } from 'react';
import domToImage from 'dom-to-image-more';
import kebabCase from 'lodash/kebabCase';
import { t, supersetTheme, SupersetClient } from '@superset-ui/core';
import { addWarningToast } from 'src/components/MessageToasts/actions';

/**
 * generate a consistent file stem from a description and date
 *
 * @param description title or description of content of file
 * @param date date when file was generated
 */
const generateFileStem = (description: string, date = new Date()) =>
  `${kebabCase(description)}-${date.toISOString().replace(/[: ]/g, '-')}`;

/**
 * Create an event handler for turning an element into an image
 *
 * @param selector css selector of the parent element which should be turned into image
 * @param description name or a short description of what is being printed.
 *   Value will be normalized, and a date as well as a file extension will be added.
 * @returns event handler
 */
export default function downloadAsPDF(
  selector: string,
  description: string,
  onePage: string,
) {
  return (event: SyntheticEvent) => {
    const elementsToPrint = document.querySelectorAll(`[id^="${selector}"]`);

    if (!elementsToPrint) {
      return addWarningToast(
        t('PDF download failed, please refresh and try again.'),
      );
    }
    // Mapbox controls are loaded from different origin, causing CORS error
    // See https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/toDataURL#exceptions
    const filter = (node: Element) => {
      if (typeof node.className === 'string') {
        return (
          node.className !== 'mapboxgl-control-container' &&
          !node.className.includes('ant-dropdown')
        );
      }
      return true;
    };

    const selectedTab = document.querySelector<HTMLElement>(
      '.ant-tabs-tab-active',
    );

    const tabsDetails = {};
    const promises: Promise<string | void>[] = [];

    const tabsElements =
      document.querySelectorAll<HTMLElement>('.ant-tabs-tab');
    if (tabsElements.length > 0) {
      elementsToPrint.forEach((element, index) => {
        const clickTabPromise = new Promise(function (resolve) {
          setTimeout(() => {
            tabsElements[index].click();
            resolve('done');
          }, 2000 * index);
        });
        const waitToScreenshotPromise = new Promise(function (resolve) {
          setTimeout(() => {
            tabsElements[index].click();
            resolve('done');
          }, 2000 * index + 1000);
        });
        promises.push(
          clickTabPromise
            .then(() => waitToScreenshotPromise)
            .then(() =>
              domToImage.toJpeg(element, {
                quality: 0.95,
                bgcolor: supersetTheme.colors.grayscale.light4,
                filter,
              }),
            )
            .then(dataUrl => {
              const elementSize = element.getBoundingClientRect();
              tabsDetails[index] = {
                dataUrl,
                width: elementSize.width,
                height: elementSize.height,
              };
            }),
        );
      });
    } else {
      const elementToPrint = document.querySelector(onePage);
      if (!elementToPrint) {
        return addWarningToast(
          t('Image download failed, please refresh and try again.'),
        );
      }
      promises.push(
        domToImage
          .toJpeg(elementToPrint, {
            quality: 0.95,
            bgcolor: supersetTheme.colors.grayscale.light4,
            filter,
          })
          .then(dataUrl => {
            const elementSize = elementToPrint.getBoundingClientRect();
            tabsDetails[0] = {
              dataUrl,
              width: elementSize.width,
              height: elementSize.height,
            };
          }),
      );
    }
    const json = {
      report_name: description,
      date: new Date().toLocaleDateString(),
      image_urls: tabsDetails,
    };
    return Promise.all(promises)
      .then(() => {
        SupersetClient.post({
          endpoint: 'api/v1/download/download/',
          jsonPayload: json,
        }).then(returnVal => {
          if (tabsElements.length > 0) {
            selectedTab?.click();
          }
          const link = document.createElement('a');
          link.download = `${generateFileStem(description)}.pdf`;
          link.href = returnVal.json.result;
          link.click();
        });
      })
      .catch(e => {
        console.error('Creating image failed', e);
      });
  };
}
