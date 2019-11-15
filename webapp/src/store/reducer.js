import { chartReducer, parametersReducer, thresholdsReducer, customLevelsReducer, statReducer } from './reducers';

const reducer = (state, action) => {
  return {
    parametersModule: parametersReducer(state, action),
    customLevelsModule: customLevelsReducer(state, action),
    thresholdsModule: thresholdsReducer(state, action),
    chartModule: chartReducer(state, action),
    statModule: statReducer(state, action),
  };
};

export default reducer;
