import React from 'react';
import { connect } from 'react-redux';
import { thresholdsUpdateAlert } from '../store/actions';

const LevelsSupport = ({ thresholds, thresholdsUpdateAlert }) => {
  const handleChange = e => {
    const { value } = e.target;
    thresholdsUpdateAlert(value, 'support');
  };

  return (
    <div className="levels">
      <div className="levels__head">
        <h3 className="levels__title">Support</h3>
        <input
          onChange={handleChange}
          value={thresholds.support}
          type="number"
          placeholder="alert threshold in %"
          className="levels__input"
        />
      </div>
      <div className="levels__inner">
        <div className="levels__col">
          <span className="levels__value">{'8700'}</span>
          <span className="levels__value">{'-4.34'}%</span>
        </div>
        <div className="levels__col">
          <span className="levels__value">{'8700'}</span>
          <span className="levels__value">{'-4.34'}%</span>
        </div>
        <div className="levels__col">
          <span className="levels__value">{'8700'}</span>
          <span className="levels__value">{'-4.34'}%</span>
        </div>
      </div>
    </div>
  );
};

export default connect(
  ({ thresholdsModule: thresholds }) => ({ thresholds }),
  { thresholdsUpdateAlert }
)(LevelsSupport);
