from daftar import app
import os

app.secret_key = os.urandom(24)
port = int(os.environ.get('PORT', 5050))
app.run(port=port, debug=True)