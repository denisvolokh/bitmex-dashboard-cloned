import * as Logger from 'logplease';

const has = Object.prototype.hasOwnProperty;

const ENV_MODE = process.env.NODE_ENV === 'development';

const onLogger = (name, msg, type) => {
  if (!ENV_MODE) return;
  const newLogger = Logger.create(name);
  newLogger[type](msg);
};

const getErrorMessage = (error = 'Somthing Wrong') => {
  let msg = error;
  if (error instanceof Object) {
    switch (true) {
      case has.call(error, 'message'):
        msg = error.data;
        break;
      case has.call(error, 'msg'):
        msg = error.data;
        break;
      case has.call(error, 'data'):
        msg = error.data;
        break;
      case has.call(error, 'response'):
        msg = error.response.data;
        break;
      default:
        break;
    }
  }
  return msg;
};

export { getErrorMessage };

export default {
  debug: (msg = '', name = '') => {
    onLogger(name, msg, 'debug');
  },
  info: (msg = '', name = '') => {
    onLogger(name, msg, 'info');
  },
  error: (error = 'Something wrong!', name = '') => {
    onLogger(name, getErrorMessage(error), 'error');
  },
  warn: (msg = '', name = '') => {
    onLogger(name, msg, 'warn');
  },
  log: (msg = '', name = '') => {
    onLogger(name, msg, 'log');
  }
};
