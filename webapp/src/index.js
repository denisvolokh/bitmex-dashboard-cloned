import React from 'react';
import ReactDOM from 'react-dom';
import './scss/styles.scss';
import App from './app/App';
import { Provider } from 'react-redux';
import store from './store';

ReactDOM.render(
  <Provider store={store}>
    <App />
  </Provider>,
  document.getElementById('root'));
