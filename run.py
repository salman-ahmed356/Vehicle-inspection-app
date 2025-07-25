from flask_wtf import CSRFProtect
from app import create_app
from app.auth import login_required
from app.license_check import check_license
import logging
import base64

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = create_app()
# configure logging
app.logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

# csrf
csrf = CSRFProtect(app)


@app.template_filter('skip_none')
def skip_none(value):
    return value if value is not None else ''

@app.template_filter('b64encode')
def b64encode(data):
    if data:
        return base64.b64encode(data).decode('utf-8')
    return ''


if __name__ == '__main__':
    check_license()  # Display license notice
    app.run(host="0.0.0.0", port="5000", debug=True)

