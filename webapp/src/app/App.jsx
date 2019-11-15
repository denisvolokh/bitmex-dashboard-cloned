import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { fetchData, wsConnect } from '../store/actions';
import SectionHead from '../components/SectionHead';
import SectionFunding from '../components/SectionFunding';
import SectionVolume from '../components/SectionVolume';
import LevelsHead from '../components/LevelsHead';
import LevelsResistance from '../components/LevelsResistance';
import LevelsSupport from '../components/LevelsSupport';
import LevelsCustom from '../components/LevelsCustom';
import Chart from '../components/Chart';

const App = ({ fetchData, wsConnect }) => {

  useEffect(() => {
    // wsConnect();
    fetchData();
  }, [wsConnect, fetchData])

  return (
    <div className="app">
      <div className="app__container">
        <h2 className="app__title">BitMEX XBUSD Dashboard</h2>
        <section className="app__section">
          <SectionHead />
          <SectionFunding />
          <SectionVolume />
        </section>
        <h2 className="app__title">S/R Levels</h2>
        <div className="app__section">
          <LevelsHead />
          <LevelsResistance />
          <LevelsSupport />
          <LevelsCustom />
        </div>
        <div className="app__section">
          <Chart />
        </div>
      </div>
    </div>
  );
}

export default connect(
  null,
  { wsConnect, fetchData }
)(App);
