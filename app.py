from flask import Flask, request, jsonify

app = Flask(__name__)

# ---- Heiken Ashi Calculation ----
def heiken_ashi(candles):
    ha_candles = []
    for i, c in enumerate(candles):
        ha_close = (c['open'] + c['high'] + c['low'] + c['close']) / 4
        ha_open = (c['open'] + c['close']) / 2 if i == 0 else (ha_candles[i-1]['open'] + ha_candles[i-1]['close']) / 2
        ha_high = max(c['high'], ha_open, ha_close)
        ha_low = min(c['low'], ha_open, ha_close)
        ha_candles.append({
            'open': ha_open,
            'close': ha_close,
            'high': ha_high,
            'low': ha_low
        })
    return ha_candles

# ---- Strategy Logic ----
def run_strategy(ha_candles):
    signals = []
    position = None
    for c in ha_candles:
        if position is None:
            if c['close'] > c['open']:
                position = 'call'
                signals.append("BUY CALL")
            elif c['close'] < c['open']:
                position = 'put'
                signals.append("BUY PUT")
        elif position == 'call' and c['close'] < c['open']:
            signals.append("SELL CALL")
            position = None
        elif position == 'put' and c['close'] > c['open']:
            signals.append("SELL PUT")
            position = None
    return signals

# ---- Webhook Endpoint ----
@app.route('/', methods=['POST'])
def webhook():
    try:
        data = request.json
        candles = data.get('candles', [])
        if not candles:
            return jsonify({'error': 'No candle data provided'}), 400

        ha_candles = heiken_ashi(candles)
        signals = run_strategy(ha_candles)
        return jsonify({'signals': signals})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---- Health Check Endpoint ----
@app.route('/ping', methods=['GET'])
def ping():
    return 'Heiken Ashi strategy service is running.'

# ---- Local Run (optional) ----
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

