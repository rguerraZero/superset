# Add new plugin

To facilitate the process to add a new plugin, there are two samples that can be copied and edited.

## SampleBlankPlugin

This one is a React Component that can be overwriten with any logic for both processing and visualizing data. The base code was obtained by following the official tutorial here: https://superset.apache.org/docs/contributing/creating-viz-plugins/

To create a new one:

1. Copy `superset-frontend/plugins/plugin-sample-blank-chart` to a folder with a name for the new plugin
2. Replace `PluginSampleBlankChart` with the name of the new chart
3. There are two kinds of charts: Regular or Time Series. If your new chart is a Time Series one, you need to:
  a. Uncomment block on superset-frontend/plugins/<name>/src/plugin/transformProps.ts:63-68
  b. Uncomment line on superset-frontend/plugins/<name>/src/plugin/buildQuery.ts:42
4. Write the code you need

Finally you just need to import and load the package into superset-frontend/src/visualizations/presets/MainPreset.js

```js
import { PluginName } from 'plugins/<plugin-name>/src';
// ...
new PluginName().configure({ key: plugin-name }),
```

Now to run the code you need to recompile the frontend with `ASSET_BASE_URL=http://localhost:8000/spa_bff/superset npm run build-dev`. The plugin should be available to be used on a new Chart

## Echart plugin

Superset has many plugins integrated from echarts (https://echarts.apache.org/examples/en/index.html), but not all of them. If a chart is on the examples, is possible to integrate it by reusing some of the logic on an existing plugin.

This guide will show an example on how to integrate a new chart from echart. It will integrate the Calendar Heatmap Chart that is not integrated (currently Superset has a legacy Calendar Heatmap Chart that is not from echarts).

1. Copy `superset-frontend/plugins/plugin-chart-echarts/src/SampleChart`  to a folder with a name for the new plugin
2. Replace SampleChart with the name of the chart
3. The most important file to overwrite is the `TransformProps.ts`, where you need to specify the options of the chart that are on the Echart website
4. Write other files as needed
5. Export it on `superset-frontend/plugins/plugin-chart-echarts/src/index.ts`

Finally you just need to import and load the package into `superset-frontend/src/visualizations/presets/MainPreset.js`

```js
import { PluginName } from 'plugins/<plugin-name>/src';
// ...
new PluginName().configure({ key: plugin-name }),
```

Now to run the code you need to recompile the frontend with `ASSET_BASE_URL=http://localhost:8000/spa_bff/superset npm run build-dev`. The plugin should be available to be used on a new Chart

# References

- https://echarts.apache.org/examples/en/index.html
- https://superset.apache.org/docs/contributing/creating-viz-plugins/

# File references

All plugins charts have the same structure:

## types.ts

Defines the basic types of the plugin. In the code generated sample it includes StylesProps and CustomizeProps. The first one refers to visual (CSS) and the second to props to customize data to be visualized.

It also defines QueryFormData, which is a combination of Superset QueryFormData, StylesProps and CustomizeProps. The QueryFormData is the data that is passed into the chart to be visualized.

## .TSX file

The props are used on the React Component. In the base example, this file contains the CSS styles and HTML structure that is going to be rendered. It also render a simple <pre> block to render a simple JSON with the data passed into the chart:

## buildQuery.ts

This file is used to preprocess the arguments that are going to be passed into the request that is made to the backend to fetch the data.

In here you can use any of the values defined on the ControlPanel.ts

## controlPanel.ts

In here you can customize and add selectors to the chart

There are two sections, where usually the first one is the filters to query the data and the second is to customize the visual appearance of the chart.

In the example, the section Customize matches all the Props that are passed into the ReactComponent.

## index.ts

This file defines some sample metadata of the plugin, like the tile, description, tags and so on. It is good to look into an existing plugin to review all the available options.

## transformProps.ts

This code is executed when the data is returned from the backend. Here you can customize and process the data to match the visualization specifications.

## ./images/thumbnail

The thumbnail to be shown when the Plugin Chart is selected when creating a new Chart.
