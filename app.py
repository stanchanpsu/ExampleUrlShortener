from flask import Flask, request, jsonify, redirect
import aiosqlite
import random
import string
import asyncio

app = Flask(__name__)


def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


async def create_table():
    async with aiosqlite.connect('url_shortener.db') as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            '''CREATE TABLE IF NOT EXISTS urls (short_code TEXT PRIMARY KEY, long_url TEXT)'''
        )
        await conn.commit()


async def shorten_url(long_url, vanity_url):
    async with aiosqlite.connect('url_shortener.db') as conn:
        cursor = await conn.cursor()

        short_code = vanity_url if vanity_url else generate_short_code()

        try:
            await cursor.execute(
                'INSERT INTO urls (short_code, long_url) VALUES (?, ?)', (short_code, long_url))
            await conn.commit()
        except aiosqlite.DatabaseError:
            return None

    return short_code


async def get_long_url(short_code):
    async with aiosqlite.connect('url_shortener.db') as conn:
        cursor = await conn.cursor()

        await cursor.execute('SELECT long_url FROM urls WHERE short_code=?', (short_code,))
        result = await cursor.fetchone()

        if result:
            long_url = result[0]
            return long_url


@app.route('/shorten', methods=['POST'])
async def shorten():
    data = request.get_json()
    long_url = data.get('url')
    vanity_url = data.get('short_code')

    if not long_url:
        return jsonify({'error': 'URL not provided'}), 400

    short_code = await shorten_url(long_url, vanity_url)

    if not short_code:
        if vanity_url:
            return jsonify({'error': 'Choose another short_code.'}), 409
        # short_key collisions are extremely rare so just give an error to the user.
        return jsonify({'error': 'Could not shorten URL.'}), 500

    return jsonify({'short_code': f'{short_code}'}), 201


@app.route('/<short_code>', methods=['GET'])
async def get_long_url_route(short_code):
    long_url = await get_long_url(short_code)

    if long_url:
        # Instead of returning the long_url, redirect the user to the long_url.
        return redirect(long_url, code=302)
    return jsonify({'error': 'Short code not found'}), 404

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_table())
    app.run(threaded=True)
