import React from 'react';
import { connect } from 'react-redux';
import { thresholdsUpdateAlert } from '../store/actions';

const SectionVolume = ({ stat, thresholds, thresholdsUpdateAlert }) => {
  const handleChange = (type, period) => e => {
    const { value } = e.target;
    thresholdsUpdateAlert({ type, value }, period);
  };

  return (
    <div className="section">
      <ul className="section__list">
        <li className="section__item">
          <div className="section__wrapper">
            <span className="section__value section__value--col">
              1m USD Volume Change
            </span>
            <input
              type="text"
              value={thresholds.volume_1m}
              onChange={handleChange('volume_1m', '1m')}
              placeholder="alert threshold in %"
              className="section__input section__input--level"
            />
          </div>
          <span className="section__value">{stat.volume_change_1m}</span>
        </li>
        <li className="section__item">
          <div className="section__wrapper">
            <span className="section__value section__value--col">
              5m USD Volume Change
            </span>
            <input
              type="text"
              value={thresholds.volume_5m}
              onChange={handleChange('volume_5m', '5m')}
              placeholder="alert threshold in %"
              className="section__input section__input--level"
            />
          </div>
          <span className="section__value">{stat.volume_change_5m}</span>
        </li>
        <li className="section__item">
          <div className="section__wrapper">
            <span className="section__value section__value--col">
              1h USD Volume Change
            </span>
            <input
              type="text"
              value={thresholds.volume_1h}
              onChange={handleChange('volume_1h', '1h')}
              placeholder="alert threshold in %"
              className="section__input section__input--level"
            />
          </div>
          <span className="section__value">{stat.volume_change_1h}</span>
        </li>
        <li className="section__item">
          <div className="section__wrapper">
            <span className="section__value section__value--col">
              1d USD Volume Change
            </span>
            <input
              type="text"
              value={thresholds.volume_1d}
              onChange={handleChange('volume_1d', '1d')}
              placeholder="alert threshold in %"
              className="section__input section__input--level"
            />
          </div>
          <span className="section__value">{stat.volume_change_1d}</span>
        </li>
      </ul>
    </div>
  );
};

export default connect(
  ({ thresholdsModule: thresholds, statModule: { stat } }) => ({ thresholds, stat }),
  { thresholdsUpdateAlert }
)(SectionVolume);
