import {
  WS_CONNECT,
  WS_CONNECTING,
  WS_CONNECTED,
  WS_DISCONNECT,
  WS_DISCONNECTED,
  CHART_UPDATE,
  CHART_REQUEST,
  CHART_SUCCESS,
  CHART_FAILURE,
  PARAMETERS_FAILURE,
  PARAMETERS_SUCCESS,
  PARAMETERS_UPDATE,
  PARAMETERS_REQUEST,
  THRESHOLDS_REQUEST,
  THRESHOLDS_SUCCESS,
  THRESHOLDS_UPDATE,
  THRESHOLDS_FAILURE,
  CUSTOM_LEVELS_REQUEST,
  CUSTOM_LEVELS_UPDATE,
  CUSTOM_LEVELS_SUCCESS,
  CUSTOM_LEVELS_FAILURE,
  STAT_UPDATE,
  STAT_REQUEST,
  STAT_SUCCESS,
  STAT_FAILURE,
  THRESHOLDS_UPDATE_ALERT,
} from '../constants';
import HttpService from '../services/httpService';
import { WESOCKET_ROOT } from '../api';

const httpService = new HttpService();

export const wsConnect = () => dispatch => dispatch([WS_CONNECT, WESOCKET_ROOT]);
export const wsConnecting = () => WS_CONNECTING;
export const wsConnected = () => WS_CONNECTED;
export const wsDisconnect = () => WS_DISCONNECT;
export const wsDisconnected = () => WS_DISCONNECTED;

export const fetchParameters = () => async dispatch => {
  dispatch(PARAMETERS_REQUEST);
  try {
    const payload = await httpService.fetchParameters();
    payload.forEach(({ key, value }) => {
      dispatch([STAT_UPDATE, { [key]: value }]);
    })
    dispatch([PARAMETERS_UPDATE, payload]);
    dispatch(PARAMETERS_SUCCESS);
  } catch (e) {
    dispatch(PARAMETERS_FAILURE);
  }
};

export const fetchFunding = () => async dispatch => {
  dispatch(STAT_REQUEST);
  try {
    const payload = await httpService.fetchFunding();
    dispatch([STAT_UPDATE, payload]);
    dispatch(STAT_SUCCESS);
  } catch (e) {
    dispatch(STAT_FAILURE);
  }
};

export const fetchThresholds = () => async dispatch => {
  dispatch(THRESHOLDS_REQUEST);
  try {
    const payload = await httpService.fetchThresholds();
    console.log(payload)
    payload.forEach(({ timeframe, threshold_value_percent: value, threshold_type }) => {
      switch (threshold_type) {
        case 'VOLUME_CHANGE':
            switch (timeframe) {
              case '1m':
                dispatch([THRESHOLDS_UPDATE_ALERT, { 'volume_1m': value }]);
                break;
              case '5m':
                dispatch([THRESHOLDS_UPDATE_ALERT, { 'volume_5m': value }]);
                break;
              case '1h':
                dispatch([THRESHOLDS_UPDATE_ALERT, { 'volume_1h': value }]);
                break;
              case '1d':
                dispatch([THRESHOLDS_UPDATE_ALERT, { 'volume_1d': value }]);
                break;
            default:
              break;
            }
          break;
        case 'RESISTANCE':
          dispatch([THRESHOLDS_UPDATE_ALERT, { 'resistance': value }]);
          break;
        case 'SUPPORT':
          dispatch([THRESHOLDS_UPDATE_ALERT, { 'support': value }]);
          break;
        default:
          break;
      }
    })
    dispatch([THRESHOLDS_UPDATE, payload]);
    dispatch(THRESHOLDS_SUCCESS);
  } catch (e) {
    console.log(e)
    dispatch(THRESHOLDS_FAILURE);
  }
};

export const fetchChart = () => async dispatch => {
  dispatch(CHART_REQUEST);
  try {
    const payload = await httpService.fetchChart();
    dispatch([CHART_UPDATE, payload]);
    dispatch(CHART_SUCCESS);
  } catch (e) {
    dispatch(CHART_FAILURE);
  }
};

export const customLevelAdd = (newLevel) => async (dispatch, getState) => {
  dispatch(CUSTOM_LEVELS_REQUEST);
  try {
    const payload = [...getState().customLevelsModule.levels, {...newLevel, id: Date.now()}];
    dispatch([CUSTOM_LEVELS_UPDATE, payload]);
    dispatch(CUSTOM_LEVELS_SUCCESS);
    return 1;
  } catch (e) {
    dispatch(CUSTOM_LEVELS_FAILURE)
    return 0;
  }
}

export const customLevelRemove = (removeId) => async (dispatch, getState) => {
  dispatch(CUSTOM_LEVELS_REQUEST);
  try {
    const payload = getState().customLevelsModule.levels.filter(({ id }) => id !== removeId);
    dispatch([CUSTOM_LEVELS_UPDATE, payload]);
    dispatch(CUSTOM_LEVELS_SUCCESS);
  } catch (e) {
    dispatch(CUSTOM_LEVELS_FAILURE)
  }
}

export const thresholdsUpdateAlert = (item, type) => async (dispatch, getState) => {
  let threshold;
  let threshold_value_percent = '';
  if (typeof item === 'object') {
    threshold_value_percent = item.value;
    dispatch([THRESHOLDS_UPDATE_ALERT, { [item.type]: threshold_value_percent }]);
    threshold = getState().thresholdsModule.thresholds.find(({ timeframe }) => timeframe === type);
  } else {
    threshold_value_percent = item;
    dispatch([THRESHOLDS_UPDATE_ALERT, { [type]: threshold_value_percent }]);
    threshold = getState().thresholdsModule.thresholds.find(({ threshold_type }) => threshold_type === type.toUpperCase());
  }
  
  if (threshold_value_percent && threshold) {
    const payload = {...threshold, threshold_value_percent};
    await httpService.thresholdsAlertsUpdate(payload);
    fetchThresholds()(dispatch);
  }
}

export const fetchData = () => (dispatch) => {
  fetchParameters()(dispatch);
  fetchFunding()(dispatch);
  fetchThresholds()(dispatch);
}

export const changeTrades = (trades) => async dispatch => {
  dispatch([STAT_UPDATE, { trades }]);
};
