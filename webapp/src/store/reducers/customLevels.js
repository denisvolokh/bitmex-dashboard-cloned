import {
  CUSTOM_LEVELS_REQUEST,
  CUSTOM_LEVELS_SUCCESS,
  CUSTOM_LEVELS_FAILURE,
  CUSTOM_LEVELS_UPDATE,
  CUSTOM_LEVELS_ADD,
  CUSTOM_LEVELS_REMOVE,
} from '../../constants';

const customLevelsReducer = (state, action) => {

  if (state === undefined) {
    return {
      loading: false,
      hasError: false,
      levels: [],
    };
  }

  switch (action.type) {
    case CUSTOM_LEVELS_REQUEST:
      return {
        ...state.customLevelsModule,
        loading: true,
        hasError: false
      };
    case CUSTOM_LEVELS_SUCCESS:
      return {
        ...state.customLevelsModule,
        loading: false,
        hasError: false
      };
    case CUSTOM_LEVELS_FAILURE:
      return {
        ...state.customLevelsModule,
        loading: false,
        hasError: true
      };
    case CUSTOM_LEVELS_UPDATE:
      return {
        ...state.customLevelsModule,
        levels: [...action.payload],
      };
    case CUSTOM_LEVELS_ADD:
      return {
        ...state.customLevelsModule,
        levels: [...action.payload],
      };
    case CUSTOM_LEVELS_REMOVE:
      return {
        ...state.customLevelsModule,
        levels: [...action.payload],
      };
    default:
      return state.customLevelsModule;
  }
};

export default customLevelsReducer;
