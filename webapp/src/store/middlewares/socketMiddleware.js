import { WS_CONNECT, WS_DISCONNECTED, WS_DISCONNECT, WS_ERROR, WS_CONNECTED, STAT_UPDATE } from '../../constants';
import logger from '../../services/logger';
import io from 'socket.io-client';


const socketMiddleware = () => {
  let socket = null;

  const onOpen = store => (event) => {
    logger.info(event, 'WEBSOCKET OPEN');
    store.dispatch(WS_CONNECTED);
  };

  const onClose = store => () => {
    logger.info('', 'WEBSOCKET DISCONECTED');
    store.dispatch(WS_DISCONNECTED);
  };

  const onError = store => () => {
    logger.error('', 'WEBSOCKET ERROR');
    store.dispatch(WS_ERROR);
  };

  const onMessage = store => (e) => {
    const payload = JSON.parse(e.data);
    logger.info(payload, 'WEBSOCKET MESSAGE');
    switch (payload.type) {
      case 'trade':
        store.dispatch([STAT_UPDATE, { 'price': payload['price']  }]);
        break;
      case 'trade_volume_XBTUSD':
        store.dispatch([STAT_UPDATE, { 'volume_of_last': payload['trade_volume']  }]);
        break;
      case 'volume1m':
       store.dispatch([STAT_UPDATE, { 'volume_change_1m': payload['volume1m']  }]);
        break;
      case 'volume5m':
        store.dispatch([STAT_UPDATE, { 'volume_change_5m': payload['volume5m']  }]);
        break;
      case 'volume1h':
        store.dispatch([STAT_UPDATE, { 'volume_change_1h': payload['volume5h']  }]);
        break;
      case 'volume1d':
        store.dispatch([STAT_UPDATE, { 'volume_change_1d': payload['volume5d']  }]);
        break;
      case 'instrument':
        store.dispatch([STAT_UPDATE, { 'open_inerest': payload['open_interest']  }]);
        break;
      default:
        break;
    }
  }

  return (store) => (next) => (action) => {
    switch (action.type) {

      case WS_CONNECT:
        if (socket !== null) {
          socket.close();
        }
        socket = io(action.payload);
        socket.onclose = onClose(store);
        socket.onopen = onOpen(store);
        socket.onerror = onError(store);
        socket.onemessage = onMessage(store);
        socket.send(JSON.stringify({
          subscribe: "XBTUSD"
        }));
        socket.send(JSON.stringify({
            subscribe: "trade_volume_XBTUSD"
        }));
        socket.send(JSON.stringify({
            subscribe: "volume1m_XBTUSD"
        }));
        socket.send(JSON.stringify({
            subscribe: "volume5m_XBTUSD"
        }));
        socket.send(JSON.stringify({
          subscribe: "volume1h_XBTUSD"
        }));
        socket.send(JSON.stringify({
          subscribe: "volume1d_XBTUSD"
        }));
        socket.send(JSON.stringify({
            subscribe: "instrument_XBTUSD"
        }))
        break;

      case WS_DISCONNECT:
        if (socket !== null) {
          socket.close();
        }
        socket = null;
        logger.info('', 'WEBSOCKET CLOSED');
        break;

      case WS_ERROR:
        logger.error('', 'WEBSOCKET ERROR');
        if (socket !== null) {
          socket.close();
          socket.open();
        }
        break;

      default:
        return next(action);
    }
  };
};

export default socketMiddleware();
