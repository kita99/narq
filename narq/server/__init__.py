import os
from datetime import date

from starlette.templating import Jinja2Templates

from narq import constants, version

templates = Jinja2Templates(
    directory=os.path.join(constants.STATIC_DIR, "narq", "server", "templates")
)
templates.env.globals["NARQ_VERSION"] = version.VERSION
templates.env.globals["NOW_YEAR"] = date.today().year
