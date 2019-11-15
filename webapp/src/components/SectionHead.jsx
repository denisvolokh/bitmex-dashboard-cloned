import React from 'react';
import { connect } from 'react-redux';

const SectionHead = ({ stat }) => {

  return (
    <div className="section">
      <ul className="section__list">
        <li className="section__item">
          <span className="section__value">Price</span>
          <span className="section__value">{stat.price} USD</span>
        </li>
        <li className="section__item">
          <div className="section__wrapper">
            <span className="section__value">Volume of last</span>
            <input
              type="number"
              value={stat.trades}
              readOnly
              className="section__input section__input--trades"
            />
            <span className="section__value">trades</span>
          </div>
          <span className="section__value">{stat.volume_of_last} USD</span>
        </li>
        <li className="section__item">
          <span className="section__value">Open Interest</span>
          <span className="section__value">{stat.open_inerest} USD</span>
        </li>
      </ul>
    </div>
  );
};

export default connect(({ statModule: { stat } }) => ({ stat }))(SectionHead);
