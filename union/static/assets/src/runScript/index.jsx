/* eslint camelcase: 0 */
import React from 'react';
import ReactDOM from 'react-dom';
import RunScriptContainer from './RunScriptContainer';


const runViewContainer = document.getElementById('js-add-slice-container');
const bootstrap_data = JSON.parse(runViewContainer.getAttribute('data-bootstrap'))

ReactDOM.render(
  <RunScriptContainer bootstrap_data={bootstrap_data}/>,
    runScriptContainer,
);