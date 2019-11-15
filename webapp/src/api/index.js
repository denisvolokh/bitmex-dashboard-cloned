const apiType = {
  prod: 'http://0.0.0.0:5000',
  test: 'http://ac0ffeea.ngrok.io',
};

const socketType = {
  prod: 'ws://0.0.0.0:5000/ws/ticks/',
  test: 'ws://ac0ffeea.ngrok.io/ws/ticks/',
};

const ROOT_URL = apiType[process.env.REACT_APP_API];
const WESOCKET_ROOT = socketType[process.env.REACT_APP_API];

const url = {
  parameters: `${ROOT_URL}/bitmex/parameters`,
  thresholds: `${ROOT_URL}/bitmex/thresholds`,
  funding: `${ROOT_URL}/bitmex/funding`,
  chart: `${ROOT_URL}/`,
}

export { WESOCKET_ROOT };

export default url;

