import React from "react";
import { connect } from 'react-redux';

const SectionFunding = ({ stat }) => {
  return (
    <div className="section">
      <ul className="section__list">
        <li className="section__item">
          <span className="section__value">Current Funding Rate</span>
          <span className="section__value">{stat.current_funding_rate}</span>
        </li>
        <li className="section__item">
          <span className="section__value">Predicted Funding Rate</span>
          <span className="section__value">{stat.predicted_funding_rate}</span>
        </li>
        <li className="section__item">
          <span className="section__value">Next Funding Rate Change at</span>
          <span className="section__value">{stat.next_funding_rate_change}</span>
        </li>
      </ul>
    </div>
  );
};

export default connect(({ statModule: { stat } }) => ({ stat }))(SectionFunding);
