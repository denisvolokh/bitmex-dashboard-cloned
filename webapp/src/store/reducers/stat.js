import models from '../../models';
import {
  STAT_REQUEST,
  STAT_SUCCESS,
  STAT_FAILURE,
  STAT_UPDATE
} from '../../constants';

const statReducer = (state, action) => {

  if (state === undefined) {
    return {
      loading: false,
      hasError: false,
      stat: {...models.stat}
    };
  }

  switch (action.type) {
    case STAT_REQUEST:
      return {
        ...state.statModule,
        loading: true,
        hasError: false
      };
    case STAT_SUCCESS:
      return {
        ...state.statModule,
        loading: false,
        hasError: false
      };
    case STAT_FAILURE:
      return {
        ...state.statModule,
        loading: false,
        hasError: true
      };
    case STAT_UPDATE:
      return {
        ...state.statModule,
        stat: { ...state.statModule.stat, ...action.payload },
      };
    default:
      return state.statModule;
  }
};

export default statReducer;
