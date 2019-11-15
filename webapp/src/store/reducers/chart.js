import {
  CHART_REQUEST,
  CHART_SUCCESS,
  CHART_FAILURE,
  CHART_UPDATE
} from '../../constants';

const chartReducer = (state, action) => {

  if (state === undefined) {
    return {
      loading: false,
      hasError: false,
      chart: []
    };
  }

  switch (action.type) {
    case CHART_REQUEST:
      return {
        ...state.chartModule,
        loading: true,
        hasError: false
      };
    case CHART_SUCCESS:
      return {
        ...state.chartModule,
        loading: false,
        hasError: false
      };
    case CHART_FAILURE:
      return {
        ...state.chartModule,
        loading: false,
        hasError: true
      };
    case CHART_UPDATE:
      return {
        ...state.chartModule,
        chart: [...action.payload],
      };
    default:
      return state.chart;
  }
};

export default chartReducer;
