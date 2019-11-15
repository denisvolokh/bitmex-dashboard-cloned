export default () => (next) => (action) => {

  if (typeof action === 'string') {
    return next({
      type: action,
    });
  }
  if (Array.isArray(action)) {
    const [ type, payload ] = action;
    return next({
      type,
      payload,
    });
  }

  return next(action);
};
