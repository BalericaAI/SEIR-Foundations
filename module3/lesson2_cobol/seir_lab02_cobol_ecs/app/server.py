"""Deliberately small lab HTTP-to-COBOL adapter (synthetic data only)."""
import json
import os
import subprocess
import threading
import uuid
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get('PORT', '8080'))
ENGINE = os.environ.get('COBOL_ENGINE', '/opt/app/financial')
TASK_ID = os.environ.get('HOSTNAME', 'local')
MAX_REQUEST_BYTES = 4096
CAPACITY = threading.BoundedSemaphore(value=8)


def amount(value, key, min_value=Decimal('0.01'), max_value=Decimal('100000000.00')):
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        raise ValueError(f'{key} must be a decimal number')
    try:
        dec = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f'{key} must be a decimal number') from None
    if not dec.is_finite() or dec < min_value or dec > max_value or dec != dec.quantize(Decimal('.01')):
        raise ValueError(f'{key} must be between {min_value} and {max_value} with at most 2 decimals')
    return f'{dec:.2f}'


def integer(value, key, low, high):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f'{key} must be an integer between {low} and {high}')
    return value


def run_financial(command):
    if not CAPACITY.acquire(blocking=False):
        raise RuntimeError('busy')
    try:
        result = subprocess.run([ENGINE], input=command + '\n', text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=3, check=False)
        line = result.stdout.strip()
        if result.returncode != 0 or not line.startswith('OK|'):
            raise RuntimeError('cobol_failure')
        return line.split('|')[1:]
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError('cobol_unavailable') from exc
    finally:
        CAPACITY.release()


class Handler(BaseHTTPRequestHandler):
    server_version = 'SEIR-COBOL-Lab02/1.0'

    def log_message(self, fmt, *args):
        # Avoid logging request bodies (even synthetic financial inputs).
        print(json.dumps({'event': 'http', 'remote': self.client_address[0],
                          'line': fmt % args}), flush=True)

    def respond(self, code, data):
        content = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path == '/health':
            return self.respond(200, {'status': 'alive'})
        if self.path == '/ready':
            try:
                good = run_financial('INTEREST|100.00|0.00|1')
                return self.respond(200 if good == ['0.00', '100.00'] else 503,
                                    {'status': 'ready' if good == ['0.00', '100.00'] else 'unready'})
            except RuntimeError:
                return self.respond(503, {'status': 'unready'})
        if self.path == '/v1/info':
            return self.respond(200, {'service': 'seir-cobol', 'version': 'lab02', 'task': TASK_ID})
        return self.respond(404, {'error': 'not_found'})

    def do_POST(self):
        paths = {'/v1/interest', '/v1/loan-payment', '/v1/transfer/validate'}
        if self.path not in paths:
            return self.respond(404, {'error': 'not_found'})
        try:
            n = int(self.headers.get('Content-Length', '0'))
            if n < 1 or n > MAX_REQUEST_BYTES:
                return self.respond(413, {'error': 'invalid_body_length'})
            data = json.loads(self.rfile.read(n))
            if not isinstance(data, dict):
                raise ValueError('JSON object required')
            if self.path == '/v1/interest':
                principal = amount(data['principal'], 'principal')
                rate = amount(data['annual_rate_percent'], 'annual_rate_percent', Decimal('0'), Decimal('100'))
                years = integer(data['years'], 'years', 1, 100)
                result = run_financial(f'INTEREST|{principal}|{rate}|{years}')
                return self.respond(200, {'interest': result[0], 'total': result[1], 'currency': 'USD', 'method': 'simple'})
            if self.path == '/v1/loan-payment':
                principal = amount(data['principal'], 'principal')
                rate = amount(data['annual_rate_percent'], 'annual_rate_percent', Decimal('0'), Decimal('100'))
                months = integer(data['months'], 'months', 1, 600)
                result = run_financial(f'LOAN|{principal}|{rate}|{months}')
                return self.respond(200, {'monthly_payment': result[0], 'currency': 'USD'})
            value = amount(data['amount'], 'amount')
            available = amount(data['available_balance'], 'available_balance', Decimal('0'))
            result = run_financial(f'TRANSFER|{value}|{available}|0')
            return self.respond(200, {'decision': result[0], 'posted': False})
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return self.respond(400, {'error': 'invalid_request', 'detail': str(exc)})
        except RuntimeError as exc:
            code = 503 if str(exc) == 'busy' else 502
            return self.respond(code, {'error': str(exc), 'request_id': str(uuid.uuid4())})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
